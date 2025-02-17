from flask import Flask, request, jsonify, render_template, url_for
from werkzeug.utils import secure_filename
import os
from pdf_parser import ResumeParser  # Updated import
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Configure upload settings
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = 'static'

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize resume parser
resume_parser = ResumeParser()

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
        
        # Save file
        file.save(filepath)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Failed to save file'}), 500
        
        try:
            # Parse the PDF using our parser
            parsed_data = resume_parser.parse(filepath)
            
            return jsonify({
                'message': 'Resume processed successfully',
                'parsed_data': parsed_data  # This is what the frontend expects
            })
            
        finally:
            # Clean up - make sure file exists before trying to remove it
            if os.path.exists(filepath):
                os.remove(filepath)
    
    except Exception as e:
        print(f"Error in upload_resume: {str(e)}")
        # If file exists, try to clean up
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 