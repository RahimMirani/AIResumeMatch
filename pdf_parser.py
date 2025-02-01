from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError

def parse_pdf(file_path):
    """
    Parse a PDF file and extract its text content.
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
        
    Raises:
        PDFSyntaxError: If the PDF is invalid or corrupted
        FileNotFoundError: If the file doesn't exist
    """
    try:
        # Extract text from PDF
        text = extract_text(file_path)
        
        # Basic text cleaning
        text = text.strip()
        # Remove multiple newlines
        text = '\n'.join(line.strip() for line in text.splitlines() if line.strip())
        
        return text
    
    except PDFSyntaxError:
        raise Exception("Invalid or corrupted PDF file")
    except FileNotFoundError:
        raise Exception("File not found")
    except Exception as e:
        raise Exception(f"Error parsing PDF: {str(e)}") 