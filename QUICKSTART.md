# Quick Reference Guide

## 🚀 Start Application (First Time)

### Mac/Linux
```bash
chmod +x setup.sh
./setup.sh
```

### Windows
```bash
setup.bat
```

## 🚀 Start Application (After Setup)

### Terminal 1: Backend
```bash
cd backend
source venv/bin/activate    # or: venv\Scripts\activate on Windows
python -m uvicorn app.main:app --reload --port 8000
```

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

### Open Browser
http://localhost:5173

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Main project documentation |
| `DEVELOPMENT.md` | Development guide & troubleshooting |
| `backend/README.md` | Backend setup & API endpoints |
| `frontend/README.md` | Frontend setup & architecture |

---

## 🔗 Access Points

| Service | URL |
|---------|-----|
| **Frontend App** | http://localhost:5173 |
| **Backend API** | http://localhost:8000 |
| **Swagger Docs** | http://localhost:8000/docs |
| **ReDoc** | http://localhost:8000/redoc |

---

## 📁 Key Files

### Backend
- `backend/app/main.py` - FastAPI app configuration
- `backend/app/routes/files.py` - File upload endpoints
- `backend/app/services/file_service.py` - Business logic

### Frontend
- `frontend/src/components/LandingPage.jsx` - Home page
- `frontend/src/components/UploadForm.jsx` - Upload modal
- `frontend/src/components/Dashboard.jsx` - Analytics
- `frontend/src/services/api.js` - API client

---

## 🔧 Common Commands

### Backend
```bash
# Run with watched reload
python -m uvicorn app.main:app --reload --port 8000

# Run in production
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# View API docs
open http://localhost:8000/docs
```

### Frontend
```bash
# Development server
npm run dev

# Production build
npm run build

# Preview build
npm run preview
```

---

## 📤 API Endpoints Quick Reference

```bash
# Upload file
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@document.pdf"

# Get metrics
curl http://localhost:8000/api/dashboard/metrics

# Get all files
curl http://localhost:8000/api/files

# Health check
curl http://localhost:8000/health
```

---

## ✨ Features

- ✅ Clean, modern UI with gradient design
- ✅ Drag-and-drop file upload
- ✅ Real-time upload progress
- ✅ Automatic dashboard redirect
- ✅ KPI metrics cards
- ✅ Interactive charts
- ✅ File history with metadata
- ✅ Responsive mobile design
- ✅ Error handling
- ✅ File validation

---

## 🛠️ Tech Stack

**Frontend:** React · Vite · Tailwind CSS · Recharts · Axios
**Backend:** FastAPI · Python · Uvicorn · Pydantic

---

## 🐛 Quick Troubleshooting

### Port in use?
```bash
lsof -i :8000  # Check what's using port
kill -9 <PID>  # Kill process
```

### Dependencies issue?
```bash
# Backend
pip install --upgrade -r requirements.txt

# Frontend
rm -rf node_modules package-lock.json
npm install
```

### CORS errors?
Double-check:
1. Backend running on http://localhost:8000
2. Frontend .env has `VITE_API_URL=http://localhost:8000`

---

## 📸 UI Flow

LOGIN SCREEN: 
- Landing page with "Import PDF"
- Feature cards
- Modern gradient background

UPLOAD:
- Modal with drag-drop zone
- File validation
- Progress bar

DASHBOARD:
- 4 KPI cards
- 2 charts (bar + line)
- File history table
- Upload new files

---

## 🎯 Next Steps

1. Start the application (see top)
2. Click "Import PDF"
3. Upload a file
4. View dashboard metrics
5. Explore API docs

---

## 📞 Useful Links

- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- Tailwind CSS: https://tailwindcss.com/
- Vite: https://vitejs.dev/

---

**Ready to code? Let's go! 🚀**
