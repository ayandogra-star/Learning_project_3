"""RAG document processor for PDF extraction and preparation."""
import pdfplumber
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional


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


class TableMerger:
    """
    Merge tables that span multiple pages.
    
    Detects table continuations based on:
    - Similar header structure
    - Column alignment
    - Continuation patterns
    """
    
    @staticmethod
    def merge_multipage_tables(pages_with_tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge tables that span multiple pages.
        
        Args:
            pages_with_tables: List of page dicts with table data
            
        Returns:
            List of page dicts with merged table data
        """
        merged_pages = []
        pending_table = None
        
        for page_data in pages_with_tables:
            if not page_data.get("tables"):
                # No tables on this page
                if pending_table:
                    # Save the pending table
                    merged_pages.append(pending_table)
                    pending_table = None
                merged_pages.append(page_data)
                continue
            
            page_with_merged = page_data.copy()
            page_with_merged["tables"] = []
            
            for table_data in page_data["tables"]:
                if pending_table is None:
                    # Start new table
                    pending_table = {
                        "table_id": table_data.get("table_id"),
                        "start_page": page_data["page_number"],
                        "end_page": page_data["page_number"],
                        "rows": table_data.get("data", []),
                        "merged": False,
                    }
                else:
                    # Check if this table continues the pending one
                    if TableMerger._is_table_continuation(pending_table["rows"], table_data.get("data", [])):
                        # Merge tables
                        pending_table["rows"].extend(table_data.get("data", []))
                        pending_table["end_page"] = page_data["page_number"]
                        pending_table["merged"] = True
                        continue
                    else:
                        # Save pending table and start new one
                        page_with_merged["tables"].append(pending_table)
                        pending_table = {
                            "table_id": table_data.get("table_id"),
                            "start_page": page_data["page_number"],
                            "end_page": page_data["page_number"],
                            "rows": table_data.get("data", []),
                            "merged": False,
                        }
            
            merged_pages.append(page_with_merged)
        
        # Don't forget the last table
        if pending_table:
            if merged_pages:
                merged_pages[-1]["tables"].append(pending_table)
            else:
                merged_pages.append({"page_number": pending_table["start_page"], "tables": [pending_table]})
        
        return merged_pages
    
    @staticmethod
    def _is_table_continuation(prev_table: List[List[str]], curr_table: List[List[str]]) -> bool:
        """
        Check if current table continues the previous one.
        
        Heuristics:
        - Same number of columns
        - Similar header patterns
        - No major structural changes
        """
        if not prev_table or not curr_table:
            return False
        
        # Check column count consistency
        prev_cols = len(prev_table[0]) if prev_table else 0
        curr_cols = len(curr_table[0]) if curr_table else 0
        
        if prev_cols != curr_cols or prev_cols == 0:
            return False
        
        # Check if headers match (first row similarity)
        if len(prev_table) > 1 and len(curr_table) > 1:
            prev_first = [str(cell).strip().lower()[:20] for cell in prev_table[0]]
            curr_first = [str(cell).strip().lower()[:20] for cell in curr_table[0]]
            
            # If headers are identical, it's likely a continuation
            return prev_first == curr_first
        
        return False


class RAGDocumentProcessor:
    """
    Extract text and tables from PDFs for RAG preparation.
    
    Extracts:
    - Full text per page with page numbers
    - Tables with structure preservation
    - Merged multi-page tables
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
        pages_data = []
        
        try:
            with pdfplumber.open(file_path) as pdf:
                content.metadata["total_pages"] = len(pdf.pages)
                content.metadata["source_file"] = file_path.name
                
                # First pass: Extract all content
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
                            # Convert table to structured format
                            table_data = {
                                "table_id": f"page_{page_num}_table_{table_idx}",
                                "start_page": page_num,
                                "end_page": page_num,
                                "rows": len(table),
                                "cols": len(table[0]) if table and len(table) > 0 else 0,
                                "data": table,
                                "merged": False,
                            }
                            page_data["tables"].append(table_data)
                        page_data["table_count"] = len(tables)
                    
                    pages_data.append(page_data)
                
                # Second pass: Merge multi-page tables
                pages_without_tables = [p for p in pages_data if not p.get("tables")]
                pages_with_tables = [p for p in pages_data if p.get("tables")]
                
                # Apply merging logic
                if pages_with_tables:
                    merged_pages = TableMerger.merge_multipage_tables(pages_with_tables)
                    # Reconstruct full page list maintaining order
                    for page_data in pages_data:
                        for merged_page in merged_pages:
                            if merged_page.get("page_number") == page_data["page_number"]:
                                page_data["tables"] = merged_page.get("tables", [])
                                page_data["table_count"] = len(page_data["tables"])
                                break
                
                content.pages = pages_data
                
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
