from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
from config import MONGODB_URI

# MongoDB client
client = None
db = None

def get_database():
    """Get or create database connection"""
    global client, db
    if client is None:
        client = MongoClient(MONGODB_URI)
        db = client.get_database()
    return db

def update_job_status(job_id: str, status: str, progress: int, result: dict = None):
    """Update job status in database"""
    database = get_database()
    update_data = {
        "status": status,
        "progress": progress,
        "updatedAt": datetime.utcnow()
    }
    if result:
        update_data["result"] = result
        
    database.jobs.update_one(
        {"jobId": job_id},
        {"$set": update_data}
    )

def create_report(job_id: str, patient_id: str, lab_id: str, classification_result: dict, pdf_path: str, individual_results: list = None):
    """Create a new report in database"""
    database = get_database()
    report = {
        "jobId": job_id,
        "patientId": patient_id,
        "labId": ObjectId(lab_id) if lab_id else None,
        "classification": classification_result["classification"],
        "primaryClass": classification_result["primary_class"],
        "primaryClassFullName": classification_result.get("primary_class_full_name", classification_result["primary_class"]),
        "malignancyPercentage": classification_result["malignancy_percentage"],
        "malignantCellCount": classification_result.get("malignant_cell_count", 0),
        "totalCellsAnalyzed": classification_result.get("total_cells", 1),
        "confidence": classification_result["confidence"],
        "topPredictions": classification_result["top_predictions"],
        "cellDistribution": classification_result.get("cell_distribution", {}),
        "allProbabilities": classification_result.get("all_probabilities", {}),
        "individualResults": individual_results or [],
        "pdfUrl": pdf_path,
        "createdAt": datetime.utcnow()
    }
    database.reports.insert_one(report)
    return report

def get_report(job_id: str):
    """Get report by job ID"""
    database = get_database()
    report = database.reports.find_one({"jobId": job_id})
    if report:
        report["_id"] = str(report["_id"])
        if report.get("labId"):
            report["labId"] = str(report["labId"])
    return report

def get_job(job_id: str):
    """Get job by job ID"""
    database = get_database()
    job = database.jobs.find_one({"jobId": job_id})
    if job:
        job["_id"] = str(job["_id"])
        if job.get("labId"):
            job["labId"] = str(job["labId"])
    return job

def get_patient(patient_id: str):
    """Get patient by patient ID"""
    database = get_database()
    patient = database.patients.find_one({"patientId": patient_id})
    if patient:
        patient["_id"] = str(patient["_id"])
    return patient
