# Cytomind ML Backend

FastAPI backend for bone marrow cell classification using the trained PyTorch ensemble model.

## Setup

### 1. Create a virtual environment

```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Create a `.env` file with:

```
MONGODB_URI=mongodb://localhost:27017/cytomind
HOST=127.0.0.1
PORT=8000
```

### 4. Run the server

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Detailed health check |
| POST | `/api/analyze` | Analyze image (with job tracking) |
| POST | `/api/predict` | Quick prediction (no database) |
| GET | `/api/jobs/{job_id}/status` | Get job status |
| GET | `/api/reports/{job_id}` | Get report details |
| GET | `/api/reports/{job_id}/pdf` | Download PDF report |

## Model Information

The backend loads `ensemble_final.pth` which is an ensemble model combining:
- EfficientNet-B3
- ResNet-50
- DenseNet-121

### Supported Cell Types (21 classes)

| Code | Cell Type |
|------|-----------|
| ABE | Abnormal Eosinophil |
| ART | Artefact |
| BAS | Basophil |
| BLA | Blast |
| EBO | Erythroblast |
| EOS | Eosinophil |
| FGC | Faggot Cell |
| HAC | Hairy Cell |
| KSC | Kidney Shaped Cell |
| LYI | Lymphocyte Immature |
| LYT | Lymphocyte |
| MMZ | Metamyelocyte |
| MON | Monocyte |
| MYB | Myeloblast |
| NGB | Band Neutrophil |
| NGS | Segmented Neutrophil |
| NIF | Neutrophil Immature Forms |
| OTH | Other |
| PEB | Proerythroblast |
| PLM | Plasma Cell |
| PMO | Promyelocyte |

## Running with Frontend

1. Start the ML backend first:
   ```bash
   cd backend
   python main.py
   ```

2. In a new terminal, start the Next.js frontend:
   ```bash
   npm run dev
   ```

3. Access the application at `http://localhost:3000`
