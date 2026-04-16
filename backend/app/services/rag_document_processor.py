"""RAG document processor for PDF extraction and preparation."""
import pdfplumber
from pathlib import Path
from typing import List, Dict, Any


class ExtractedContent:
    """Container for extracted PDF content."""
    
    def __init__(self):
        self.pages: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
    
    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            "pages": self.pages,
            "metadata": self.metadata,
            "total_pages": len(self.pages),
            "total_text_chars": sum(len(p.get("text", "")) for p in self.pages),
            "total_tables": sum(len(p.get("tables", [])) for p in self.pages),
        }


class RAGDocumentProcessor:
    """
    Extract text and tables from PDFs for RAG preparation.
    
    Extracts:
    - Full text per page with page numbers
    - Tables with structure preservation
    - Metadata about sections and content locations
    """
    
    @staticmethod
    def extract_from_pdf(file_path: Path) -> ExtractedContent:
        """
        Extract text and tables from PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            ExtractedContent with pages and metadata
            
        Raises:
            ValueError: If PDF cannot be read
            FileNotFoundError: If file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        content = ExtractedContent()
        
        try:
            with pdfplumber.open(file_path) as pdf:
                content.metadata["total_pages"] = len(pdf.pages)
                content.metadata["source_file"] = file_path.name
                
                for page_num, page in enumerate(pdf.pages, 1):
                    page_data = {
                        "page_number": page_num,
                        "text": "",
                        "tables": [],
                        "table_count": 0,
                    }
                    
                    # Extract text
                    text = page.extract_text()
                    if text:
                        page_data["text"] = text
                        page_data["text_length"] = len(text)
                    
                    # Extract tables
                    tables = page.extract_tables()
                    if tables:
                        for table_idx, table in enumerate(tables):
                            table_data = {
                                "table_id": f"page_{page_num}_table_{table_idx}",
                                "rows": len(table),
                                "cols": len(table[0]) if table and len(table) > 0 else 0,
                                "data": table,
                                "bbox": page.find_table(table).bbox if hasattr(page, 'find_table') else None,
                            }
                            page_data["tables"].append(table_data)
                        page_data["table_count"] = len(tables)
                    
                    content.pages.append(page_data)
                
        except Exception as e:
            raise ValueError(f"Error extracting PDF: {str(e)}")
        
        return content
    
    @staticmethod
    def extract_text_only(file_path: Path) -> str:
        """
        Extract full text from PDF.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Full extracted text
        """
        content = RAGDocumentProcessor.extract_from_pdf(file_path)
        return "\n\n".join(page["text"] for page in content.pages if page["text"])
    
    @staticmethod
    def extract_has_tables(file_path: Path) -> bool:
        """Check if PDF contains tables."""
        content = RAGDocumentProcessor.extract_from_pdf(file_path)
        return any(page["table_count"] > 0 for page in content.pages)
