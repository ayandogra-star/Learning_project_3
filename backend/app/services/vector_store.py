"""Vector store management using FAISS for RAG retrieval."""
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np


class VectorStore:
    """
    Manage vector embeddings using FAISS.
    
    Stores embeddings with metadata for similarity search and retrieval.
    """
    
    STORE_DIR = Path(__file__).parent.parent / "vector_store"
    
    def __init__(self):
        """Initialize vector store."""
        self.STORE_DIR.mkdir(exist_ok=True)
        self.index_path = self.STORE_DIR / "faiss.index"
        self.metadata_path = self.STORE_DIR / "metadata.json"
        self.index = None
        self.metadata = {}
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing index or create new one."""
        try:
            import faiss
            
            if self.index_path.exists() and self.metadata_path.exists():
                self.index = faiss.read_index(str(self.index_path))
                with open(self.metadata_path, "r") as f:
                    self.metadata = json.load(f)
            else:
                # Create empty index
                embedding_dim = 1536  # text-embedding-3-small dimension
                self.index = faiss.IndexFlatL2(embedding_dim)
                self.metadata = {
                    "chunks": {},
                    "file_mappings": {}
                }
        except Exception as e:
            raise ValueError(f"Error loading vector store: {str(e)}")
    
    def add_embeddings(self, embeddings_data: List[Dict[str, Any]], file_id: int) -> Dict[str, Any]:
        """
        Add embeddings to vector store.
        
        Args:
            embeddings_data: List of dicts with embedding vectors and metadata
            file_id: File ID for tracking
            
        Returns:
            Summary of added embeddings
        """
        try:
            import faiss
            
            if not embeddings_data:
                return {"added": 0, "file_id": file_id}
            
            # Extract embeddings as numpy array
            embeddings_array = np.array(
                [item["embedding"] for item in embeddings_data],
                dtype=np.float32
            )
            
            # Get starting index
            start_id = self.index.ntotal
            
            # Add to FAISS index
            self.index.add(embeddings_array)
            
            # Store metadata
            if str(file_id) not in self.metadata["file_mappings"]:
                self.metadata["file_mappings"][str(file_id)] = []
            
            chunk_ids = []
            for idx, item in enumerate(embeddings_data):
                vector_id = start_id + idx
                chunk_id = item["chunk_id"]
                
                self.metadata["chunks"][str(vector_id)] = {
                    "vector_id": vector_id,
                    "chunk_id": chunk_id,
                    "file_id": file_id,
                    "content": item.get("content", ""),  # Include actual content
                    "content_type": item.get("content_type", "text"),
                    "metadata": item.get("metadata", {}),
                    "content_length": item.get("content_length", 0),
                    "token_count": item.get("token_count", 0),
                }
                
                self.metadata["file_mappings"][str(file_id)].append({
                    "chunk_id": chunk_id,
                    "vector_id": vector_id
                })
                
                chunk_ids.append(chunk_id)
            
            # Save index and metadata
            self._save()
            
            return {
                "added": len(embeddings_data),
                "file_id": file_id,
                "chunk_ids": chunk_ids,
                "vector_ids": list(range(start_id, start_id + len(embeddings_data)))
            }
            
        except Exception as e:
            raise ValueError(f"Error adding embeddings: {str(e)}")
    
    def search(self, query_embedding: List[float], k: int = 5, file_id: int = None) -> List[Dict[str, Any]]:
        """
        Search for similar chunks with relevance boosting.
        
        Boosting rules:
        - Tables: 1.3x boost (highly structured content)
        - Definition sections: 1.5x boost
        - Security/compliance keywords: 1.5x boost
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            file_id: Optional file ID to filter by
            
        Returns:
            List of dicts with chunk metadata and similarity scores
        """
        try:
            if self.index.ntotal == 0:
                return []
            
            # Convert to numpy array
            query_array = np.array([query_embedding], dtype=np.float32)
            
            # Search FAISS index
            distances, indices = self.index.search(query_array, min(k * 2, self.index.ntotal))  # Get more to apply boosting
            
            results = []
            for distance, vector_id in zip(distances[0], indices[0]):
                vector_id = int(vector_id)
                vector_key = str(vector_id)
                
                if vector_key in self.metadata["chunks"]:
                    chunk_meta = self.metadata["chunks"][vector_key]
                    
                    # Filter by file_id if specified
                    if file_id and chunk_meta["file_id"] != file_id:
                        continue
                    
                    # Calculate base similarity score
                    base_similarity = 1 / (1 + float(distance))
                    
                    # Apply relevance boosting
                    boost_multiplier = self._get_relevance_boost(chunk_meta, query_embedding)
                    boosted_similarity = base_similarity * boost_multiplier
                    
                    results.append({
                        "vector_id": vector_id,
                        "chunk_id": chunk_meta["chunk_id"],
                        "file_id": chunk_meta["file_id"],
                        "similarity_distance": float(distance),
                        "similarity_score": base_similarity,
                        "boosted_similarity_score": boosted_similarity,
                        "boost_multiplier": boost_multiplier,
                        "metadata": chunk_meta.get("metadata", {}),
                        "content": chunk_meta.get("content", ""),  # Return full content for compliance analysis
                        "content_preview": chunk_meta.get("content", "")[:200],
                    })
            
            # Sort by boosted similarity score
            results.sort(key=lambda x: x["boosted_similarity_score"], reverse=True)
            
            return results[:k]
            
        except Exception as e:
            raise ValueError(f"Error searching vector store: {str(e)}")
    
    def _get_relevance_boost(self, chunk_meta: Dict[str, Any], query_embedding: List[float]) -> float:
        """
        Calculate relevance boost multiplier for a chunk.
        
        Boosting rules:
        - Tables: 1.3x (structured content is valuable)
        - Definition sections: 1.5x (Section 2-3 are key)
        - Security/compliance keywords: 1.5x
        - Query contains "definition|defined|means": 1.8x for def sections
        """
        boost = 1.0
        
        # Check content type
        content_type = chunk_meta.get("content_type", "")
        if content_type == "table":
            boost *= 1.3
        
        # Check if section is definitions-related
        section_title = chunk_meta.get("metadata", {}).get("section_title", "")
        if section_title:
            section_lower = section_title.lower()
            if any(kw in section_lower for kw in ["definition", "defined", "means", "glossary", "interpretation"]):
                boost *= 1.5
            # Prioritize section 2-3 (typically definitions)
            elif section_lower.startswith(("2.", "3.", "section 2", "section 3", "§2", "§3")):
                boost *= 1.4
        
        # Check for security/compliance keywords in metadata
        content = chunk_meta.get("content", "").lower()
        security_keywords = ["security", "compliance", "encryption", "mfa", "data residency", 
                           "breach", "incident", "liability", "confidential", "proprietary"]
        if any(kw in content for kw in security_keywords):
            boost *= 1.2
        
        # Cap boost at 2.0x
        return min(boost, 2.0)
    
    def get_file_chunks(self, file_id: int) -> List[Dict[str, Any]]:
        """Get all chunks for a file."""
        file_key = str(file_id)
        if file_key not in self.metadata["file_mappings"]:
            return []
        
        chunks = []
        for mapping in self.metadata["file_mappings"][file_key]:
            vector_key = str(mapping["vector_id"])
            if vector_key in self.metadata["chunks"]:
                chunks.append(self.metadata["chunks"][vector_key])
        
        return chunks
    
    def _save(self):
        """Save index and metadata to disk."""
        try:
            import faiss
            faiss.write_index(self.index, str(self.index_path))
            with open(self.metadata_path, "w") as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            raise ValueError(f"Error saving vector store: {str(e)}")
    
    def delete_file_embeddings(self, file_id: int):
        """Delete all embeddings for a file (advanced cleanup)."""
        file_key = str(file_id)
        if file_key in self.metadata["file_mappings"]:
            del self.metadata["file_mappings"][file_key]
            # Note: FAISS doesn't support deletion, so we flag as orphaned
            self._save()
