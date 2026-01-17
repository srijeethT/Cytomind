import os
import uuid
import asyncio
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import aiofiles

from config import UPLOAD_DIR, REPORTS_DIR, HOST, PORT
from model_loader import get_classifier
from database import update_job_status, create_report, get_report, get_job, get_patient
from report_generator import generate_pdf_report

# Initialize FastAPI app
app = FastAPI(
    title="Cytomind ML Backend",
    description="Bone Marrow Cell Classification API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize classifier on startup
@app.on_event("startup")
async def startup_event():
    """Load the ML model on startup"""
    print("Initializing ML model...")
    get_classifier()
    print("ML model ready!")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Cytomind ML Backend"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    classifier = get_classifier()
    return {
        "status": "healthy",
        "model_loaded": classifier is not None,
        "device": str(classifier.device) if classifier else "N/A",
        "num_classes": classifier.num_classes if classifier else 0
    }


async def process_image_task(
    job_id: str,
    image_paths: List[str],
    patient_id: str,
    patient_name: str,
    patient_age: int,
    lab_id: str
):
    """Background task to process multiple images and generate comprehensive report"""
    try:
        total_images = len(image_paths)
        
        # Update status: Processing started
        update_job_status(job_id, "PROCESSING", 5)
        await asyncio.sleep(0.3)
        
        classifier = get_classifier()
        all_results = []
        
        # Process each image
        for idx, image_path in enumerate(image_paths):
            progress = 10 + int((idx / total_images) * 60)
            update_job_status(job_id, "PROCESSING", progress)
            
            result = classifier.predict(image_path)
            result['image_index'] = idx + 1
            result['image_filename'] = os.path.basename(image_path)
            all_results.append(result)
            
            await asyncio.sleep(0.1)
        
        # Aggregate results from all images
        update_job_status(job_id, "PROCESSING", 75)
        aggregated = aggregate_results(all_results)
        
        # Update status: Generating report
        update_job_status(job_id, "PROCESSING", 85)
        await asyncio.sleep(0.2)
        
        # Generate PDF report
        patient_data = {
            "patientId": patient_id,
            "name": patient_name,
            "age": patient_age
        }
        
        pdf_path = generate_pdf_report(
            job_id=job_id,
            patient_data=patient_data,
            classification_result=aggregated,
            image_paths=image_paths,
            individual_results=all_results
        )
        
        # Update status: Report generation complete
        update_job_status(job_id, "PROCESSING", 95)
        await asyncio.sleep(0.2)
        
        # Create report in database
        report = create_report(
            job_id=job_id,
            patient_id=patient_id,
            lab_id=lab_id,
            classification_result=aggregated,
            pdf_path=pdf_path,
            individual_results=all_results
        )
        
        # Final status: Completed
        result_data = {
            "classification": aggregated["classification"],
            "primaryClass": aggregated["primary_class"],
            "primaryClassFullName": aggregated["primary_class_full_name"],
            "malignancyPercentage": aggregated["malignancy_percentage"],
            "confidence": aggregated["confidence"],
            "topPredictions": aggregated["top_predictions"],
            "totalCellsAnalyzed": total_images,
            "cellDistribution": aggregated["cell_distribution"],
            "individualResults": all_results
        }
        
        update_job_status(job_id, "COMPLETED", 100, result_data)
        
        print(f"Job {job_id} completed successfully! ({total_images} images processed)")
        
    except Exception as e:
        print(f"Error processing job {job_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        update_job_status(job_id, "FAILED", 0, {"error": str(e)})


def aggregate_results(all_results: List[dict]) -> dict:
    """Aggregate classification results from multiple images"""
    if not all_results:
        return {}
    
    # If only one result, return it directly
    if len(all_results) == 1:
        result = all_results[0].copy()
        result['cell_distribution'] = {result['primary_class']: 1}
        result['total_cells'] = 1
        return result
    
    # Count cell types
    cell_counts = {}
    malignant_count = 0
    
    # Define malignant cell types
    malignant_classes = ['BLA', 'MYB', 'PMO', 'FGC', 'ABE', 'EBO', 'PLM']
    
    # Cell type full names
    cell_names = {
        'ABE': 'Abnormal Eosinophil',
        'ART': 'Artefact',
        'BAS': 'Basophil',
        'BLA': 'Blast Cell',
        'EBO': 'Erythroblast',
        'EOS': 'Eosinophil',
        'FGC': 'Faggot Cell',
        'HAC': 'Hairy Cell',
        'KSC': 'Kidney Shaped Cell',
        'LYI': 'Lymphocyte Immature',
        'LYT': 'Lymphocyte',
        'MMZ': 'Metamyelocyte',
        'MON': 'Monocyte',
        'MYB': 'Myeloblast',
        'NGB': 'Band Neutrophil',
        'NGS': 'Segmented Neutrophil',
        'NIF': 'Neutrophil Immature',
        'OTH': 'Other',
        'PEB': 'Proerythroblast',
        'PLM': 'Plasma Cell',
        'PMO': 'Promyelocyte'
    }
    
    for result in all_results:
        cell_type = result.get('primary_class', 'OTH')
        cell_counts[cell_type] = cell_counts.get(cell_type, 0) + 1
        
        if cell_type in malignant_classes:
            malignant_count += 1
    
    total_cells = len(all_results)
    
    # Find most common cell type
    primary_class = max(cell_counts, key=cell_counts.get)
    primary_count = cell_counts[primary_class]
    
    # Calculate malignancy percentage
    malignancy_percentage = round((malignant_count / total_cells) * 100, 1)
    
    # Determine overall classification
    if malignancy_percentage >= 20:
        classification = "MALIGNANT"
    elif malignancy_percentage >= 5:
        classification = "SUSPICIOUS"
    else:
        classification = "BENIGN"
    
    # Calculate average confidence across all results
    avg_confidence = sum(r.get('confidence', 0) for r in all_results) / total_cells
    
    # Create cell distribution with percentages
    cell_distribution = {}
    for cell_type, count in sorted(cell_counts.items(), key=lambda x: x[1], reverse=True):
        cell_distribution[cell_type] = {
            'count': count,
            'percentage': round((count / total_cells) * 100, 1),
            'full_name': cell_names.get(cell_type, cell_type)
        }
    
    # Create top predictions based on cell distribution
    top_predictions = []
    for cell_type, data in list(cell_distribution.items())[:5]:
        top_predictions.append({
            'class': cell_type,
            'full_name': data['full_name'],
            'probability': data['percentage'],
            'count': data['count']
        })
    
    return {
        "classification": classification,
        "primary_class": primary_class,
        "primary_class_full_name": cell_names.get(primary_class, primary_class),
        "malignancy_percentage": malignancy_percentage,
        "malignant_cell_count": malignant_count,
        "confidence": round(avg_confidence, 1),
        "top_predictions": top_predictions,
        "cell_distribution": cell_distribution,
        "total_cells": total_cells
    }


@app.post("/api/analyze")
async def analyze_image(
    background_tasks: BackgroundTasks,
    images: List[UploadFile] = File(...),
    job_id: str = Form(...),
    patient_id: str = Form(...),
    patient_name: str = Form(...),
    patient_age: int = Form(...),
    lab_id: Optional[str] = Form(None)
):
    """
    Analyze bone marrow cell images (supports multiple images)
    
    This endpoint accepts one or more images and patient data, saves the images,
    and starts a background task to process them with the ML model.
    """
    # Validate file types
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/tiff"]
    
    image_paths = []
    
    for idx, image in enumerate(images):
        if image.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type for {image.filename}. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Save uploaded image
        file_extension = os.path.splitext(image.filename)[1] or ".jpg"
        saved_filename = f"{job_id}_{idx}{file_extension}"
        image_path = os.path.join(UPLOAD_DIR, saved_filename)
        
        async with aiofiles.open(image_path, 'wb') as f:
            content = await image.read()
            await f.write(content)
        
        image_paths.append(image_path)
    
    # Start background processing
    background_tasks.add_task(
        process_image_task,
        job_id,
        image_paths,
        patient_id,
        patient_name,
        patient_age,
        lab_id
    )
    
    return {
        "success": True,
        "jobId": job_id,
        "totalImages": len(image_paths),
        "message": f"{len(image_paths)} image(s) uploaded successfully. Processing started."
    }


@app.get("/api/jobs/{job_id}/status")
async def get_job_status(job_id: str):
    """Get the status of a processing job"""
    job = get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    response = {
        "jobId": job["jobId"],
        "status": job["status"],
        "progress": job.get("progress", 0)
    }
    
    # Include result if completed
    if job["status"] == "COMPLETED" and job.get("result"):
        response["report"] = job["result"]
        
        # Get full report from database
        report = get_report(job_id)
        if report:
            response["report"]["patientId"] = report.get("patientId")
            response["report"]["date"] = report.get("createdAt")
    
    if job["status"] == "FAILED" and job.get("result"):
        response["message"] = job["result"].get("error", "Processing failed")
    
    return response


@app.get("/api/reports/{job_id}")
async def get_report_details(job_id: str):
    """Get the full report for a job"""
    report = get_report(job_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {
        "success": True,
        "report": report
    }


@app.get("/api/reports/{job_id}/pdf")
async def download_report_pdf(job_id: str):
    """Download the PDF report for a job"""
    pdf_path = os.path.join(REPORTS_DIR, f"report_{job_id}.pdf")
    
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Report PDF not found")
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"cytomind_report_{job_id}.pdf"
    )


@app.post("/api/predict")
async def predict_single(image: UploadFile = File(...)):
    """
    Quick prediction endpoint for a single image
    Returns classification result without storing in database
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/tiff"]
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Save temporary file
    temp_id = str(uuid.uuid4())
    file_extension = os.path.splitext(image.filename)[1] or ".jpg"
    temp_path = os.path.join(UPLOAD_DIR, f"temp_{temp_id}{file_extension}")
    
    try:
        async with aiofiles.open(temp_path, 'wb') as f:
            content = await image.read()
            await f.write(content)
        
        # Run prediction
        classifier = get_classifier()
        result = classifier.predict(temp_path)
        
        return {
            "success": True,
            "prediction": result
        }
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
