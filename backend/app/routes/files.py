"""API routes for file operations."""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Path, Query
from app.services.file_service import FileService
from app.services.rag_pipeline import RAGPipeline
from app.schemas import (
    FileUploadResponse, DashboardMetrics, FileMetadataResponse, AnalyzedContractResponse,
    RAGChunkResponse, RAGRetrievalResponse, RAGProcessingResponse, RAGSearchRequest
)
from datetime import datetime
from typing import List

router = APIRouter(prefix="/api", tags=["files"])


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a PDF file and process it for contract analysis.
    
    Args:
        file: The PDF file to upload
        
    Returns:
        FileUploadResponse with file metadata
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.txt', '.doc', '.docx')):
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF, TXT, DOC, DOCX allowed.")
        
        # Save file and get metadata
        metadata = await FileService.save_upload_file(file)
        
        return FileUploadResponse(
            id=metadata.id,
            filename=metadata.filename,
            file_size=metadata.file_size,
            message="File uploaded and analyzed successfully",
            upload_time=metadata.upload_time.isoformat(),
            processing_time=metadata.processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contracts/{file_id}/analysis", response_model=AnalyzedContractResponse)
async def get_contract_analysis(file_id: int):
    """
    Get contract analysis KPIs for a specific file.
    
    Args:
        file_id: The ID of the uploaded contract file
        
    Returns:
        AnalyzedContractResponse with extracted KPIs
    """
    try:
        metadata = FileService.get_file_by_id(file_id)
        if not metadata:
            raise HTTPException(status_code=404, detail=f"File with ID {file_id} not found")
        
        return AnalyzedContractResponse(
            filename=metadata.filename,
            kpis=metadata.kpis,
            analysis_timestamp=metadata.upload_time.isoformat(),
            message="Contract analyzed successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics():
    """
    Get dashboard metrics and statistics.
    
    Returns:
        DashboardMetrics with KPIs and chart data
    """
    metrics = FileService.get_dashboard_metrics()
    return DashboardMetrics(**metrics)


@router.get("/files", response_model=list[FileMetadataResponse])
async def get_all_files():
    """
    Get list of all uploaded files.
    
    Returns:
        List of FileMetadataResponse objects
    """
    files = FileService.get_all_files()
    return files


@router.get("/rag/{file_id}", response_model=dict)
async def get_rag_chunks(file_id: int):
    """
    Get all RAG chunks for a specific file.
    
    Args:
        file_id: The ID of the uploaded file
        
    Returns:
        Dict with chunk metadata and processing status
    """
    try:
        metadata = FileService.get_file_by_id(file_id)
        if not metadata:
            raise HTTPException(status_code=404, detail=f"File with ID {file_id} not found")
        
        rag_pipeline = RAGPipeline()
        chunks = rag_pipeline.get_file_chunks(file_id)
        
        return {
            "file_id": file_id,
            "filename": metadata.filename,
            "total_chunks": len(chunks),
            "chunks": chunks,
            "rag_metadata": metadata.rag_metadata,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag/search", response_model=List[RAGRetrievalResponse])
async def search_rag_chunks(request: RAGSearchRequest):
    """
    Search for relevant chunks based on query.
    
    Args:
        request: RAGSearchRequest with query and optional file_id filter
        
    Returns:
        List of relevant chunks sorted by similarity
    """
    try:
        rag_pipeline = RAGPipeline()
        results = rag_pipeline.retrieve_chunks(
            query=request.query,
            file_id=request.file_id,
            top_k=request.top_k
        )
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rag/retrieve", response_model=List[dict])
async def retrieve_chunks(
    query: str = Query(..., description="Search query"),
    top_k: int = Query(5, description="Number of results"),
    file_id: int = Query(None, description="Optional file ID filter")
):
    """
    Retrieve relevant chunks for a query (alternative GET endpoint).
    
    Args:
        query: Search query string
        top_k: Number of results to return
        file_id: Optional file ID to filter by
        
    Returns:
        List of relevant chunks
    """
    try:
        rag_pipeline = RAGPipeline()
        results = rag_pipeline.retrieve_chunks(
            query=query,
            file_id=file_id,
            top_k=top_k
        )
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

