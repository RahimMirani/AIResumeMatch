import pdfplumber
from typing import Dict, List, Any

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
                text = first_page.extract_text()
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                
                resume_data = {
                    "personal_info": self._extract_personal_info(lines[:3]),
                    "sections": self._extract_sections(lines[3:])
                }
                
                return resume_data
                
        except Exception as e:
            print(f"Error parsing PDF: {str(e)}")
            return self._get_empty_structure()

    def _get_empty_structure(self) -> Dict[str, Any]:
        return {
            "personal_info": {
                "name": "",
                "contact": {"email": "", "phone": "", "location": ""}
            },
            "sections": []
        }

    def _extract_personal_info(self, lines: List[str]) -> Dict[str, Any]:
        """Extract personal information from top of resume"""
        personal_info = {
            "name": "",
            "contact": {"email": "", "phone": "", "location": ""}
        }

        if not lines:
            return personal_info

        # First line is name
        personal_info["name"] = lines[0]

        # Second line contains contact info
        if len(lines) > 1:
            parts = [p.strip() for p in lines[1].split('|')]
            for part in parts:
                if '@' in part:
                    personal_info["contact"]["email"] = part
                elif any(c.isdigit() for c in part):
                    personal_info["contact"]["phone"] = part
                elif any(state in part for state in ['NC', 'TX']):
                    personal_info["contact"]["location"] = part

        return personal_info

    def _extract_sections(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract sections from resume"""
        sections = []
        current_section = None
        current_entry = None
        bullet_points = []

        for line in lines:
            # Check for section headers
            if line in self.section_headers:
                if current_section:
                    if current_entry and bullet_points:
                        current_entry["points"].extend(bullet_points)
                        bullet_points = []
                    if current_entry:
                        current_section["entries"].append(current_entry)
                    sections.append(current_section)
                
                current_section = {"title": line, "entries": []}
                current_entry = None
                continue

            if not current_section:
                continue

            # Handle company lines (contains location)
            if '|' in line and any(state in line for state in ['NC', 'TX']):
                if current_entry and bullet_points:
                    current_entry["points"].extend(bullet_points)
                    bullet_points = []
                if current_entry:
                    current_section["entries"].append(current_entry)

                parts = [p.strip() for p in line.split('|')]
                current_entry = {
                    "company": parts[0],
                    "location": parts[1] if len(parts) > 1 else "",
                    "duration": parts[2] if len(parts) > 2 else "",
                    "position": "",
                    "points": []
                }
                continue

            # Handle position line (follows company line)
            if current_entry and not current_entry["position"]:
                current_entry["position"] = line
                continue

            # Handle bullet points
            if line.startswith('•') or line.startswith('\uf0b7'):
                bullet_points.append(line.lstrip('•').lstrip('\uf0b7').strip())
            elif bullet_points:  # Continuation of previous bullet point
                bullet_points[-1] += ' ' + line

        # Add final section
        if current_section:
            if current_entry:
                if bullet_points:
                    current_entry["points"].extend(bullet_points)
                current_section["entries"].append(current_entry)
            sections.append(current_section)

        return sections

def parse_pdf(filepath: str) -> Dict[str, Any]:
    """Main function to parse PDF"""
    parser = ResumeParser()
    return parser.parse(filepath) 