"""API routes for file operations."""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Path, Query
from app.services.file_service import FileService
from app.services.rag_pipeline import RAGPipeline
from app.services.contract_definition_generator import ContractDefinitionGenerator
from app.services.compliance_analyzer import ComplianceAnalyzer
from app.schemas import (
    FileUploadResponse, DashboardMetrics, FileMetadataResponse, AnalyzedContractResponse,
    RAGChunkResponse, RAGRetrievalResponse, RAGProcessingResponse, RAGSearchRequest,
    ContractDefinitionRequest, ContractDefinitionResponse, RAGQueryRequest, RAGQueryResponse,
    ComplianceAnalysisRequest, ComplianceAnalysisResponse, ComplianceFinding
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


@router.post("/rag/define", response_model=ContractDefinitionResponse)
async def define_contract_term(request: ContractDefinitionRequest):
    """
    Get definition of a contract term using RAG.
    
    Retrieves relevant sections and uses LLM to generate a definition.
    
    Args:
        request: ContractDefinitionRequest with term and file_id
        
    Returns:
        ContractDefinitionResponse with detailed definition
    """
    try:
        # Retrieve relevant chunks
        rag_pipeline = RAGPipeline()
        retrieved_chunks = rag_pipeline.retrieve_chunks(
            query=request.term,
            file_id=request.file_id,
            top_k=8
        )
        
        if not retrieved_chunks:
            return ContractDefinitionResponse(
                term=request.term,
                definition="Not explicitly defined in the contract",
                confidence="low",
                file_id=request.file_id,
                chunks_used=0,
                message=f"No relevant sections found for '{request.term}'"
            )
        
        # Generate definition using LLM
        definition_response = ContractDefinitionGenerator.generate_definition(
            query=request.term,
            retrieved_chunks=retrieved_chunks,
            file_id=request.file_id
        )
        
        # Convert to schema
        return ContractDefinitionResponse(**definition_response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag/query", response_model=RAGQueryResponse)
async def query_rag_system(request: RAGQueryRequest):
    """
    Generic RAG query endpoint for contract analysis.
    
    Supports query types: definition|section|compliance|risk
    
    Args:
        request: RAGQueryRequest with query, file_id, and query_type
        
    Returns:
        RAGQueryResponse with results
    """
    try:
        # Retrieve relevant chunks
        rag_pipeline = RAGPipeline()
        retrieved_chunks = rag_pipeline.retrieve_chunks(
            query=request.query,
            file_id=request.file_id,
            top_k=request.top_k
        )
        
        if not retrieved_chunks:
            return RAGQueryResponse(
                query=request.query,
                query_type=request.query_type,
                results={"message": f"No relevant sections found for '{request.query}'"},
                retrieved_chunks=0
            )
        
        # Generate response based on query type
        if request.query_type == "definition":
            results = ContractDefinitionGenerator.generate_definition(
                query=request.query,
                retrieved_chunks=retrieved_chunks,
                file_id=request.file_id
            )
        elif request.query_type == "section":
            results = ContractDefinitionGenerator.generate_section_explanation(
                section_query=request.query,
                retrieved_chunks=retrieved_chunks
            )
        else:
            # Default: return raw chunks
            results = {
                "chunks": [
                    {
                        "chunk_id": chunk.get("chunk_id"),
                        "content": chunk.get("content", ""),
                        "page_number": chunk.get("metadata", {}).get("page_number"),
                        "similarity_score": chunk.get("boosted_similarity_score", chunk.get("similarity_score"))
                    }
                    for chunk in retrieved_chunks
                ]
            }
        
        return RAGQueryResponse(
            query=request.query,
            query_type=request.query_type,
            results=results,
            retrieved_chunks=len(retrieved_chunks),
            metadata={
                "file_id": request.file_id,
                "top_k": request.top_k
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compliance/analyze", response_model=ComplianceAnalysisResponse)
async def analyze_contract_compliance(request: ComplianceAnalysisRequest):
    """
    Perform compliance analysis on a contract.
    
    Retrieves relevant chunks and evaluates compliance across key areas:
    - Network Authentication & Authorization
    - MFA Enforcement
    - Logging and Monitoring
    - Incident Response
    - Data Encryption and Key Management
    
    Args:
        request: ComplianceAnalysisRequest with file_id
        
    Returns:
        ComplianceAnalysisResponse with compliance findings
        
    Raises:
        HTTPException: If analysis fails or file not found
    """
    try:
        rag_pipeline = RAGPipeline()
        
        # Build search query to retrieve relevant compliance sections
        compliance_query = "authentication authorization MFA encryption logging monitoring incident response data protection"
        
        # Retrieve relevant chunks
        retrieved_chunks = rag_pipeline.retrieve_chunks(
            query=compliance_query,
            file_id=request.file_id,
            top_k=request.top_k
        )
        
        if not retrieved_chunks:
            # Return non-compliant response if no chunks found
            findings = ComplianceAnalyzer.generate_compliance_analysis([])
        else:
            # Generate compliance analysis from retrieved chunks
            findings = ComplianceAnalyzer.generate_compliance_analysis(retrieved_chunks)
        
        # Calculate summary statistics
        summary = _calculate_compliance_summary(findings)
        
        return ComplianceAnalysisResponse(
            file_id=request.file_id,
            analysis_timestamp=datetime.utcnow().isoformat(),
            findings=findings,
            summary=summary,
            message="Compliance analysis completed successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Compliance analysis failed: {str(e)}"
        )


def _calculate_compliance_summary(findings: List[dict]) -> dict:
    """
    Calculate summary statistics from compliance findings.
    
    Args:
        findings: List of compliance findings
        
    Returns:
        Dictionary with summary statistics
    """
    total = len(findings)
    fully_compliant = sum(
        1 for f in findings 
        if f.get("compliance_state") == "Fully Compliant"
    )
    partially_compliant = sum(
        1 for f in findings 
        if f.get("compliance_state") == "Partially Compliant"
    )
    non_compliant = sum(
        1 for f in findings 
        if f.get("compliance_state") == "Non-Compliant"
    )
    avg_confidence = sum(
        f.get("confidence", 0) for f in findings
    ) / total if total > 0 else 0
    
    return {
        "total_requirements": total,
        "fully_compliant": fully_compliant,
        "partially_compliant": partially_compliant,
        "non_compliant": non_compliant,
        "average_confidence": round(avg_confidence, 2),
        "compliance_percentage": round((fully_compliant / total * 100) if total > 0 else 0, 1)
    }
