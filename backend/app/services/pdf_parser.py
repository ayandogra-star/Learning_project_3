"""PDF text extraction service for contract processing."""
from pathlib import Path
from pypdf import PdfReader


class PDFParser:
    """
    Production PDF parser for extracting text from contract documents.
    
    Handles multi-page PDFs and returns clean text for KPI extraction.
    """
    
    @staticmethod
    def extract_text(file_path: Path) -> str:
        """
        Extract text from a PDF file.
        
        Used by the backend after a PDF is uploaded to extract contract text
        which is then sent to the KPI extraction engine.
        
        Args:
            file_path: Path to the uploaded PDF file
            
        Returns:
            Extracted text from all pages of the PDF
            
        Raises:
            ValueError: If PDF cannot be read or parsed
        """
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"PDF file not found: {file_path}")
            
            reader = PdfReader(file_path)
            
            # Extract text from all pages
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                text += page_text + "\n"
            
            text = text.strip()
            
            if not text:
                raise ValueError("No text could be extracted from PDF - file may be image-only or corrupted")
            
            return text
            
        except FileNotFoundError as e:
            raise ValueError(f"PDF file not found: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing PDF: {str(e)}")
