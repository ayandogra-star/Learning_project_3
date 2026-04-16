"""Semantic chunking for RAG preparation."""
import re
import tiktoken
from typing import List, Dict, Any


class RAGChunk:
    """Semantic chunk for RAG with metadata."""
    
    def __init__(
        self,
        chunk_id: str,
        content: str,
        page_number: int,
        section_title: str = None,
        content_type: str = "text",
        source_filename: str = None,
        char_range: tuple = None,
        token_count: int = None,
    ):
        self.chunk_id = chunk_id
        self.content = content
        self.page_number = page_number
        self.section_title = section_title
        self.content_type = content_type  # "text" or "table"
        self.source_filename = source_filename
        self.char_range = char_range  # (start, end) character positions
        self.token_count = token_count or self.count_tokens(content)
        self.embedding = None  # To be filled by EmbeddingService
    
    @staticmethod
    def count_tokens(text: str) -> int:
        """Count tokens in text using tiktoken."""
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except:
            # Fallback: rough estimate (1 token ≈ 4 chars)
            return len(text) // 4
    
    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "page_number": self.page_number,
            "section_title": self.section_title,
            "content_type": self.content_type,
            "source_filename": self.source_filename,
            "char_range": self.char_range,
            "token_count": self.token_count,
            "metadata": {
                "chunk_id": self.chunk_id,
                "page_number": self.page_number,
                "section_title": self.section_title,
                "content_type": self.content_type,
                "source_filename": self.source_filename,
            }
        }


class SemanticChunker:
    """
    Split extracted content into semantic chunks for RAG.
    
    Rules:
    - Preserve logical sections (headings, numbered sections)
    - Keep tables intact
    - Target chunk size: 300-800 tokens
    - Preserve metadata for traceability
    """
    
    MIN_CHUNK_TOKENS = 300
    MAX_CHUNK_TOKENS = 800
    HEADING_PATTERN = re.compile(r"^(#{1,6}\s+|[A-Z][A-Z\s]+:|^\d+\.\s+|^[A-Z][A-Z0-9\s]*:?$)", re.MULTILINE)
    
    @staticmethod
    def chunk_text_content(
        text: str,
        page_number: int,
        source_filename: str,
        chunk_id_prefix: str = "chunk",
    ) -> List[RAGChunk]:
        """
        Chunk text content semantically.
        
        Args:
            text: Text content to chunk
            page_number: Page number source
            source_filename: Source PDF filename
            chunk_id_prefix: Prefix for chunk IDs
            
        Returns:
            List of RAGChunk objects
        """
        chunks = []
        chunk_counter = 0
        
        # Split by headings first
        sections = SemanticChunker._split_by_headings(text)
        
        for section_title, section_content in sections:
            # Further split by paragraphs if needed
            if RAGChunk.count_tokens(section_content) > SemanticChunker.MAX_CHUNK_TOKENS:
                sub_chunks = SemanticChunker._split_by_paragraphs(
                    section_content,
                    page_number,
                    source_filename,
                    section_title,
                    chunk_counter,
                    chunk_id_prefix,
                )
                chunks.extend(sub_chunks)
                chunk_counter += len(sub_chunks)
            else:
                # Single chunk for this section
                chunk_id = f"{chunk_id_prefix}_{chunk_counter}"
                chunk = RAGChunk(
                    chunk_id=chunk_id,
                    content=section_content,
                    page_number=page_number,
                    section_title=section_title,
                    content_type="text",
                    source_filename=source_filename,
                    char_range=(0, len(section_content)),
                )
                chunks.append(chunk)
                chunk_counter += 1
        
        return chunks
    
    @staticmethod
    def chunk_table(
        table_data: List[List[str]],
        page_number: int,
        table_id: str,
        source_filename: str,
    ) -> RAGChunk:
        """
        Create a chunk for a table (keep intact).
        
        Args:
            table_data: Table rows/columns
            page_number: Page number
            table_id: Table identifier
            source_filename: Source PDF filename
            
        Returns:
            RAGChunk representing the table
        """
        # Format table as structured text
        table_text = SemanticChunker._format_table_as_text(table_data)
        
        chunk = RAGChunk(
            chunk_id=table_id,
            content=table_text,
            page_number=page_number,
            section_title=f"Table: {table_id}",
            content_type="table",
            source_filename=source_filename,
        )
        return chunk
    
    @staticmethod
    def _split_by_headings(text: str) -> List[tuple]:
        """
        Split text by detected headings.
        
        Returns:
            List of (section_title, section_content) tuples
        """
        sections = []
        current_heading = None
        current_content = []
        
        for line in text.split("\n"):
            if SemanticChunker.HEADING_PATTERN.match(line.strip()):
                # Found a heading
                if current_content:
                    section_text = "\n".join(current_content).strip()
                    if section_text:
                        sections.append((current_heading, section_text))
                current_heading = line.strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Add last section
        if current_content:
            section_text = "\n".join(current_content).strip()
            if section_text:
                sections.append((current_heading, section_text))
        
        return sections if sections else [("Content", text)]
    
    @staticmethod
    def _split_by_paragraphs(
        text: str,
        page_number: int,
        source_filename: str,
        section_title: str,
        chunk_counter: int,
        chunk_id_prefix: str,
    ) -> List[RAGChunk]:
        """Split section into smaller chunks by paragraphs."""
        chunks = []
        paragraphs = text.split("\n\n")
        current_chunk = []
        current_tokens = 0
        chunk_id = f"{chunk_id_prefix}_{chunk_counter}"
        
        for para in paragraphs:
            para_tokens = RAGChunk.count_tokens(para)
            
            if current_tokens + para_tokens > SemanticChunker.MAX_CHUNK_TOKENS and current_chunk:
                # Finalize current chunk
                chunk_text = "\n\n".join(current_chunk)
                chunk = RAGChunk(
                    chunk_id=chunk_id,
                    content=chunk_text,
                    page_number=page_number,
                    section_title=section_title,
                    content_type="text",
                    source_filename=source_filename,
                )
                chunks.append(chunk)
                
                # Start new chunk
                chunk_counter += 1
                chunk_id = f"{chunk_id_prefix}_{chunk_counter}"
                current_chunk = [para]
                current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens
        
        # Finalize last chunk
        if current_chunk:
            chunk_text = "\n\n".join(current_chunk)
            chunk = RAGChunk(
                chunk_id=chunk_id,
                content=chunk_text,
                page_number=page_number,
                section_title=section_title,
                content_type="text",
                source_filename=source_filename,
            )
            chunks.append(chunk)
        
        return chunks
    
    @staticmethod
    def _format_table_as_text(table_data: List[List[str]]) -> str:
        """Format table as readable text for embedding."""
        if not table_data:
            return ""
        
        lines = []
        for row in table_data:
            line = " | ".join(str(cell).strip() if cell else "" for cell in row)
            lines.append(line)
        
        return "\n".join(lines)
