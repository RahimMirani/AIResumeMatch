from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError
import re

def clean_text(text):
    """Clean and structure the extracted text."""
    # Remove excessive whitespace while preserving important line breaks
    text = re.sub(r'\s*\n\s*\n\s*', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    
    # Try to identify sections (common resume section titles)
    section_patterns = [
        r'EDUCATION[:\s]',
        r'EXPERIENCE[:\s]',
        r'SKILLS[:\s]',
        r'PROJECTS[:\s]',
        r'WORK EXPERIENCE[:\s]',
        r'PROFESSIONAL EXPERIENCE[:\s]',
        r'CERTIFICATIONS[:\s]',
        r'ACHIEVEMENTS[:\s]',
        r'SUMMARY[:\s]',
        r'OBJECTIVE[:\s]'
    ]
    
    # Add section markers
    for pattern in section_patterns:
        text = re.sub(f'({pattern})', r'\n\n\1\n', text, flags=re.IGNORECASE)
    
    # Process the text line by line
    lines = text.split('\n')
    formatted_lines = []
    current_section = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this line is a section header
        is_section = any(re.match(pattern, line, re.IGNORECASE) for pattern in section_patterns)
        
        if is_section:
            current_section = line
            formatted_lines.append(f"\n{line}")
            formatted_lines.append("=" * len(line))
        else:
            # Check if line starts with a bullet point or could be a bullet point
            if line.startswith('•'):
                formatted_lines.append(line)
            elif line.startswith('-'):
                formatted_lines.append(f"• {line[1:].strip()}")
            elif re.match(r'^\d+\.', line):
                formatted_lines.append(f"• {line}")
            else:
                # If line is short, it might be a header
                if len(line) < 50 and line.isupper():
                    formatted_lines.append(f"\n{line}")
                else:
                    formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def parse_pdf(file_path):
    """
    Parse a PDF file and extract its text content with improved formatting.
    
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
        
        # Clean and structure the text
        formatted_text = clean_text(text)
        
        # Add some spacing for better readability
        formatted_text = f"\n{formatted_text.strip()}\n"
        
        return formatted_text
    
    except PDFSyntaxError:
        raise Exception("Invalid or corrupted PDF file")
    except FileNotFoundError:
        raise Exception("File not found")
    except Exception as e:
        raise Exception(f"Error parsing PDF: {str(e)}") 