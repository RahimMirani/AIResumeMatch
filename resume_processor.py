from typing import Dict, Any
import json
import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import JsonOutputParser
from langchain.schema import StrOutputParser

load_dotenv()

class ResumeProcessor:
    def __init__(self):
        # Initialize Claude through LangChain
        self.llm = ChatAnthropic(
            model="claude-3-opus-20240229",
            anthropic_api_key=os.getenv('CLAUDE_API_KEY'),
            max_tokens=4000,
            temperature=0.1
        )
        
        # Create output parser for JSON
        self.parser = JsonOutputParser()
        
        # Define the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a resume parsing expert. Analyze the resume and return a JSON with this structure:
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
                    }
                ]
            }
            Return only valid JSON, no additional text."""),
            ("user", "{text}")
        ])
        
        # Create the chain
        self.chain = self.prompt | self.llm | self.parser

    async def process_resume(self, text: str) -> Dict[str, Any]:
        """Process resume text using LangChain"""
        try:
            # Process the resume
            result = await self.chain.ainvoke({"text": text})
            return result
            
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