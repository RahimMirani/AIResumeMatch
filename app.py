from flask import Flask, request, jsonify, render_template, url_for
from werkzeug.utils import secure_filename
import os
from pdf_parser import parse_pdf
from resume_processor import ResumeProcessor
from config import Config
from asgiref.sync import async_to_sync

app = Flask(__name__)
app.config.from_object(Config)

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = 'static'

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# After app configuration
if not app.config['CLAUDE_API_KEY']:
    raise ValueError("Claude API key not found in configuration")

# Initialize resume processor with error handling
try:
    resume_processor = ResumeProcessor()
except ValueError as e:
    print(f"Error initializing resume processor: {e}")
    raise

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload-resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['resume']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PDF files are allowed'}), 400
    
    try:
        # Save and parse PDF
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract text from PDF
        raw_text = parse_pdf(filepath)
        
        # Add debug logging
        print(f"Using API key: {app.config['CLAUDE_API_KEY']}")
        
        # Process with LLM (using async_to_sync)
        structured_data = async_to_sync(resume_processor.process_resume)(raw_text)
        
        # Convert to HTML
        formatted_html = resume_processor.format_for_display(structured_data)
        
        # Clean up
        os.remove(filepath)
        
        return jsonify({
            'message': 'Resume processed successfully',
            'html': formatted_html,
            'structured_data': structured_data
        })
    
    except Exception as e:
        print(f"Error in upload_resume: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 