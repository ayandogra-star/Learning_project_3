# Architecture & System Design

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      USER BROWSER                           │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              REACT FRONTEND (Port 5173)               │ │
│  │                                                        │ │
│  │  ┌──────────────────────────────────────────┐        │ │
│  │  │         Landing Page                     │        │ │
│  │  │  - Hero section with features           │        │ │
│  │  │  - Import PDF button                    │        │ │
│  │  └──────────────────────────────────────────┘        │ │
│  │                        ↓                              │ │
│  │  ┌──────────────────────────────────────────┐        │ │
│  │  │         Upload Form Modal                │        │ │
│  │  │  - Drag & drop zone                      │        │ │
│  │  │  - File validation                       │        │ │
│  │  │  - Progress bar                          │        │ │
│  │  │  - Error handling                        │        │ │
│  │  └──────────────────────────────────────────┘        │ │
│  │                        ↓                              │ │
│  │  ┌──────────────────────────────────────────┐        │ │
│  │  │         Dashboard Page                   │        │ │
│  │  │  - 4 KPI Cards (Metrics)                 │        │ │
│  │  │  - Bar chart (docs by day)               │        │ │
│  │  │  - Line chart (performance)              │        │ │
│  │  │  - File history table                    │        │ │
│  │  └──────────────────────────────────────────┘        │ │
│  │                                                        │ │
│  │  Services:                                            │ │
│  │  - React Router (SPA navigation)                     │ │
│  │  - Axios (API calls)                                 │ │
│  │  - Recharts (data visualization)                     │ │
│  │  - Tailwind CSS (styling)                            │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                             │
│                     HTTP/REST API                           │
│              CORS: localhost:5173 allowed                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            ↕ (HTTP)
┌─────────────────────────────────────────────────────────────┐
│                FASTAPI BACKEND (Port 8000)                 │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                Route Handlers                          │ │
│  │                                                        │ │
│  │  POST /api/upload                                     │ │
│  │  ├─→ Upload file from frontend                        │ │
│  │  ├─→ Validate file type & size                        │ │
│  │  ├─→ Save to disk (uploads/)                          │ │
│  │  ├─→ Simulate processing (2.5s)                       │ │
│  │  ├─→ Create metadata                                   │ │
│  │  └─→ Return response                                   │ │
│  │                                                        │ │
│  │  GET /api/dashboard/metrics                           │ │
│  │  ├─→ Calculate KPI metrics                            │ │
│  │  ├─→ Group documents by day                           │ │
│  │  └─→ Return chart data                                │ │
│  │                                                        │ │
│  │  GET /api/files                                       │ │
│  │  ├─→ Retrieve all uploaded files                      │ │
│  │  └─→ Return file metadata list                        │ │
│  │                                                        │ │
│  │  GET /health                                          │ │
│  │  └─→ Return health status                             │ │
│  │                                                        │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ↓                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           File Service (Business Logic)               │ │
│  │                                                        │ │
│  │  - save_upload_file()                                 │ │
│  │  - get_all_files()                                    │ │
│  │  - get_dashboard_metrics()                            │ │
│  │                                                        │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ↓                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Storage & Models                          │ │
│  │                                                        │ │
│  │  FileMetadata (In-Memory Storage)                     │ │
│  │  ├─ id: int                                            │ │
│  │  ├─ filename: str                                      │ │
│  │  ├─ file_size: int                                     │ │
│  │  ├─ upload_time: datetime                              │ │
│  │  ├─ processing_time: float                             │ │
│  │  └─ status: str                                        │ │
│  │                                                        │ │
│  │  📁 /uploads/ (Disk Storage)                           │ │
│  │  └─ uploaded files stored here                         │ │
│  │                                                        │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### Upload Flow
```
User Selects File
       ↓
File Validation (Client)
       ↓
POST /api/upload (with file)
       ↓
Backend Validation
       ↓
Save File to Disk
       ↓
Simulate Processing (2.5s)
       ↓
Create Metadata
       ↓
Store in Memory
       ↓
Return Success Response
       ↓
Redirect to Dashboard
```

### Dashboard Load Flow
```
Dashboard Component Mounts
       ↓
useEffect Hook Triggered
       ↓
Parallel API Calls:
  ├─→ GET /api/dashboard/metrics
  └─→ GET /api/files
       ↓
Calculate KPIs
       ↓
Format Chart Data
       ↓
Update React State
       ↓
Render UI with Data
       ↓
Display Cards + Charts + Table
```

## Component Hierarchy

```
App (Router)
├── LandingPage
│   └── UploadForm (modal)
│       └── File Upload UI
│       └── Progress Bar
│
└── Dashboard
    ├── Header
    │   ├── Title
    │   └── New Upload Button
    │
    ├── KPI Cards Container
    │   ├── Card 1: Total Documents
    │   ├── Card 2: Avg Processing Time
    │   ├── Card 3: Success Rate
    │   └── Card 4: Extracted Data Points
    │
    ├── Charts Container
    │   ├── BarChart: Documents by Day
    │   └── LineChart: Performance Metrics
    │
    └── Files Table
        └── Table with File History
```

## API Schema

### Request/Response Models

```
FileUploadResponse:
  - id: int
  - filename: string
  - file_size: int
  - message: string
  - upload_time: ISO datetime
  - processing_time: float

DashboardMetrics:
  - total_documents_processed: int
  - average_processing_time: float
  - success_rate: float
  - extracted_data_points: int
  - documents_by_day: [
      { date: string, count: int }
    ]

FileMetadataResponse:
  - id: int
  - filename: string
  - file_size: int
  - upload_time: ISO datetime
  - processing_time: float
  - status: string
```

## Directory Tree

```
Manulife/
├── backend/                         # FastAPI Application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app setup & CORS
│   │   ├── models.py               # FileMetadata model
│   │   ├── schemas.py              # Pydantic schemas
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── files.py            # File endpoints
│   │   └── services/
│   │       ├── __init__.py
│   │       └── file_service.py     # Business logic
│   ├── uploads/                    # File storage
│   ├── requirements.txt            # Python dependencies
│   └── README.md
│
├── frontend/                        # React Application
│   ├── src/
│   │   ├── components/
│   │   │   ├── LandingPage.jsx     # Home page
│   │   │   ├── UploadForm.jsx      # Upload modal
│   │   │   ├── Dashboard.jsx       # Analytics page
│   │   ├── services/
│   │   │   └── api.js              # Axios API client
│   │   ├── App.jsx                 # Main app with routing
│   │   ├── main.jsx                # React DOM entry
│   │   └── index.css               # Global styles
│   ├── package.json                # Node dependencies
│   ├── vite.config.js              # Vite config
│   ├── tailwind.config.js          # Tailwind theme
│   ├── postcss.config.js           # PostCSS setup
│   ├── .env                        # Environment variables
│   └── README.md
│
├── README.md                        # Main documentation
├── QUICKSTART.md                   # Quick reference
├── DEVELOPMENT.md                  # Development guide
├── ARCHITECTURE.md                 # This file
├── setup.sh                        # Auto setup (Mac/Linux)
├── setup.bat                       # Auto setup (Windows)
└── .gitignore                      # Git ignore rules
```

## Technology Decisions

### Why FastAPI?
- ✅ Modern async/await support
- ✅ Automatic API documentation
- ✅ Built-in data validation (Pydantic)
- ✅ High performance
- ✅ Easy to learn and use

### Why React + Vite?
- ✅ Fast development with HMR
- ✅ Modern hooks API
- ✅ Large ecosystem
- ✅ Component reusability
- ✅ Great developer experience

### Why Tailwind CSS?
- ✅ Utility-first approach
- ✅ Fast development
- ✅ Consistent design system
- ✅ Highly customizable
- ✅ Great for responsive design

### Why In-Memory Storage?
- ✅ Simple for demo/MVP
- ✅ Fast access
- ✅ No database setup needed
- ✅ Can be replaced with DB later

## Performance Considerations

### Frontend
- Lazy loading ready for components
- CSS minified via Tailwind
- Tree-shaking via Vite
- Gzip compression in production

### Backend
- Async file handling
- Efficient file streaming
- Memory-efficient
- Ready for horizontal scaling

## Security Measures

- ✅ File type validation
- ✅ File size limits
- ✅ CORS protection
- ✅ Input validation (Pydantic)
- ⚠️ TODO: JWT authentication
- ⚠️ TODO: Rate limiting
- ⚠️ TODO: HTTPS in production

## Scalability Path

```
Current (Single Application)
    ↓
Add: Database (PostgreSQL)
    ↓
Add: Authentication (JWT)
    ↓
Add: Advanced File Processing
    ↓
Add: Microservices (if needed)
    ↓
Add: Message Queue (Redis/RabbitMQ)
    ↓
Add: Container Orchestration (Docker/K8s)
```

---

See `DEVELOPMENT.md` for implementation details and customization options.
