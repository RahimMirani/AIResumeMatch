import pdfplumber
from typing import Dict, List, Any
import re
from datetime import datetime

class ResumeParser:
    def __init__(self):
        self.section_headers = [
            'Professional Experience',
            'Education',
            'Skills',
            'Projects'
        ]

    def parse(self, pdf_path: str) -> Dict[str, Any]:
        """Main parsing function"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                first_page = pdf.pages[0]
                
                # Extract text directly
                text = first_page.extract_text()
                lines = text.split('\n')
                
                # Print debug info
                print("\n=== Extracted Lines ===")
                for i, line in enumerate(lines):
                    print(f"Line {i}: {line}")
                
                resume_data = {
                    "personal_info": self._extract_personal_info(lines[:3]),
                    "sections": self._extract_sections(lines[3:])
                }
                
                return resume_data
                
        except Exception as e:
            print(f"Error parsing PDF: {str(e)}")
            raise

    def _extract_personal_info(self, lines: List[str]) -> Dict[str, Any]:
        """Extract personal information from top of resume"""
        personal_info = {
            "name": "",
            "contact": {
                "email": "",
                "phone": "",
                "location": ""
            }
        }

        # First line is name
        if lines:
            personal_info["name"] = lines[0].strip()

        # Process contact info
        for line in lines[1:]:
            # Split by vertical bar if present
            parts = [p.strip() for p in line.split('|')]
            for part in parts:
                if '@' in part:
                    personal_info["contact"]["email"] = part
                elif any(c.isdigit() for c in part):
                    personal_info["contact"]["phone"] = part
                elif 'NC' in part or 'TX' in part:  # Location usually contains state
                    personal_info["contact"]["location"] = part

        return personal_info

    def _extract_sections(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract sections from resume"""
        sections = []
        current_section = None
        current_entry = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers
            if any(header in line for header in self.section_headers):
                if current_section:
                    if current_entry:
                        current_section["entries"].append(current_entry)
                    sections.append(current_section)
                current_section = {"title": line, "entries": []}
                current_entry = None
                continue
            
            # Process entries
            if current_section:
                # Check for company/location/date line
                if '|' in line and any(state in line for state in ['NC', 'TX']):
                    if current_entry:
                        current_section["entries"].append(current_entry)
                    
                    parts = line.split('|')
                    current_entry = {
                        "company": parts[0].strip(),
                        "location": parts[1].strip() if len(parts) > 1 else "",
                        "duration": parts[2].strip() if len(parts) > 2 else "",
                        "position": "",
                        "points": []
                    }
                # Check for position (usually follows company line)
                elif current_entry and not current_entry["position"]:
                    current_entry["position"] = line
                # Check for bullet points
                elif line.startswith('•') and current_entry:
                    current_entry["points"].append(line.lstrip('•').strip())
        
        # Add final section
        if current_section:
            if current_entry:
                current_section["entries"].append(current_entry)
            sections.append(current_section)
        
        return sections

def parse_pdf(filepath: str) -> Dict[str, Any]:
    """Main function to parse PDF"""
    parser = ResumeParser()
    return parser.parse(filepath) 