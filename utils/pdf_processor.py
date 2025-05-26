"""
PDF processing utilities for converting PDF pages to images.
"""
import fitz  # PyMuPDF
import base64
import io
from PIL import Image
from typing import List, Tuple, Optional
import logging
from pathlib import Path

from config import PROCESSING_CONFIG

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Handles PDF to image conversion and processing."""
    
    def __init__(self, dpi: int = None, image_format: str = None):
        """
        Initialize PDF processor.
        
        Args:
            dpi: Resolution for image conversion
            image_format: Output image format (PNG, JPEG)
        """
        self.dpi = dpi or PROCESSING_CONFIG.pdf_dpi
        self.image_format = image_format or PROCESSING_CONFIG.image_format
        
    def pdf_to_images(self, pdf_path: str) -> List[Tuple[int, str]]:
        """
        Convert PDF pages to base64 encoded images.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of tuples (page_number, base64_image)
        """
        try:
            doc = fitz.open(pdf_path)
            images = []
            
            logger.info(f"Processing PDF with {len(doc)} pages")
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Convert page to image
                mat = fitz.Matrix(self.dpi/72, self.dpi/72)  # Scale factor for DPI
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format=self.image_format)
                img_base64 = base64.b64encode(buffer.getvalue()).decode()
                
                images.append((page_num + 1, f"data:image/{self.image_format.lower()};base64,{img_base64}"))
                
                logger.info(f"Processed page {page_num + 1}")
                
            doc.close()
            return images
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            raise
    
    def get_pdf_info(self, pdf_path: str) -> dict:
        """
        Get basic information about the PDF.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with PDF metadata
        """
        try:
            doc = fitz.open(pdf_path)
            info = {
                "page_count": len(doc),
                "metadata": doc.metadata,
                "file_size": Path(pdf_path).stat().st_size
            }
            doc.close()
            return info
            
        except Exception as e:
            logger.error(f"Error getting PDF info for {pdf_path}: {str(e)}")
            raise
    
    def validate_pdf(self, pdf_path: str) -> bool:
        """
        Validate if the file is a valid PDF.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            True if valid PDF, False otherwise
        """
        try:
            doc = fitz.open(pdf_path)
            is_valid = len(doc) > 0
            doc.close()
            return is_valid
            
        except Exception as e:
            logger.warning(f"PDF validation failed for {pdf_path}: {str(e)}")
            return False

def process_uploaded_pdf(uploaded_file) -> Tuple[List[Tuple[int, str]], dict]:
    """
    Process an uploaded PDF file from Streamlit.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        Tuple of (images_list, pdf_info)
    """
    # Save uploaded file temporarily
    temp_path = f"temp_{uploaded_file.name}"
    
    try:
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        processor = PDFProcessor()
        
        # Validate PDF
        if not processor.validate_pdf(temp_path):
            raise ValueError("Invalid PDF file")
        
        # Get PDF info
        pdf_info = processor.get_pdf_info(temp_path)
        
        # Convert to images
        images = processor.pdf_to_images(temp_path)
        
        return images, pdf_info
        
    finally:
        # Clean up temporary file
        if Path(temp_path).exists():
            Path(temp_path).unlink()
