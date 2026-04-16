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
        Search for similar chunks.
        
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
            distances, indices = self.index.search(query_array, min(k, self.index.ntotal))
            
            results = []
            for distance, vector_id in zip(distances[0], indices[0]):
                vector_id = int(vector_id)
                vector_key = str(vector_id)
                
                if vector_key in self.metadata["chunks"]:
                    chunk_meta = self.metadata["chunks"][vector_key]
                    
                    # Filter by file_id if specified
                    if file_id and chunk_meta["file_id"] != file_id:
                        continue
                    
                    results.append({
                        "vector_id": vector_id,
                        "chunk_id": chunk_meta["chunk_id"],
                        "file_id": chunk_meta["file_id"],
                        "similarity_distance": float(distance),
                        "similarity_score": 1 / (1 + float(distance)),  # Convert distance to similarity
                        "metadata": chunk_meta.get("metadata", {}),
                    })
            
            return results[:k]
            
        except Exception as e:
            raise ValueError(f"Error searching vector store: {str(e)}")
    
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
