from flask import Flask, request, jsonify, render_template, url_for
from werkzeug.utils import secure_filename
import os
from pdf_parser import parse_pdf
from resume_processor import ResumeProcessor
from config import Config
from asgiref.sync import async_to_sync
import asyncio

app = Flask(__name__)
app.config.from_object(Config)

# Configure upload settings
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = 'static'

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize resume processor with error handling
try:
    resume_processor = ResumeProcessor()
except Exception as e:
    print(f"Error initializing resume processor: {e}")
    raise

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload-resume', methods=['POST'])
def upload_resume():
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['resume']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only PDF files are allowed'}), 400
        
        # Create a unique filename to avoid conflicts
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Ensure directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Debug print
        print(f"Saving file to: {filepath}")
        
        # Save file
        file.save(filepath)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Failed to save file'}), 500
        
        # Extract text from PDF
        raw_text = parse_pdf(filepath)
        
        # Process with LangChain
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            structured_data = loop.run_until_complete(resume_processor.process_resume(raw_text))
        finally:
            loop.close()
        
        # Convert to HTML
        formatted_html = resume_processor.format_for_display(structured_data)
        
        # Clean up - make sure file exists before trying to remove it
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({
            'message': 'Resume processed successfully',
            'html': formatted_html,
            'structured_data': structured_data
        })
    
    except Exception as e:
        print(f"Error in upload_resume: {str(e)}")
        # If file exists, try to clean up
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 