# Backend Setup

This is the FastAPI backend for the PDF Processing application.

## Prerequisites

- Python 3.9+
- pip

## Installation & Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Backend

From the backend directory with the virtual environment activated:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

The API will be available at:
- **Base URL**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc

## API Endpoints

### File Upload
- **POST** `/api/upload` - Upload a file for processing

### Dashboard Metrics
- **GET** `/api/dashboard/metrics` - Get KPI metrics and chart data

### File List
- **GET** `/api/files` - Get list of all uploaded files

### Health Check
- **GET** `/health` - Health check endpoint

## File Storage

Uploaded files are stored in the `uploads/` directory.

## Testing

You can test the API using:
1. Swagger UI at http://localhost:8000/docs
2. cURL commands
3. The frontend application

Example cURL for file upload:
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "accept: application/json" \
  -F "file=@path/to/your/file.pdf"
```
