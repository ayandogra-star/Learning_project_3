"""RAG pipeline orchestrator for document processing and retrieval."""
from pathlib import Path
from typing import List, Dict, Any
from app.services.rag_document_processor import RAGDocumentProcessor
from app.services.semantic_chunker import SemanticChunker
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore


class RAGPipeline:
    """
    Orchestrate the RAG pipeline:
    1. Extract content from PDF
    2. Create semantic chunks
    3. Generate embeddings
    4. Store in vector DB
    5. Enable retrieval
    """
    
    def __init__(self):
        """Initialize RAG pipeline."""
        self.vector_store = VectorStore()
    
    def process_document(self, file_path: Path, file_id: int, source_filename: str) -> Dict[str, Any]:
        """
        Process a document through the complete RAG pipeline.
        
        Args:
            file_path: Path to PDF file
            file_id: Unique file ID for tracking
            source_filename: Original filename
            
        Returns:
            Dict with:
            - chunks: List of created chunks
            - embeddings_added: Count of embeddings added to vector store
            - metadata: Processing metadata
        """
        try:
            # Step 1: Extract content from PDF
            extracted_content = RAGDocumentProcessor.extract_from_pdf(file_path)
            
            # Step 2: Create semantic chunks
            chunks = []
            chunk_counter = 0
            
            # Process text content by page
            for page_data in extracted_content.pages:
                page_num = page_data["page_number"]
                text_content = page_data.get("text", "").strip()
                
                if text_content:
                    page_chunks = SemanticChunker.chunk_text_content(
                        text=text_content,
                        page_number=page_num,
                        source_filename=source_filename,
                        chunk_id_prefix=f"file_{file_id}_p{page_num}",
                    )
                    chunks.extend(page_chunks)
                    chunk_counter += len(page_chunks)
                
                # Process tables on this page
                for table_data in page_data.get("tables", []):
                    table_id = table_data.get("table_id", f"file_{file_id}_table_{chunk_counter}")
                    table_chunk = SemanticChunker.chunk_table(
                        table_data=table_data.get("data", []),
                        page_number=page_num,
                        table_id=table_id,
                        source_filename=source_filename,
                    )
                    chunks.append(table_chunk)
                    chunk_counter += 1
            
            # Step 3: Generate embeddings for all chunks
            embeddings_data = EmbeddingService.generate_embeddings(chunks)
            
            # Step 4: Add embeddings to vector store
            add_result = self.vector_store.add_embeddings(embeddings_data, file_id)
            
            return {
                "file_id": file_id,
                "source_filename": source_filename,
                "total_chunks": len(chunks),
                "text_chunks": len([c for c in chunks if c.content_type == "text"]),
                "table_chunks": len([c for c in chunks if c.content_type == "table"]),
                "embeddings_added": add_result.get("added", 0),
                "chunks": [c.to_dict() for c in chunks[:5]],  # Return first 5 for preview
                "status": "completed",
                "metadata": {
                    "total_pages": extracted_content.metadata.get("total_pages"),
                    "total_text_chars": extracted_content.to_dict()["total_text_chars"],
                    "total_tables_found": extracted_content.to_dict()["total_tables"],
                }
            }
            
        except Exception as e:
            raise ValueError(f"Error processing document: {str(e)}")
    
    def process_text_content(self, text_content: str, file_id: int, source_filename: str) -> Dict[str, Any]:
        """
        Process text content through RAG pipeline (for .txt files).
        
        Args:
            text_content: Raw text content
            file_id: Unique file ID for tracking
            source_filename: Original filename
            
        Returns:
            Dict with processing results
        """
        try:
            # Step 1: Create semantic chunks from text (single page)
            chunks = SemanticChunker.chunk_text_content(
                text=text_content,
                page_number=1,
                source_filename=source_filename,
                chunk_id_prefix=f"file_{file_id}_p1",
            )
            
            if not chunks:
                return {
                    "file_id": file_id,
                    "source_filename": source_filename,
                    "total_chunks": 0,
                    "text_chunks": 0,
                    "table_chunks": 0,
                    "embeddings_added": 0,
                    "status": "completed",
                    "metadata": {
                        "total_pages": 1,
                        "total_text_chars": len(text_content),
                        "total_tables_found": 0,
                    }
                }
            
            # Step 2: Generate embeddings for all chunks
            embeddings_data = EmbeddingService.generate_embeddings(chunks)
            
            # Step 3: Add embeddings to vector store
            add_result = self.vector_store.add_embeddings(embeddings_data, file_id)
            
            return {
                "file_id": file_id,
                "source_filename": source_filename,
                "total_chunks": len(chunks),
                "text_chunks": len([c for c in chunks if c.content_type == "text"]),
                "table_chunks": len([c for c in chunks if c.content_type == "table"]),
                "embeddings_added": add_result.get("added", 0),
                "chunks": [c.to_dict() for c in chunks[:5]],  # Return first 5 for preview
                "status": "completed",
                "metadata": {
                    "total_pages": 1,
                    "total_text_chars": len(text_content),
                    "total_tables_found": 0,
                }
            }
            
        except Exception as e:
            raise ValueError(f"Error processing text content: {str(e)}")
    
    def retrieve_chunks(self, query: str, file_id: int = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks based on query.
        
        Args:
            query: Query text
            file_id: Optional file ID to filter by
            top_k: Number of results to return
            
        Returns:
            List of relevant chunks with metadata
        """
        try:
            # Generate embedding for query
            query_embedding = EmbeddingService.embed_single_query(query)
            
            # Search vector store
            results = self.vector_store.search(query_embedding, k=top_k, file_id=file_id)
            
            return results
            
        except Exception as e:
            raise ValueError(f"Error retrieving chunks: {str(e)}")
    
    def get_file_chunks(self, file_id: int) -> List[Dict[str, Any]]:
        """Get all chunks for a file."""
        return self.vector_store.get_file_chunks(file_id)
