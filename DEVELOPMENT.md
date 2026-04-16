# Development Guide

## Getting Started

### First Time Setup

1. **Clone/Download the project**
   ```bash
   cd Manulife
   ```

2. **Run the setup script** (Mac/Linux):
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
   
   Or on Windows:
   ```bash
   setup.bat
   ```

3. **Follow the script output** for running backend and frontend

### Manual Setup (if script doesn't work)

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Development Workflow

1. **Keep both servers running** in separate terminals
2. **Frontend** automatically reloads on file changes (HMR)
3. **Backend** automatically reloads on Python file changes

## Project Architecture

### Backend Structure
```
backend/
├── app/
│   ├── main.py              # FastAPI app setup
│   ├── models.py            # Database models (in-memory)
│   ├── schemas.py           # Pydantic schemas
│   ├── routes/
│   │   └── files.py         # File upload endpoints
│   └── services/
│       └── file_service.py  # Business logic
├── uploads/                 # Uploaded files
└── requirements.txt         # Python dependencies
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── LandingPage.jsx  # Home page
│   │   ├── UploadForm.jsx   # Upload modal
│   │   └── Dashboard.jsx    # Analytics page
│   ├── services/
│   │   └── api.js           # API client
│   ├── App.jsx              # Main app
│   ├── main.jsx             # Entry point
│   └── index.css            # Global styles
├── package.json             # Node dependencies
└── vite.config.js           # Vite configuration
```

## Key Technologies

### Backend
- **FastAPI**: Modern Python web framework with automatic API docs
- **Uvicorn**: ASGI server for running async Python apps
- **Pydantic**: Data validation using Python type hints

### Frontend  
- **React 18**: UI library with modern hooks
- **Vite**: Lightning-fast build tool
- **Tailwind CSS**: Utility-first CSS framework
- **Recharts**: React charting library
- **React Router**: Client-side navigation

## Customization Guide

### Change API Port
**Backend** (default: 8000):
```bash
python -m uvicorn app.main:app --reload --port 9000
```

**Frontend** `.env`:
```env
VITE_API_URL=http://localhost:9000
```

### Modify Upload Delay
Edit `backend/app/services/file_service.py`:
```python
# Line 28: Change 2.5 to desired seconds
await asyncio.sleep(2.5)
```

### Customize Dashboard Metrics
Edit `backend/app/services/file_service.py` → `get_dashboard_metrics()`:
- Change `extracted_points` calculation
- Modify chart data grouping
- Add new KPI metrics

### Update UI Colors
Edit `frontend/tailwind.config.js` → `theme.extend.colors`:
```javascript
colors: {
  primary: '#custom-color',
  secondary: '#another-color',
}
```

## Testing

### Manual Testing
1. Open http://localhost:5173
2. Click "Import PDF"
3. Drag/drop a file or select one
4. Watch progress bar
5. View dashboard

### API Testing
**Upload file with cURL:**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@test.pdf"
```

**Get metrics:**
```bash
curl "http://localhost:8000/api/dashboard/metrics"
```

**View API docs:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Browser Testing
- Chrome: Full support
- Firefox: Full support
- Safari: Full support
- Edge: Full support

## Common Issues & Solutions

### Issue: "Port already in use"
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Issue: "Module not found" (backend)
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Issue: "npm ERR" (frontend)
```bash
# Clear npm cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Issue: CORS errors
- Ensure backend is running: http://localhost:8000
- Check `.env` has correct `VITE_API_URL`
- Verify CORS origins in `backend/app/main.py`

## Performance Optimization

### Frontend
- Built with Vite for fast builds
- Tree-shaking removes unused code
- Lazy loading for routes (can be added)
- CSS is minified via Tailwind

### Backend
- Async/await for non-blocking I/O
- Efficient file streaming
- Query optimization ready

## Deployment Preparation

### Frontend Build
```bash
npm run build
```
Creates optimized `dist/` folder for deployment

### Backend Production
```bash
# Use production-grade server
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

## File Size Guidelines

- Keep frontend bundle under 1MB
- Limit uploaded files to 50MB
- Archive processed files periodically

## Security Checklist

- ✅ File type validation
- ✅ File size limits  
- ✅ CORS protection
- ✅ Input validation (Pydantic)
- ⚠️ Add: Authentication (next sprint)
- ⚠️ Add: Rate limiting (next sprint)
- ⚠️ Add: HTTPS in production (next sprint)

## Git Workflow

```bash
# Initialize git
git init

# Create commits
git add .
git commit -m "Initial full-stack PDF processor"

# Ignore files
# (Already configured in .gitignore)
```

## Support & Documentation

- FastAPI docs: https://fastapi.tiangolo.com/
- React docs: https://react.dev/
- Tailwind: https://tailwindcss.com/
- Vite: https://vitejs.dev/

---

Happy developing! 🚀
