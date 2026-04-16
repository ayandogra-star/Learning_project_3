"""File service for handling uploads and storage."""
import asyncio
from datetime import datetime
from pathlib import Path
from fastapi import UploadFile
from app.models import FileMetadata
from app.services.pdf_parser import PDFParser
from app.services.contract_analyzer import ContractAnalyzer
from app.services.rag_pipeline import RAGPipeline


UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


class FileService:
    """Service for handling file operations."""
    
    @staticmethod
    async def save_upload_file(file: UploadFile) -> FileMetadata:
        """
        Save uploaded file and process it for contract analysis and RAG.
        
        Args:
            file: The uploaded file from FastAPI
            
        Returns:
            FileMetadata object with file information, KPIs, and RAG metadata
        """
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Save file to disk
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Extract KPIs from the uploaded contract
        kpis = {}
        rag_metadata = {
            "chunks_created": 0,
            "embeddings_added": 0,
            "processing_status": "pending"
        }
        
        try:
            # Parse PDF if it's a PDF file
            if file.filename.lower().endswith('.pdf'):
                pdf_text = PDFParser.extract_text(file_path)
                kpis = ContractAnalyzer.extract_kpis(pdf_text)
            else:
                # For non-PDF files, try to read as text
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text_content = f.read()
                kpis = ContractAnalyzer.extract_kpis(text_content)
        except Exception as e:
            # Log error but don't fail - return default KPIs
            import traceback
            print(f"Error analyzing contract: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            kpis = {
                "totalContractsProcessed": "Not Present",
                "contractType": "Not Present",
                "contractStatus": "Not Present",
                "complianceScore": "Not Present",
                "controlCoveragePercentage": "Not Present",
                "incidentReadinessScore": "Not Present",
                "highRiskIssuesCount": "Not Present",
                "openRisksCount": "Not Present",
                "averageTimeToRemediate": "Not Present",
                "totalContractValue": "Not Present",
                "revenueAtRisk": "Not Present",
                "totalObligationsExtracted": "Not Present",
                "obligationsCompletionRate": "Not Present",
                "upcomingExpirations": "Not Present",
                "averageProcessingTime": "Not Present",
                "clauseExtractionAccuracy": "Not Present",
                "dataResidencyCompliance": "Not Present",
                "encryptionCompliance": "Not Present",
                "mfaCoverage": "Not Present"
            }
        
        # Simulate processing delay
        await asyncio.sleep(2.5)
        
        # Create metadata first (to get file_id)
        metadata = FileMetadata(
            filename=file.filename,
            file_size=file_size,
            upload_time=datetime.now(),
            kpis=kpis,
            rag_metadata=rag_metadata
        )
        
        FileMetadata.add(metadata)
        
        # Process RAG pipeline for supported file types
        try:
            if file.filename.lower().endswith('.pdf'):
                # Process PDF files
                rag_pipeline = RAGPipeline()
                rag_result = rag_pipeline.process_document(
                    file_path=file_path,
                    file_id=metadata.id,
                    source_filename=file.filename
                )
                
                # Update RAG metadata
                metadata.rag_metadata = {
                    "chunks_created": rag_result.get("total_chunks", 0),
                    "embeddings_added": rag_result.get("embeddings_added", 0),
                    "processing_status": rag_result.get("status", "completed"),
                    "details": {
                        "text_chunks": rag_result.get("text_chunks", 0),
                        "table_chunks": rag_result.get("table_chunks", 0),
                        "total_pages": rag_result.get("metadata", {}).get("total_pages", 0),
                    }
                }
            elif file.filename.lower().endswith(('.txt', '.doc', '.docx')):
                # Process text-based files
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        text_content = f.read()
                    
                    rag_pipeline = RAGPipeline()
                    rag_result = rag_pipeline.process_text_content(
                        text_content=text_content,
                        file_id=metadata.id,
                        source_filename=file.filename
                    )
                    
                    # Update RAG metadata
                    metadata.rag_metadata = {
                        "chunks_created": rag_result.get("total_chunks", 0),
                        "embeddings_added": rag_result.get("embeddings_added", 0),
                        "processing_status": rag_result.get("status", "completed"),
                        "details": {
                            "text_chunks": rag_result.get("text_chunks", 0),
                            "table_chunks": rag_result.get("table_chunks", 0),
                            "total_pages": rag_result.get("metadata", {}).get("total_pages", 0),
                        }
                    }
                except Exception as e:
                    print(f"Warning: Text content RAG processing failed: {str(e)}")
                    metadata.rag_metadata["processing_status"] = "failed"
                    metadata.rag_metadata["error"] = str(e)
        except Exception as e:
            # Log RAG error but don't fail the upload
            print(f"Warning: RAG processing failed for {file.filename}: {str(e)}")
            metadata.rag_metadata["processing_status"] = "failed"
            metadata.rag_metadata["error"] = str(e)
        
        return metadata
    
    @staticmethod
    def get_all_files() -> list[dict]:
        """Get all uploaded files metadata."""
        all_files = FileMetadata.get_all()
        return [f.to_dict() for f in all_files]
    
    @staticmethod
    def get_file_by_id(file_id: int) -> FileMetadata | None:
        """
        Get file metadata by ID.
        
        Args:
            file_id: The ID of the file to retrieve
            
        Returns:
            FileMetadata object or None if not found
        """
        return FileMetadata.get_by_id(file_id)
    
    @staticmethod
    def get_dashboard_metrics() -> dict:
        """Extract contract analysis KPIs from uploaded files."""
        all_files = FileMetadata.get_all()
        
        # Get KPIs from the most recently analyzed contract, or use defaults
        if all_files and all_files[-1].kpis:
            latest_kpis = all_files[-1].kpis
        else:
            # Initialize all KPIs as "Not Present" if no files exist
            latest_kpis = {
                "totalContractsProcessed": "Not Present",
                "contractType": "Not Present",
                "contractStatus": "Not Present",
                "complianceScore": "Not Present",
                "controlCoveragePercentage": "Not Present",
                "incidentReadinessScore": "Not Present",
                "highRiskIssuesCount": "Not Present",
                "openRisksCount": "Not Present",
                "averageTimeToRemediate": "Not Present",
                "totalContractValue": "Not Present",
                "revenueAtRisk": "Not Present",
                "totalObligationsExtracted": "Not Present",
                "obligationsCompletionRate": "Not Present",
                "upcomingExpirations": "Not Present",
                "averageProcessingTime": str(round(sum(f.processing_time for f in all_files) / len(all_files), 2)) + "s" if all_files else "Not Present",
                "clauseExtractionAccuracy": "Not Present",
                "dataResidencyCompliance": "Not Present",
                "encryptionCompliance": "Not Present",
                "mfaCoverage": "Not Present"
            }
        
        return {
            "kpis": latest_kpis,
            "contracts_processed_today": len(all_files)
        }

