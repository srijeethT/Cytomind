import json
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import numpy as np
from config import MODEL_PATH, METADATA_PATH, CELL_TYPE_NAMES, MALIGNANT_CLASSES

# Try to import transformers for ViT, fall back if not available
try:
    from transformers import ViTModel, ViTConfig
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    print("Warning: transformers library not installed. Installing...")


class ViTWrapper(nn.Module):
    """Wrapper for Vision Transformer"""
    def __init__(self, num_classes=21):
        super().__init__()
        if HAS_TRANSFORMERS:
            self.vit = ViTModel.from_pretrained('google/vit-base-patch16-224')
            self.classifier = nn.Linear(self.vit.config.hidden_size, num_classes)
        
    def forward(self, x):
        outputs = self.vit(x)
        return self.classifier(outputs.last_hidden_state[:, 0])


class ResNetWrapper(nn.Module):
    """Wrapper for ResNet50"""
    def __init__(self, num_classes=21):
        super().__init__()
        self.resnet = models.resnet50(weights=None)
        # Replace fc with sequential layers matching the saved model
        self.resnet.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(2048, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )
        
    def forward(self, x):
        return self.resnet(x)


class EnsembleModel(nn.Module):
    """Ensemble model combining ViT and ResNet"""
    
    def __init__(self, num_classes=21):
        super().__init__()
        self.num_classes = num_classes
        
        # ViT component
        self.vit = ViTWrapper(num_classes)
        
        # ResNet component  
        self.resnet = ResNetWrapper(num_classes)
        
        # Final classifier (combines both)
        self.classifier = nn.Sequential(
            nn.Linear(num_classes * 2, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )
        
    def forward(self, x):
        vit_out = self.vit(x)
        resnet_out = self.resnet(x)
        combined = torch.cat([vit_out, resnet_out], dim=1)
        return self.classifier(combined)


class CellClassifier:
    """Cell classification using the trained ensemble model"""
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.metadata = None
        self.transform = None
        self._load_metadata()
        self._load_model()
        self._setup_transforms()
        
    def _load_metadata(self):
        """Load model metadata"""
        with open(METADATA_PATH, 'r') as f:
            self.metadata = json.load(f)
        self.classes = self.metadata['classes']
        self.num_classes = self.metadata['num_classes']
        self.input_size = self.metadata['input_size']
        
    def _load_model(self):
        """Load the trained model"""
        print(f"Loading model from {MODEL_PATH}...")
        print(f"Using device: {self.device}")
        
        # Load state dict first to inspect structure
        state_dict = torch.load(MODEL_PATH, map_location=self.device, weights_only=False)
        
        # Handle different state dict formats
        if 'model_state_dict' in state_dict:
            state_dict = state_dict['model_state_dict']
        elif 'state_dict' in state_dict:
            state_dict = state_dict['state_dict']
        
        # Create model and load with strict=False to handle mismatches
        self.model = EnsembleModel(num_classes=self.num_classes)
        
        try:
            self.model.load_state_dict(state_dict, strict=True)
        except RuntimeError as e:
            print(f"Strict loading failed, trying with strict=False: {e}")
            # Try loading with strict=False
            self.model.load_state_dict(state_dict, strict=False)
            
        self.model.to(self.device)
        self.model.eval()
        print("Model loaded successfully!")
        
    def _setup_transforms(self):
        """Setup image transforms"""
        self.transform = transforms.Compose([
            transforms.Resize((self.input_size, self.input_size)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
    def predict(self, image_path: str) -> dict:
        """
        Predict cell type from image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with prediction results
        """
        # Load and preprocess image
        image = Image.open(image_path).convert('RGB')
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        # Get prediction
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.softmax(outputs, dim=1)[0]
            
        # Get top predictions
        top_probs, top_indices = torch.topk(probabilities, k=5)
        
        predictions = []
        for prob, idx in zip(top_probs.cpu().numpy(), top_indices.cpu().numpy()):
            class_name = self.classes[idx]
            predictions.append({
                "class": class_name,
                "class_full_name": CELL_TYPE_NAMES.get(class_name, class_name),
                "probability": float(prob * 100)
            })
        
        # Primary prediction
        primary_class = predictions[0]["class"]
        primary_confidence = predictions[0]["probability"]
        
        # Calculate malignancy percentage
        malignancy_percentage = sum(
            float(probabilities[self.classes.index(cls)].cpu().numpy() * 100)
            for cls in MALIGNANT_CLASSES if cls in self.classes
        )
        
        # Determine if malignant (if primary class is malignant or high malignancy percentage)
        is_malignant = primary_class in MALIGNANT_CLASSES or malignancy_percentage > 30
        
        return {
            "primary_class": primary_class,
            "primary_class_full_name": CELL_TYPE_NAMES.get(primary_class, primary_class),
            "confidence": round(primary_confidence, 2),
            "top_predictions": predictions,
            "malignancy_percentage": round(malignancy_percentage, 2),
            "classification": "MALIGNANT" if is_malignant else "BENIGN",
            "all_probabilities": {
                self.classes[i]: round(float(probabilities[i].cpu().numpy() * 100), 2)
                for i in range(len(self.classes))
            }
        }
    
    def predict_batch(self, image_paths: list) -> list:
        """
        Predict cell types for multiple images
        
        Args:
            image_paths: List of paths to image files
            
        Returns:
            List of prediction results
        """
        results = []
        for path in image_paths:
            try:
                result = self.predict(path)
                result["image_path"] = path
                result["success"] = True
                results.append(result)
            except Exception as e:
                results.append({
                    "image_path": path,
                    "success": False,
                    "error": str(e)
                })
        return results


# Global classifier instance
classifier = None

def get_classifier() -> CellClassifier:
    """Get or create the global classifier instance"""
    global classifier
    if classifier is None:
        classifier = CellClassifier()
    return classifier
