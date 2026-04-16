"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import files

# Create FastAPI app
app = FastAPI(
    title="PDF Processing API",
    description="A simple PDF upload and processing API",
    version="1.0.0"
)

# Add CORS middleware with explicit OPTIONS handling
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://localhost",
        "127.0.0.1",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=7200,
)

# Add explicit OPTIONS handlers BEFORE including routes
@app.options("/{full_path:path}")
async def preflight_handler(full_path: str):
    """Handle CORS preflight requests."""
    return {"status": "ok"}

# Include routes
app.include_router(files.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "PDF Processing API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
