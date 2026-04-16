"""Embedding service for RAG chunks."""
import os
import json
from typing import List, Dict, Any
from app.services.semantic_chunker import RAGChunk


class EmbeddingService:
    """
    Generate embeddings for RAG chunks using OpenAI API.
    
    Uses the text-embedding-3-small model for efficient embeddings.
    """
    
    MODEL = "text-embedding-3-small"
    EMBEDDING_DIM = 1536  # Dimension of text-embedding-3-small
    
    @staticmethod
    def generate_embeddings(chunks: List[RAGChunk]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for a list of chunks.
        
        Args:
            chunks: List of RAGChunk objects
            
        Returns:
            List of dicts with chunk_id, embedding, and metadata
            
        Note:
            Uses OpenAI's text-embedding-3-small model
            Falls back to mock embeddings for testing if API keys not configured
        """
        try:
            from dotenv import load_dotenv
            
            load_dotenv()
            
            # Get OpenAI API key (try standard first, then Azure)
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                api_key = os.getenv("AZURE_OPENAI_API_KEY")
            
            embeddings_data = []
            
            if api_key and "OPENAI_API_KEY" in os.environ or "sk-" in (api_key or ""):
                # Use OpenAI API for real embeddings
                try:
                    from openai import OpenAI
                    client = OpenAI(api_key=api_key)
                    
                    # Generate embeddings
                    for chunk in chunks:
                        try:
                            response = client.embeddings.create(
                                input=chunk.content,
                                model="text-embedding-3-small",
                            )
                            embedding = response.data[0].embedding
                            
                            embeddings_data.append({
                                "chunk_id": chunk.chunk_id,
                                "embedding": embedding,
                                "content": chunk.content,
                                "content_type": chunk.content_type,
                                "metadata": chunk.to_dict()["metadata"],
                                "content_length": len(chunk.content),
                                "token_count": chunk.token_count,
                            })
                        except Exception as e:
                            print(f"Error generating embedding for {chunk.chunk_id}: {str(e)}")
                            continue
                except Exception as e:
                    print(f"Warning: Could not use OpenAI embeddings, falling back to mock: {str(e)}")
                    embeddings_data = []  # Fall through to mock embeddings
            
            # Fallback: Generate mock embeddings for testing
            if not embeddings_data:
                print("Using mock embeddings for testing (set OPENAI_API_KEY for real embeddings)")
                import hashlib
                import numpy as np
                
                for chunk in chunks:
                    # Generate deterministic mock embedding based on content
                    hash_obj = hashlib.md5(chunk.content.encode())
                    hash_int = int(hash_obj.hexdigest(), 16)
                    
                    # Create consistent 1536-dim vector from hash
                    np.random.seed(hash_int % (2**32))
                    embedding = np.random.randn(1536).tolist()
                    
                    embeddings_data.append({
                        "chunk_id": chunk.chunk_id,
                        "embedding": embedding,
                        "content": chunk.content,
                        "content_type": chunk.content_type,
                        "metadata": chunk.to_dict()["metadata"],
                        "content_length": len(chunk.content),
                        "token_count": chunk.token_count,
                    })
            
            return embeddings_data
            
        except Exception as e:
            raise ValueError(f"Error initializing embedding service: {str(e)}")
    
    @staticmethod
    def embed_single_query(query: str) -> List[float]:
        """
        Generate embedding for a single query string.
        
        Args:
            query: Query text
            
        Returns:
            Embedding vector
        """
        try:
            from dotenv import load_dotenv
            
            load_dotenv()
            
            # Get OpenAI API key (try standard first, then Azure)
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                api_key = os.getenv("AZURE_OPENAI_API_KEY")
            
            if api_key and "sk-" in api_key:
                # Use real OpenAI embeddings
                try:
                    from openai import OpenAI
                    client = OpenAI(api_key=api_key)
                    response = client.embeddings.create(
                        input=query,
                        model="text-embedding-3-small"
                    )
                    return response.data[0].embedding
                except Exception as e:
                    print(f"Warning: Could not embed query with OpenAI, using mock: {str(e)}")
            
            # Fallback: Generate mock embedding
            print("Using mock embedding for query")
            import hashlib
            import numpy as np
            
            hash_obj = hashlib.md5(query.encode())
            hash_int = int(hash_obj.hexdigest(), 16)
            
            # Create consistent 1536-dim vector from hash
            np.random.seed(hash_int % (2**32))
            embedding = np.random.randn(1536).tolist()
            return embedding
            
        except Exception as e:
            raise ValueError(f"Error embedding query: {str(e)}")
    
    @staticmethod
    def get_embedding_dimension() -> int:
        """Get embedding dimension."""
        return EmbeddingService.EMBEDDING_DIM
