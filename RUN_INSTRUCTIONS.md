# How to Run the Contract Analysis Agent

## ⚡ Quick Start (Recommended)

### For Mac/Linux:
```bash
cd /Users/ayandogra/Downloads/Manulife
chmod +x setup.sh
./setup.sh
```

### For Windows:
```bash
cd C:\Users\ayandogra\Downloads\Manulife
setup.bat
```

---

## 🔧 Manual Setup (Step-by-Step)

### Step 1: Start Backend (Terminal Tab 1)

```bash
cd /Users/ayandogra/Downloads/Manulife/backend

# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
# On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python -m uvicorn app.main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

✅ **Backend ready at:** `http://localhost:8000`

---

### Step 2: Start Frontend (Terminal Tab 2)

```bash
cd /Users/ayandogra/Downloads/Manulife/frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

Expected output:
```
  VITE v5.0.0  ready in 140 ms
  ➜  Local:   http://localhost:5173/
```

✅ **Frontend ready at:** `http://localhost:5173`

---

## 🎯 Open the Application

Visit: **http://localhost:5173**

You'll see:
- 🎨 Beautiful gradient hero section
- 📋 "Contract Analysis Agent" title
- ✨ 3 feature cards (KPI Extraction, Compliance Analysis, Risk Management)
- 🔵 "Analyze Contract" button

---

## 📋 How to Use

1. Click **"Analyze Contract"** button
2. Upload a PDF/DOC file by:
   - Dragging & dropping into upload zone, OR
   - Clicking to select from file browser
3. Watch progress bar (2.5 second simulation)
4. View **Dashboard** with 18 extracted KPIs in 5 categories:
   - Contract Overview (4 KPIs)
   - Compliance & Risk (4 KPIs)
   - Risk & Obligations (4 KPIs)
   - Security & Obligations (4 KPIs)
   - Processing & Accuracy (3 KPIs)

---

## 🐛 Troubleshooting

### Backend won't start: "Address already in use"

```bash
# Kill process using port 8000
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Backend won't start: "No module named fastapi"

```bash
# Ensure you're in the backend directory with venv activated
cd /Users/ayandogra/Downloads/Manulife/backend
source venv/bin/activate
pip install -r requirements.txt
```

### Backend won't start: "python: command not found"

```bash
# Use python3 explicitly
python3 -m uvicorn app.main:app --reload --port 8000
```

### Frontend won't start: "npm: command not found"

Install Node.js from https://nodejs.org/ then try again

### Frontend won't start: "node_modules" errors

```bash
cd /Users/ayandogra/Downloads/Manulife/frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Port 5173 already in use

```bash
lsof -i :5173 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

---

## 🧪 Test API Endpoints

### Using Swagger UI (Easiest)

Visit: **http://localhost:8000/docs**
- Try out each endpoint interactively
- Upload test files
- See real-time responses

### Using cURL

**Health check:**
```bash
curl http://localhost:8000/health
```

**Get dashboard metrics:**
```bash
curl http://localhost:8000/api/dashboard/metrics
```

**Get all analyzed files:**
```bash
curl http://localhost:8000/api/files
```

**Upload a file:**
```bash
curl -X POST http://localhost:8000/api/upload -F "file=@/path/to/your/file.pdf"
```

---

## 📁 Project Structure

```
Manulife/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── schemas.py           # Pydantic models (ContractKPIs)
│   │   ├── models.py            # FileMetadata storage
│   │   ├── routes/
│   │   │   └── files.py         # API endpoints
│   │   └── services/
│   │       └── file_service.py  # Business logic
│   ├── uploads/                 # Uploaded files directory
│   ├── requirements.txt         # Python dependencies
│   └── venv/                    # Virtual environment
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx    # 18 KPI dashboard
│   │   │   ├── LandingPage.jsx  # Home page
│   │   │   └── UploadForm.jsx   # Upload modal
│   │   ├── services/
│   │   │   └── api.js           # Axios HTTP client
│   │   ├── App.jsx              # Router setup
│   │   └── main.jsx             # React entry point
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── node_modules/            # NPM dependencies
│
├── RUN_INSTRUCTIONS.md          # This file
├── README.md
├── ARCHITECTURE.md
├── DEVELOPMENT.md
├── setup.sh                     # Auto-setup for Mac/Linux
└── setup.bat                    # Auto-setup for Windows
```

---

## 🛑 Stop the Application

**To stop backend (Terminal 1):**
```
Press: Ctrl + C
```

**To stop frontend (Terminal 2):**
```
Press: Ctrl + C
```

---

## 📊 API Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/upload` | Upload contract for analysis |
| GET | `/api/dashboard/metrics` | Get 18 contract KPIs |
| GET | `/api/files` | List all analyzed contracts |
| GET | `/health` | API health check |
| GET | `/docs` | Swagger API documentation |
| GET | `/redoc` | ReDoc API documentation |

### Sample Response: `/api/dashboard/metrics`

```json
{
  "kpis": {
    "TotalContractsProcessed": "3",
    "ContractType": "Not Present",
    "ContractStatus": "Not Present",
    "ComplianceScore": "Not Present",
    "ControlCoveragePercentage": "Not Present",
    "IncidentReadinessScore": "Not Present",
    "HighRiskIssuesCount": "Not Present",
    "OpenRisksCount": "Not Present",
    "AverageTimeToRemediate": "Not Present",
    "TotalContractValue": "Not Present",
    "RevenueAtRisk": "Not Present",
    "TotalObligationsExtracted": "Not Present",
    "ObligationsCompletionRate": "Not Present",
    "UpcomingExpirations": "Not Present",
    "AverageProcessingTime": "2.5s",
    "ClauseExtractionAccuracy": "Not Present",
    "DataResidencyCompliance": "Not Present",
    "EncryptionCompliance": "Not Present",
    "MFACoverage": "Not Present"
  },
  "contracts_processed_today": 3
}
```

---

## ⚙️ Configuration

### Change Backend Port

Edit the uvicorn command:
```bash
python -m uvicorn app.main:app --reload --port 9000
```

### Change Frontend Port

Edit `frontend/vite.config.js`:
```javascript
export default {
  plugins: [react()],
  server: {
    port: 3000  // Change to desired port
  }
}
```

### Custom API URL

Create `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
```

---

## 📚 Additional Commands

**Build frontend for production:**
```bash
cd frontend
npm run build
```

**Preview production build locally:**
```bash
cd frontend
npm run preview
```

**Run backend tests:**
```bash
cd backend
pytest
```

**Check frontend code style:**
```bash
cd frontend
npm run lint
```

---

## ✅ Verification Checklist

Before using the app, verify:

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:5173
- [ ] Can access http://localhost:5173 in browser
- [ ] "Analyze Contract" button is visible
- [ ] Can upload a file without errors
- [ ] Dashboard displays all 18 KPI cards
- [ ] Swagger API docs accessible at http://localhost:8000/docs
- [ ] File upload progress bar works
- [ ] File appears in uploaded files list

---

## 🆘 Advanced Troubleshooting

### Check Python version
```bash
python3 --version
# Should be 3.9 or higher
```

### Check Node.js version
```bash
node --version
npm --version
# Should be 16+ and 8+ respectively
```

### View backend logs
The backend logs appear in Terminal 1 with all requests logged

### View frontend logs
Open browser Developer Tools (F12) → Console tab

### Check if ports are blocked by firewall
```bash
sudo lsof -i :8000
sudo lsof -i :5173
```

### Kill ALL Python processes
```bash
pkill -9 -f "uvicorn"
pkill -9 -f "python"
```

### Restart from scratch
```bash
# Kill everything
pkill -9 -f "npm"
pkill -9 -f "uvicorn"
pkill -9 -f "python"

# Clean dependencies
cd /Users/ayandogra/Downloads/Manulife/backend
rm -rf venv

cd /Users/ayandogra/Downloads/Manulife/frontend
rm -rf node_modules package-lock.json

# Start fresh
./setup.sh  # Or setup.bat on Windows
```

---

## 📞 Need Help?

1. **Check Terminal Output** - Error messages tell you what's wrong
2. **Read the Error** - Don't ignore the error text, it's helpful!
3. **Check Browser Console** - Open DevTools (F12) for frontend errors
4. **Verify Prerequisites** - Python 3.9+, Node.js 16+, npm 8+
5. **Try the Troubleshooting Section** - Most issues are covered above

---

**🚀 Happy analyzing!**

For more details, see:
- [README.md](./README.md) - Project overview
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design
- [DEVELOPMENT.md](./DEVELOPMENT.md) - Development guide
