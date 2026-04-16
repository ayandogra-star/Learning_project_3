"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class FileUploadResponse(BaseModel):
    """Response after file upload."""
    id: int
    filename: str
    file_size: int
    message: str
    upload_time: str
    processing_time: float


class FileMetadataResponse(BaseModel):
    """File metadata response."""
    id: int
    filename: str
    file_size: int
    upload_time: str
    processing_time: float
    status: str


class ContractKPIs(BaseModel):
    """Contract analysis KPIs extracted from documents."""
    totalContractsProcessed: str = Field(default="Not Present", description="Total contracts processed")
    contractType: str = Field(default="Not Present", description="Type of contract")
    contractStatus: str = Field(default="Not Present", description="Current status of contract")
    complianceScore: str = Field(default="Not Present", description="Compliance score percentage")
    controlCoveragePercentage: str = Field(default="Not Present", description="Control coverage percentage")
    incidentReadinessScore: str = Field(default="Not Present", description="Incident readiness score")
    highRiskIssuesCount: str = Field(default="Not Present", description="Count of high-risk issues")
    openRisksCount: str = Field(default="Not Present", description="Count of open risks")
    averageTimeToRemediate: str = Field(default="Not Present", description="Average time to remediate in days")
    totalContractValue: str = Field(default="Not Present", description="Total contract value")
    revenueAtRisk: str = Field(default="Not Present", description="Revenue at risk")
    totalObligationsExtracted: str = Field(default="Not Present", description="Total obligations extracted")
    obligationsCompletionRate: str = Field(default="Not Present", description="Obligations completion rate percentage")
    upcomingExpirations: str = Field(default="Not Present", description="Upcoming expiration dates")
    averageProcessingTime: str = Field(default="Not Present", description="Average processing time")
    clauseExtractionAccuracy: str = Field(default="Not Present", description="Clause extraction accuracy percentage")
    dataResidencyCompliance: str = Field(default="Not Present", description="Data residency compliance status")
    encryptionCompliance: str = Field(default="Not Present", description="Encryption compliance status")
    mfaCoverage: str = Field(default="Not Present", description="MFA coverage percentage")


class DashboardMetrics(BaseModel):
    """Dashboard metrics response."""
    kpis: ContractKPIs = Field(..., description="Extracted contract KPIs")
    contracts_processed_today: int = Field(default=0, description="Contracts processed today")


class AnalyzedContractResponse(BaseModel):
    """Response containing analyzed contract KPIs."""
    filename: str = Field(..., description="Name of the analyzed contract file")
    kpis: ContractKPIs = Field(..., description="Extracted contract KPIs")
    analysis_timestamp: str = Field(..., description="Timestamp of analysis in ISO format")
    message: str = Field(default="Contract analyzed successfully", description="Response message")


class RAGChunkMetadata(BaseModel):
    """Metadata for a RAG chunk."""
    chunk_id: str = Field(..., description="Unique chunk identifier")
    page_number: int = Field(..., description="Page number in source document")
    section_title: Optional[str] = Field(default=None, description="Section title if identifiable")
    content_type: str = Field(..., description="Type of content: 'text' or 'table'")
    source_filename: str = Field(..., description="Source PDF filename")


class RAGChunkResponse(BaseModel):
    """Response for a single RAG chunk."""
    chunk_id: str = Field(..., description="Unique chunk identifier")
    content: str = Field(..., description="Chunk text content")
    page_number: int = Field(..., description="Page number")
    section_title: Optional[str] = Field(default=None, description="Section title")
    content_type: str = Field(..., description="Content type (text or table)")
    token_count: int = Field(..., description="Token count in chunk")
    metadata: RAGChunkMetadata


class RAGRetrievalResponse(BaseModel):
    """Response for RAG chunk retrieval/search."""
    vector_id: int = Field(..., description="Vector ID in FAISS index")
    chunk_id: str = Field(..., description="Chunk ID")
    file_id: int = Field(..., description="File ID")
    similarity_score: float = Field(..., description="Similarity score (0-1)")
    metadata: Dict[str, Any] = Field(..., description="Chunk metadata")


class RAGProcessingResponse(BaseModel):
    """Response after RAG processing of a document."""
    file_id: int = Field(..., description="File ID")
    source_filename: str = Field(..., description="Source filename")
    total_chunks: int = Field(..., description="Total chunks created")
    text_chunks: int = Field(..., description="Number of text chunks")
    table_chunks: int = Field(..., description="Number of table chunks")
    embeddings_added: int = Field(..., description="Number of embeddings added to vector store")
    status: str = Field(..., description="Processing status")
    metadata: Dict[str, Any] = Field(..., description="Processing metadata")


class RAGSearchRequest(BaseModel):
    """Request for RAG chunk search."""
    query: str = Field(..., description="Search query")
    top_k: int = Field(default=5, description="Number of results to return")
    file_id: Optional[int] = Field(default=None, description="Optional file ID to filter by")
