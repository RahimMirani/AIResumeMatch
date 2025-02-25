import pdfplumber
from typing import Dict, List, Any
import re

class ResumeParser:
    def __init__(self):
        self.section_headers = [
            'EDUCATION',
            'EXPERIENCE',
            'SKILLS',
            'PROJECTS',
            'PROFESSIONAL EXPERIENCE'
        ]

    def parse(self, pdf_path: str) -> Dict[str, Any]:
        """Main parsing function"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                first_page = pdf.pages[0]
                text = first_page.extract_text()
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                
                # Find the name (usually the first line)
                name = lines[0] if lines else ""
                
                # Extract contact info (usually in the first few lines)
                contact_info = self._extract_contact_info(lines[:5])
                
                # Find section boundaries
                sections = self._extract_sections(lines)
                
                resume_data = {
                    "personal_info": {
                        "name": name,
                        "contact": contact_info
                    },
                    "sections": sections
                }
                
                return resume_data
                
        except Exception as e:
            print(f"Error parsing PDF: {str(e)}")
            return self._get_empty_structure()

    def _get_empty_structure(self) -> Dict[str, Any]:
        return {
            "personal_info": {
                "name": "",
                "contact": {"email": "", "phone": "", "location": "", "linkedin": "", "github": ""}
            },
            "sections": []
        }

    def _extract_contact_info(self, lines: List[str]) -> Dict[str, str]:
        """Extract contact information from top of resume"""
        contact_info = {
            "email": "",
            "phone": "",
            "location": "",
            "linkedin": "",
            "github": ""
        }

        # Join lines to handle contact info that might be spread across multiple lines
        contact_text = " ".join(lines)
        
        # Extract email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+', contact_text)
        if email_match:
            contact_info["email"] = email_match.group(0)
        
        # Extract phone
        phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', contact_text)
        if phone_match:
            contact_info["phone"] = phone_match.group(0)
        
        # Extract location (common city/state formats)
        location_match = re.search(r'([A-Za-z\s]+),\s*([A-Z]{2})', contact_text)
        if location_match:
            contact_info["location"] = location_match.group(0)
        
        # Extract LinkedIn
        linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', contact_text)
        if linkedin_match:
            contact_info["linkedin"] = linkedin_match.group(0)
        
        # Extract GitHub
        github_match = re.search(r'github\.com/[\w-]+', contact_text)
        if github_match:
            contact_info["github"] = github_match.group(0)

        return contact_info

    def _extract_sections(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract sections from resume"""
        sections = []
        current_section = None
        section_content = []
        
        # Find section boundaries
        for i, line in enumerate(lines):
            # Check if line is a section header
            if any(header in line.upper() for header in self.section_headers):
                # Save previous section if exists
                if current_section and section_content:
                    sections.append({
                        "title": current_section,
                        "entries": self._parse_section_content(current_section, section_content)
                    })
                
                # Start new section
                current_section = line
                section_content = []
            elif current_section:
                section_content.append(line)
        
        # Add final section
        if current_section and section_content:
            sections.append({
                "title": current_section,
                "entries": self._parse_section_content(current_section, section_content)
            })
        
        return sections

    def _parse_section_content(self, section_title: str, content: List[str]) -> List[Dict[str, Any]]:
        """Parse content of a section based on its type"""
        if "EDUCATION" in section_title.upper():
            return self._parse_education(content)
        elif "EXPERIENCE" in section_title.upper():
            return self._parse_experience(content)
        elif "SKILLS" in section_title.upper():
            return self._parse_skills(content)
        else:
            return self._parse_generic_section(content)

    def _parse_education(self, content: List[str]) -> List[Dict[str, Any]]:
        """Parse education section"""
        entries = []
        current_entry = None
        
        for line in content:
            # Check if line is a university/school name
            if re.search(r'University|College|School', line):
                if current_entry:
                    entries.append(current_entry)
                
                # Extract location if present
                location_match = re.search(r'([A-Za-z\s]+),\s*([A-Z]{2})', line)
                location = location_match.group(0) if location_match else ""
                
                # Remove location from school name if present
                school = line
                if location:
                    school = line.replace(location, "").strip()
                
                current_entry = {
                    "company": school,
                    "location": location,
                    "position": "",
                    "duration": "",
                    "points": []
                }
            elif current_entry:
                # Check if line contains a degree
                if "Bachelor" in line or "Master" in line or "Associate" in line or "Degree" in line:
                    current_entry["position"] = line
                # Check if line contains dates
                elif re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}', line):
                    current_entry["duration"] = line
                # Otherwise, add as bullet point
                elif line.startswith('•'):
                    current_entry["points"].append(line.lstrip('•').strip())
        
        # Add final entry
        if current_entry:
            entries.append(current_entry)
        
        return entries

    def _parse_experience(self, content: List[str]) -> List[Dict[str, Any]]:
        """Parse experience section"""
        entries = []
        current_entry = None
        bullet_points = []
        
        for line in content:
            # Check if line is a company name (often followed by location)
            if re.search(r'([A-Za-z\s]+),\s*([A-Z]{2})', line) and not line.startswith('•'):
                # Save previous entry
                if current_entry:
                    if bullet_points:
                        current_entry["points"] = bullet_points
                    entries.append(current_entry)
                    bullet_points = []
                
                # Extract location
                location_match = re.search(r'([A-Za-z\s]+),\s*([A-Z]{2})', line)
                location = location_match.group(0) if location_match else ""
                
                # Extract company name
                company = line
                if location:
                    company = line.replace(location, "").strip()
                
                current_entry = {
                    "company": company,
                    "location": location,
                    "position": "",
                    "duration": "",
                    "points": []
                }
            # Check if line contains a job title
            elif current_entry and not current_entry["position"] and not line.startswith('•'):
                # Check if line contains dates
                date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}', line)
                if date_match:
                    current_entry["duration"] = line
                else:
                    current_entry["position"] = line
            # Check if line is a bullet point
            elif line.startswith('•'):
                bullet_points.append(line.lstrip('•').strip())
            # Check if line is a date range
            elif current_entry and re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}', line):
                current_entry["duration"] = line
        
        # Add final entry
        if current_entry:
            if bullet_points:
                current_entry["points"] = bullet_points
            entries.append(current_entry)
        
        return entries

    def _parse_skills(self, content: List[str]) -> List[Dict[str, Any]]:
        """Parse skills section"""
        # For skills, we'll create a single entry with bullet points
        skills_entry = {
            "company": "Technical Skills",
            "position": "",
            "location": "",
            "duration": "",
            "points": []
        }
        
        for line in content:
            if line.startswith('•'):
                skills_entry["points"].append(line.lstrip('•').strip())
            else:
                # If not a bullet point, add the whole line as a skill
                skills_entry["points"].append(line)
        
        return [skills_entry]

    def _parse_generic_section(self, content: List[str]) -> List[Dict[str, Any]]:
        """Parse any other section type"""
        # For generic sections, create a single entry
        entry = {
            "company": "",
            "position": "",
            "location": "",
            "duration": "",
            "points": []
        }
        
        for line in content:
            if line.startswith('•'):
                entry["points"].append(line.lstrip('•').strip())
            else:
                # If not a bullet point, add as a separate point
                entry["points"].append(line)
        
        return [entry]

def parse_pdf(filepath: str) -> Dict[str, Any]:
    """Main function to parse PDF"""
    parser = ResumeParser()
    return parser.parse(filepath) 