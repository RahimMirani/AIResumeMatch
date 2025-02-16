import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Claude API Configuration
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    
    # Flask Configuration
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # Resume Processing Configuration
    RESUME_CACHE_TIME = 3600  # Cache parsed resumes for 1 hour

