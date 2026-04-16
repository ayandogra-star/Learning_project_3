"""Database models for the application."""
import json
from datetime import datetime
from pathlib import Path

METADATA_FILE = Path(__file__).parent.parent / "data" / "metadata.json"


class FileMetadata:
    """In-memory file metadata storage."""
    
    _storage = []
    
    def __init__(self, filename: str, file_size: int, upload_time: datetime, kpis: dict = None, rag_metadata: dict = None):
        self.id = len(self._storage) + 1
        self.filename = filename
        self.file_size = file_size
        self.upload_time = upload_time
        self.processing_time = 2.5  # Simulated processing time in seconds
        self.status = "completed"
        self.kpis = kpis or {}  # Store extracted KPIs
        self.rag_metadata = rag_metadata or {  # Track RAG processing
            "chunks_created": 0,
            "embeddings_added": 0,
            "processing_status": "pending"
        }
    
    @classmethod
    def add(cls, metadata: "FileMetadata") -> "FileMetadata":
        """Add metadata to storage."""
        cls._storage.append(metadata)
        return metadata
    
    @classmethod
    def get_all(cls) -> list["FileMetadata"]:
        """Get all file metadata."""
        return cls._storage
    
    @classmethod
    def get_by_id(cls, file_id: int) -> "FileMetadata | None":
        """Get metadata by ID."""
        for item in cls._storage:
            if item.id == file_id:
                return item
        return None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "filename": self.filename,
            "file_size": self.file_size,
            "upload_time": self.upload_time.isoformat(),
            "processing_time": self.processing_time,
            "status": self.status,
            "kpis": self.kpis,
            "rag_metadata": self.rag_metadata,
        }
