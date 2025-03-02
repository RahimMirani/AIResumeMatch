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
        # Expanded bullet point patterns
        self.bullet_patterns = [
            r'^\s*•\s+',  # Standard bullet
            r'^\s*-\s+',  # Dash bullet
            r'^\s*\*\s+', # Asterisk bullet
            r'^\s*\u2022\s+',  # Unicode bullet
            r'^\s*\u2023\s+',  # Triangle bullet
            r'^\s*\u25E6\s+',  # White bullet
            r'^\s*\u25AA\s+',  # Black small square
            r'^\s*\d+\.\s+',   # Numbered list (1. 2. etc)
            r'^\s*\[\s*\d+\s*\]\s+',  # [1] style
            r'^\s*o\s+'    # 'o' as bullet
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

    def _is_bullet_point(self, line: str) -> bool:
        """Check if a line is a bullet point using various patterns"""
        for pattern in self.bullet_patterns:
            if re.match(pattern, line):
                return True
        
        # Special case for indented lines that might be continuation of bullets
        if line.startswith('    ') and len(line) > 5:
            return True
            
        return False
    
    def _clean_bullet_point(self, line: str) -> str:
        """Remove bullet point marker and clean the text"""
        for pattern in self.bullet_patterns:
            line = re.sub(pattern, '', line)
        return line.strip()

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
        
        # If no sections were found, create default sections from the content
        if not sections and lines:
            # Attempt to detect sections based on line formatting
            sections = self._detect_implicit_sections(lines)
        
        return sections

    def _detect_implicit_sections(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Detect sections that aren't explicitly labeled"""
        # This is a fallback when no explicit sections are found
        
        # Try to find experience section
        exp_entries = []
        for i, line in enumerate(lines):
            if re.search(r'(job|work|employment|position)', line.lower()):
                # Found potential experience entry
                entry = {
                    "company": line,
                    "position": lines[i+1] if i+1 < len(lines) else "",
                    "location": "",
                    "duration": "",
                    "points": []
                }
                
                # Look for bullet points following this entry
                j = i + 2
                while j < len(lines) and (self._is_bullet_point(lines[j]) or lines[j].startswith('    ')):
                    entry["points"].append(self._clean_bullet_point(lines[j]))
                    j += 1
                
                exp_entries.append(entry)
        
        # Create default sections
        sections = []
        if exp_entries:
            sections.append({
                "title": "EXPERIENCE",
                "entries": exp_entries
            })
        
        # Add remaining lines as a generic section
        if lines:
            sections.append({
                "title": "ADDITIONAL INFORMATION",
                "entries": [{
                    "company": "",
                    "position": "",
                    "location": "",
                    "duration": "",
                    "points": [line for line in lines if self._is_bullet_point(line)]
                }]
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
            if re.search(r'University|College|School', line) and not self._is_bullet_point(line):
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
                # Check if line is a bullet point
                if self._is_bullet_point(line):
                    current_entry["points"].append(self._clean_bullet_point(line))
                # Check if line contains a degree
                elif "Bachelor" in line or "Master" in line or "Associate" in line or "Degree" in line:
                    current_entry["position"] = line
                # Check if line contains dates
                elif re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}', line):
                    current_entry["duration"] = line
        
        # Add final entry
        if current_entry:
            entries.append(current_entry)
        
        return entries

    def _parse_experience(self, content: List[str]) -> List[Dict[str, Any]]:
        """Parse experience section"""
        entries = []
        current_entry = None
        bullet_points = []
        
        i = 0
        while i < len(content):
            line = content[i]
            
            # Check if line is a bullet point
            if self._is_bullet_point(line):
                if current_entry:
                    bullet_points.append(self._clean_bullet_point(line))
                else:
                    # Create a default entry if bullet points come before any entry
                    current_entry = {
                        "company": "Professional Experience",
                        "location": "",
                        "position": "",
                        "duration": "",
                        "points": [self._clean_bullet_point(line)]
                    }
            # Check if line might be a company name (not a bullet point)
            elif not self._is_bullet_point(line) and len(line) < 60:  # Companies are usually short lines
                # Save previous entry
                if current_entry:
                    if bullet_points:
                        current_entry["points"] = bullet_points
                    entries.append(current_entry)
                    bullet_points = []
                
                # Extract location if present
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
                
                # Check if next line might be a position or date
                if i+1 < len(content) and not self._is_bullet_point(content[i+1]):
                    next_line = content[i+1]
                    # Check if it's a date
                    if re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}', next_line):
                        current_entry["duration"] = next_line
                        i += 1  # Skip this line on next iteration
                    else:
                        # Assume it's a position
                        current_entry["position"] = next_line
                        i += 1  # Skip this line on next iteration
            
            i += 1
        
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
            if self._is_bullet_point(line):
                skills_entry["points"].append(self._clean_bullet_point(line))
            else:
                # For skills, even non-bulleted lines can be skills
                parts = re.split(r'[,;:|]', line)
                for part in parts:
                    if part.strip():
                        skills_entry["points"].append(part.strip())
        
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
            if self._is_bullet_point(line):
                entry["points"].append(self._clean_bullet_point(line))
            else:
                # For non-bullet points in generic sections, add as separate points
                # but only if they're not too long (likely title lines)
                if len(line) < 60:
                    entry["points"].append(line.strip())
        
        return [entry]

def parse_pdf(filepath: str) -> Dict[str, Any]:
    """Main function to parse PDF"""
    parser = ResumeParser()
    return parser.parse(filepath) 