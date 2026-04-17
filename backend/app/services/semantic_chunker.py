"""Semantic chunking for RAG preparation."""
import re
import tiktoken
from typing import List, Dict, Any


class TableFormatter:
    """Convert table data to readable text format for embeddings."""
    
    @staticmethod
    def format_table_to_text(table_data: List[List[str]], table_id: str = "") -> str:
        """
        Convert table to readable text format.
        
        Example:
            Input:  [['Name', 'Value'], ['Security', 'AES-256'], ['MFA', 'Enabled']]
            Output: "Table {table_id}:\n* Name: Value\n* Security: AES-256\n* MFA: Enabled"
        
        Args:
            table_data: Table rows/columns (2D list)
            table_id: Optional table identifier
            
        Returns:
            Formatted text representation of table
        """
        if not table_data or not table_data[0]:
            return ""
        
        formatted_parts = []
        if table_id:
            formatted_parts.append(f"Table: {table_id}\n")
        
        # Detect if it's a key-value table (2 columns)
        if len(table_data[0]) == 2:
            # Key-value format
            for row_idx, row in enumerate(table_data):
                if row_idx == 0:
                    # Skip header row
                    continue
                key = str(row[0]).strip() if row[0] else ""
                value = str(row[1]).strip() if len(row) > 1 and row[1] else ""
                
                if key:
                    formatted_parts.append(f"* {key}: {value}")
        else:
            # Multi-column table - convert to readable format
            headers = [str(h).strip() for h in table_data[0]] if table_data else []
            
            for row_idx, row in enumerate(table_data[1:], 1):
                row_lines = [f"Row {row_idx}:"]
                for col_idx, cell in enumerate(row):
                    header = headers[col_idx] if col_idx < len(headers) else f"Col{col_idx}"
                    cell_text = str(cell).strip() if cell else ""
                    if cell_text:
                        row_lines.append(f"  {header}: {cell_text}")
                formatted_parts.append("\n".join(row_lines))
        
        return "\n".join(formatted_parts)
    
    @staticmethod
    def extract_table_keywords(table_data: List[List[str]]) -> List[str]:
        """
        Extract keywords from table for relevance boosting.
        
        Args:
            table_data: Table data
            
        Returns:
            List of key terms in table
        """
        keywords = []
        for row in table_data:
            for cell in row:
                text = str(cell).strip().lower()
                if text and len(text) > 3:
                    keywords.extend(text.split())
        
        return list(set(keywords))[:20]  # Return top 20 unique keywords


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
        self.relevance_boost = 1.0  # For retrieval boosting
    
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
    - Keep tables intact (never split across chunks)
    - Handle multi-page tables
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
                
                # Apply boosting for definition sections
                if SemanticChunker._is_definition_section(section_title, section_content):
                    chunk.relevance_boost = 1.5
                
                chunks.append(chunk)
                chunk_counter += 1
        
        return chunks
    
    @staticmethod
    def chunk_table(
        table_data: List[List[str]],
        page_number: int,
        table_id: str,
        source_filename: str,
        page_range: tuple = None,
    ) -> RAGChunk:
        """
        Create a chunk for a table (keep intact, never split).
        
        Args:
            table_data: Table rows/columns
            page_number: Page number (or start page if multi-page)
            table_id: Table identifier
            source_filename: Source PDF filename
            page_range: Optional (start_page, end_page) tuple for multi-page tables
            
        Returns:
            RAGChunk representing the table
        """
        # Format table to readable text
        formatted_text = TableFormatter.format_table_to_text(table_data, table_id)
        
        chunk = RAGChunk(
            chunk_id=table_id,
            content=formatted_text,
            page_number=page_number,
            section_title=f"Table: {table_id}",
            content_type="table",
            source_filename=source_filename,
            char_range=(0, len(formatted_text)),
        )
        
        # Tables get relevance boost - they're important
        chunk.relevance_boost = 1.3
        
        # Additional boost if table contains security or compliance keywords
        keywords = TableFormatter.extract_table_keywords(table_data)
        if any(kw in ' '.join(keywords).lower() for kw in ['security', 'compliance', 'encrypt', 'mfa', 'data']):
            chunk.relevance_boost = 1.5
        
        return chunk
    
    @staticmethod
    def _split_by_headings(text: str) -> List[tuple]:
        """
        Split text by section headings.
        
        Returns list of (section_title, section_content) tuples.
        """
        sections = []
        current_section = None
        current_content = []
        
        lines = text.split('\n')
        
        for line in lines:
            # Check if line is a heading
            if SemanticChunker.HEADING_PATTERN.match(line.strip()) and len(line.strip()) < 100:
                # Save previous section
                if current_section is not None:
                    sections.append((current_section, '\n'.join(current_content).strip()))
                
                current_section = line.strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Don't forget last section
        if current_section is not None:
            sections.append((current_section, '\n'.join(current_content).strip()))
        elif current_content:
            sections.append(("", '\n'.join(current_content).strip()))
        
        # Filter empty sections
        return [(title, content) for title, content in sections if content.strip()]
    
    @staticmethod
    def _split_by_paragraphs(
        text: str,
        page_number: int,
        source_filename: str,
        section_title: str,
        start_counter: int,
        chunk_id_prefix: str,
    ) -> List[RAGChunk]:
        """Split section by paragraphs if it's too large."""
        chunks = []
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        current_chunk_content = []
        current_token_count = 0
        chunk_counter = start_counter
        
        for para in paragraphs:
            para_tokens = RAGChunk.count_tokens(para)
            
            # Check if adding this paragraph would exceed max tokens
            if current_token_count + para_tokens > SemanticChunker.MAX_CHUNK_TOKENS and current_chunk_content:
                # Save current chunk
                chunk_id = f"{chunk_id_prefix}_{chunk_counter}"
                chunk_content = '\n\n'.join(current_chunk_content)
                chunk = RAGChunk(
                    chunk_id=chunk_id,
                    content=chunk_content,
                    page_number=page_number,
                    section_title=section_title,
                    content_type="text",
                    source_filename=source_filename,
                )
                chunks.append(chunk)
                chunk_counter += 1
                
                # Reset for next chunk
                current_chunk_content = [para]
                current_token_count = para_tokens
            else:
                # Add to current chunk
                current_chunk_content.append(para)
                current_token_count += para_tokens
        
        # Don't forget last chunk
        if current_chunk_content:
            chunk_id = f"{chunk_id_prefix}_{chunk_counter}"
            chunk_content = '\n\n'.join(current_chunk_content)
            chunk = RAGChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                page_number=page_number,
                section_title=section_title,
                content_type="text",
                source_filename=source_filename,
            )
            chunks.append(chunk)
        
        return chunks
    
    @staticmethod
    def _is_definition_section(section_title: str, content: str) -> bool:
        """Check if section is likely a definitions section (for relevance boosting)."""
        definition_keywords = ['definition', 'defined', 'means', 'interpretation', 'glossary']
        section_lower = section_title.lower() if section_title else ""
        content_lower = content[:200].lower() if content else ""
        
        # Boost if section title contains definition keywords
        if any(kw in section_lower for kw in definition_keywords):
            return True
        
        # Boost if section number is 2 or 3 (typically definitions)
        if section_lower.startswith(('2.', '3.', '§2', '§3')):
            return True
        
        return False
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
