from typing import Dict, Any
import json
import os
from dotenv import load_dotenv
import aiohttp

load_dotenv()

class ResumeProcessor:
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        
        self.system_prompt = """
        As a resume parsing expert, analyze the given resume and structure it consistently.
        Focus on extracting and organizing:
        1. Personal and contact information
        2. Professional summary
        3. Work experience with detailed bullet points
        4. Education details
        5. Skills and certifications
        
        Format the output as JSON with this structure:
        {
            "personal_info": {
                "name": "",
                "contact": {
                    "email": "",
                    "phone": "",
                    "location": "",
                    "linkedin": ""
                },
                "summary": ""
            },
            "sections": [
                {
                    "title": "Experience",
                    "entries": [
                        {
                            "company": "",
                            "position": "",
                            "location": "",
                            "duration": {
                                "start": "",
                                "end": ""
                            },
                            "points": []
                        }
                    ]
                },
                {
                    "title": "Education",
                    "entries": [
                        {
                            "institution": "",
                            "degree": "",
                            "duration": {
                                "start": "",
                                "end": ""
                            },
                            "details": []
                        }
                    ]
                },
                {
                    "title": "Skills",
                    "categories": {
                        "technical": [],
                        "soft": [],
                        "tools": []
                    }
                }
            ]
        }
        """

    async def process_resume(self, text: str) -> Dict[str, Any]:
        """Process resume text using DeepSeek API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": text}
                ],
                "temperature": 0.1,
                "max_tokens": 2000
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        raise Exception(f"API request failed with status {response.status}")
                    
                    result = await response.json()
                    structured_data = json.loads(result['choices'][0]['message']['content'])
                    return structured_data

        except json.JSONDecodeError:
            raise Exception("Failed to parse LLM response")
        except Exception as e:
            print(f"Error processing resume: {str(e)}")
            raise

    def format_for_display(self, structured_data: Dict[str, Any]) -> str:
        """Convert structured data to HTML for display"""
        html = []
        
        # Personal Info Section
        personal = structured_data["personal_info"]
        html.append('<div class="personal-info section">')
        html.append(f'<h1 class="name">{personal["name"]}</h1>')
        
        # Contact Information
        contact = personal["contact"]
        html.append('<div class="contact-info">')
        contact_items = []
        if contact.get("email"): 
            contact_items.append(f'<span class="email">{contact["email"]}</span>')
        if contact.get("phone"): 
            contact_items.append(f'<span class="phone">{contact["phone"]}</span>')
        if contact.get("location"): 
            contact_items.append(f'<span class="location">{contact["location"]}</span>')
        if contact.get("linkedin"):
            contact_items.append(f'<a href="{contact["linkedin"]}" class="linkedin">LinkedIn</a>')
        html.append(' | '.join(contact_items))
        html.append('</div>')
        
        # Summary
        if personal.get("summary"):
            html.append(f'<div class="summary"><p>{personal["summary"]}</p></div>')
        html.append('</div>')
        
        # Main Sections
        for section in structured_data["sections"]:
            html.append(f'<div class="section" data-section="{section["title"].lower()}">')
            html.append(f'<h2>{section["title"]}</h2>')
            
            if section["title"] == "Skills":
                # Skills section
                html.append('<div class="skills-container">')
                for category, skills in section["categories"].items():
                    if skills:
                        html.append(f'<div class="skill-category">')
                        html.append(f'<h3>{category.title()}</h3>')
                        html.append('<ul class="skills-list">')
                        for skill in skills:
                            html.append(f'<li class="skill-item">{skill}</li>')
                        html.append('</ul>')
                        html.append('</div>')
                html.append('</div>')
            else:
                # Experience and Education sections
                for entry in section["entries"]:
                    html.append('<div class="entry">')
                    
                    # Header info (company/institution and position/degree)
                    header_primary = entry.get("company") or entry.get("institution")
                    header_secondary = entry.get("position") or entry.get("degree")
                    
                    if header_primary:
                        html.append(f'<h3>{header_primary}</h3>')
                    if header_secondary:
                        html.append(f'<h4>{header_secondary}</h4>')
                    
                    # Duration
                    if "duration" in entry:
                        duration = entry["duration"]
                        duration_text = f'{duration["start"]} - {duration["end"]}'
                        html.append(f'<p class="duration">{duration_text}</p>')
                    
                    # Points/Details
                    points = entry.get("points") or entry.get("details")
                    if points:
                        html.append('<ul class="points">')
                        for point in points:
                            html.append(
                                f'<li class="bullet-point" data-original="{point}">'
                                f'• {point}</li>'
                            )
                        html.append('</ul>')
                    
                    html.append('</div>')
            
            html.append('</div>')
        
        return '\n'.join(html) 