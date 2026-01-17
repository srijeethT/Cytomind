# 🔬 Cytomind - AI-Powered Bone Marrow Cell Classification

Cytomind is an intelligent medical diagnostic system that uses deep learning to analyze bone marrow cell images and classify them into 21 different cell types. The system helps identify potential malignancies and generates comprehensive medical reports.

---

## 📋 Table of Contents

- [System Overview](#system-overview)
- [Architecture](#architecture)
- [How Frontend & Backend Connect](#how-frontend--backend-connect)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Cell Types](#cell-types)

---

## 🏗️ System Overview

Cytomind consists of **two main components**:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CYTOMIND SYSTEM                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────────────┐         ┌─────────────────────────────┐   │
│   │   FRONTEND          │         │   ML BACKEND                │   │
│   │   (Next.js)         │ ──────► │   (Python FastAPI)          │   │
│   │   Port: 3000        │ ◄────── │   Port: 8000                │   │
│   └─────────────────────┘         └─────────────────────────────┘   │
│            │                                   │                     │
│            │                                   │                     │
│            ▼                                   ▼                     │
│   ┌─────────────────────┐         ┌─────────────────────────────┐   │
│   │   MongoDB           │         │   PyTorch Model             │   │
│   │   (User Data, Jobs) │         │   (ViT + ResNet Ensemble)   │   │
│   └─────────────────────┘         └─────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

| Component | Technology | Port | Purpose |
|-----------|------------|------|---------|
| **Frontend** | Next.js + React | 3000 | User interface, authentication, dashboard |
| **ML Backend** | FastAPI + Python | 8000 | AI model inference, image processing, PDF reports |
| **Database** | MongoDB | 27017 | Store users, jobs, patients, reports |

---

## 🔄 How Frontend & Backend Connect

### The Flow (Step by Step)

```
┌──────────────┐     ┌──────────────────┐     ┌────────────────────┐
│   Browser    │     │  Next.js Server  │     │  Python ML Backend │
│   (User)     │     │  (Port 3000)     │     │  (Port 8000)       │
└──────┬───────┘     └────────┬─────────┘     └─────────┬──────────┘
       │                      │                         │
       │  1. Upload Images    │                         │
       │ ────────────────────>│                         │
       │                      │                         │
       │                      │  2. Forward to ML API   │
       │                      │ ───────────────────────>│
       │                      │                         │
       │                      │                         │ 3. AI Model
       │                      │                         │    Processes
       │                      │                         │    Images
       │                      │                         │
       │                      │  4. Return Job ID       │
       │                      │ <───────────────────────│
       │                      │                         │
       │  5. Job ID Response  │                         │
       │ <────────────────────│                         │
       │                      │                         │
       │  6. Poll Job Status  │                         │
       │ ────────────────────>│                         │
       │                      │                         │
       │  7. Return Results   │                         │
       │ <────────────────────│                         │
       │                      │                         │
       │  8. Download PDF     │                         │
       │ ────────────────────>│ ───────────────────────>│
       │                      │                         │
       │  9. PDF Report       │                         │
       │ <────────────────────│ <───────────────────────│
       │                      │                         │
```

### Connection Details

#### 1️⃣ **User Uploads Images (Browser → Next.js)**
```
URL: POST http://localhost:3000/api/upload
```
- User selects one or more bone marrow cell images
- Includes patient data (ID, name, age)
- Next.js API receives the request

#### 2️⃣ **Next.js Forwards to ML Backend**
```
URL: POST http://127.0.0.1:8000/api/analyze
```
The Next.js server acts as a **proxy** - it forwards the images to the Python backend:

```javascript
// File: app/api/upload/route.js
const ML_BACKEND_URL = 'http://127.0.0.1:8000';

// Forward images to Python backend
const mlResponse = await fetch(`${ML_BACKEND_URL}/api/analyze`, {
  method: 'POST',
  body: formData  // Contains images + patient data
});
```

#### 3️⃣ **ML Backend Processes Images**
```python
# File: backend/main.py
@app.post("/api/analyze")
async def analyze_image(images: List[UploadFile], ...):
    # Save images
    # Run AI classification
    # Generate PDF report
    # Return job ID
```

#### 4️⃣ **Status Polling**
```
URL: GET http://localhost:3000/api/jobs/{jobId}/status
```
Frontend periodically checks if processing is complete.

#### 5️⃣ **Download Report**
```
URL: GET http://localhost:3000/api/reports/{jobId}
```
Next.js fetches PDF from Python backend and sends to browser.

---

## 🔗 Configuration Files

### Frontend Environment (`.env.local`)
```env
# MongoDB connection
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/cytomind

# JWT Secret for authentication
JWT_SECRET=your-secret-key

# ML Backend URL (Python server)
ML_BACKEND_URL=http://127.0.0.1:8000
```

### Backend Environment (`backend/.env`)
```env
# MongoDB connection
MONGODB_URI=
# Model path
MODEL_PATH=../ensemble_final.pth
```

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.9+
- MongoDB (Atlas or local)

### Step 1: Install Frontend Dependencies
```bash
cd C:\Users\manju\Cytomind
npm install
```

### Step 2: Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 3: Start ML Backend (Terminal 1)
```bash
cd backend
python main.py
```
✅ Backend runs on: `http://127.0.0.1:8000`

### Step 4: Start Frontend (Terminal 2)
```bash
npm run dev
```
✅ Frontend runs on: `http://localhost:3000`

### Step 5: Open Browser
Navigate to `http://localhost:3000`

---

## 📁 Project Structure

```
Cytomind/
├── app/                          # Next.js App Router
│   ├── api/                      # API Routes (Backend for Frontend)
│   │   ├── auth/                 # Login/Register endpoints
│   │   ├── upload/               # Image upload → forwards to ML
│   │   ├── jobs/[jobId]/status/  # Job status checking
│   │   └── reports/[jobId]/      # PDF download
│   ├── layout.js
│   └── page.js
│
├── src/
│   ├── components/               # React UI Components
│   │   ├── Dashboard.jsx         # Main dashboard
│   │   ├── ImageUpload.jsx       # Multi-image uploader
│   │   ├── PatientForm.jsx       # Patient data input
│   │   ├── StatusTracker.jsx     # Progress tracking
│   │   └── ReportViewer.jsx      # Results display
│   ├── context/
│   │   └── AuthContext.js        # Authentication state
│   ├── lib/
│   │   ├── api.js                # API client functions
│   │   ├── auth.js               # JWT verification
│   │   └── db.js                 # MongoDB connection
│   └── models/                   # Mongoose schemas
│       ├── User.js
│       ├── Patient.js
│       ├── Job.js
│       └── Report.js
│
├── backend/                      # Python ML Backend
│   ├── main.py                   # FastAPI application
│   ├── model_loader.py           # PyTorch model loading
│   ├── report_generator.py       # PDF report creation
│   ├── database.py               # MongoDB operations
│   ├── config.py                 # Configuration
│   └── requirements.txt          # Python dependencies
│
├── ensemble_final.pth            # Trained AI Model (ViT + ResNet)
├── model_metadata.json           # Model configuration
└── .env.local                    # Environment variables
```

---

## 🔌 API Endpoints

### Frontend APIs (Next.js - Port 3000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | User login |
| POST | `/api/upload` | Upload images for analysis |
| GET | `/api/jobs/{jobId}/status` | Check job status |
| GET | `/api/reports/{jobId}` | Download PDF report |

### ML Backend APIs (Python - Port 8000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Detailed health status |
| POST | `/api/analyze` | Analyze images (multi-image) |
| GET | `/api/jobs/{jobId}/status` | Job status |
| GET | `/api/reports/{jobId}/pdf` | Get PDF report |

---

## 🧬 Cell Types (21 Classes)

The AI model classifies bone marrow cells into these categories:

| Code | Cell Type | Category |
|------|-----------|----------|
| ABE | Abnormal Eosinophil | Abnormal |
| ART | Artefact | Technical |
| BAS | Basophil | Normal Granulocyte |
| **BLA** | **Blast Cell** | **⚠️ Malignant** |
| EBO | Erythroblast | Erythroid Precursor |
| EOS | Eosinophil | Normal Granulocyte |
| **FGC** | **Faggot Cell** | **⚠️ Malignant (APL)** |
| **HAC** | **Hairy Cell** | **⚠️ Malignant** |
| KSC | Kidney Shaped Cell | Monocytic |
| LYI | Immature Lymphocyte | Immature |
| LYT | Lymphocyte | Normal Lymphoid |
| MMZ | Metamyelocyte | Granulocyte Precursor |
| MON | Monocyte | Normal Monocytic |
| **MYB** | **Myeloblast** | **⚠️ Malignant** |
| NGB | Band Neutrophil | Granulocyte Precursor |
| NGS | Segmented Neutrophil | Normal Granulocyte |
| NIF | Immature Neutrophil | Granulocyte Precursor |
| OTH | Other | Unclassified |
| PEB | Proerythroblast | Erythroid Precursor |
| **PLM** | **Plasma Cell** | **⚠️ Potentially Malignant** |
| **PMO** | **Promyelocyte** | **⚠️ Potentially Malignant** |

---

## 🧠 AI Model Details

- **Architecture**: Ensemble of ViT (Vision Transformer) + ResNet50
- **Input Size**: 224 × 224 pixels
- **Output**: 21 cell type probabilities
- **Framework**: PyTorch + HuggingFace Transformers

---

## 📊 Report Features

The generated PDF report includes:

✅ Patient Information  
✅ Overall Classification (BENIGN / SUSPICIOUS / MALIGNANT)  
✅ Risk Level Assessment  
✅ Cell Type Distribution Table  
✅ Individual Cell Analysis (for multiple images)  
✅ Clinical Interpretation  
✅ Recommendations  
✅ Quality Metrics  

---

## 🔒 Authentication

- JWT-based authentication
- Passwords hashed with bcrypt
- Token stored in localStorage
- Protected API routes

---

## 📞 Support

For issues or questions, please open a GitHub issue.

---

**© 2026 Cytomind | AI-Powered Bone Marrow Analysis**
