import os
from dotenv import load_dotenv

load_dotenv()

# Model paths
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ensemble_final.pth")
METADATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model_metadata.json")

# MongoDB
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/cytomind")

# Upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")

# Create directories if they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# Server config
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))

# Cell type full names for reports
CELL_TYPE_NAMES = {
    "ABE": "Abnormal Eosinophil",
    "ART": "Artefact",
    "BAS": "Basophil",
    "BLA": "Blast",
    "EBO": "Erythroblast",
    "EOS": "Eosinophil",
    "FGC": "Faggot Cell",
    "HAC": "Hairy Cell",
    "KSC": "Kidney Shaped Cell",
    "LYI": "Lymphocyte Immature",
    "LYT": "Lymphocyte",
    "MMZ": "Metamyelocyte",
    "MON": "Monocyte",
    "MYB": "Myeloblast",
    "NGB": "Band Neutrophil",
    "NGS": "Segmented Neutrophil",
    "NIF": "Neutrophil Immature Forms",
    "OTH": "Other",
    "PEB": "Proerythroblast",
    "PLM": "Plasma Cell",
    "PMO": "Promyelocyte"
}

# Malignant cell types (Blast and other abnormal cells)
MALIGNANT_CLASSES = {"BLA", "MYB", "PLM", "PMO", "ABE", "FGC", "HAC", "LYI"}
