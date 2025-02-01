from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from pdf_parser import parse_pdf

app = Flask(__name__)

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload-resume', methods=['POST'])
def upload_resume():
    # Check if a file was uploaded
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['resume']
    
    # Check if a file was selected
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check if file is allowed
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PDF files are allowed'}), 400
    
    try:
        # Secure the filename and save the file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Parse the PDF
        parsed_text = parse_pdf(filepath)
        
        # Clean up - remove the uploaded file
        os.remove(filepath)
        
        return jsonify({
            'message': 'Resume uploaded and parsed successfully',
            'parsed_text': parsed_text
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 