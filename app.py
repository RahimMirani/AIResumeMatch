from flask import Flask, request, jsonify, render_template, url_for, send_from_directory, abort
from flask_cors import CORS  # Add this import
from werkzeug.utils import secure_filename
import os
from pdf_parser import parse_pdf  # Change import to use our parse_pdf function
from config import Config
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
import uuid
import html
import re

app = Flask(__name__)
CORS(app)  # Enable CORS
app.config.from_object(Config)

# Configure upload settings
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = 'static'

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# We no longer need to initialize a parser since we're using a function
# resume_parser = ResumeParser()  # Remove this line

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload-resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        # Secure the filename
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Parse the PDF using our function
            parsed_data = parse_pdf(filepath)
            
            # Return both the parsed data and the PDF filename
            return jsonify({
                'status': 'success',
                'parsed_data': parsed_data,
                'pdf_filename': filename
            })
        except Exception as e:
            return jsonify({'error': f'Error parsing PDF: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/pdf/<filename>')
def serve_pdf(filename):
    # For security, make sure to validate the filename
    if '..' in filename or filename.startswith('/'):
        abort(404)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        # Get HTML content from request
        data = request.json
        if not data or 'html' not in data:
            return jsonify({'error': 'No HTML content provided'}), 400
        
        # Extract text data from HTML
        html_content = data['html']
        
        # Create a more robust HTML parser
        import re
        
        # Helper function to clean HTML tags
        def clean_html(text):
            return re.sub(r'<[^>]*>', '', text).strip()
        
        # Extract name (looking for h1 tag)
        name_match = re.search(r'<h1>(.*?)</h1>', html_content, re.DOTALL)
        name = clean_html(name_match.group(1)) if name_match else "Resume"
        
        # Extract contact info
        contact_match = re.search(r'<div class="contact-info">(.*?)</div>', html_content, re.DOTALL)
        contact_info = clean_html(contact_match.group(1)) if contact_match else ""
        contact_info = contact_info.replace('<br>', '\n')
        
        # Extract sections
        sections = []
        section_matches = re.finditer(r'<h2>(.*?)</h2>(.*?)(?=<h2>|$)', html_content, re.DOTALL)
        
        for match in section_matches:
            section_title = clean_html(match.group(1))
            section_content = match.group(2)
            
            # Extract bullet points
            bullet_points = []
            bullet_matches = re.finditer(r'<li>(.*?)</li>', section_content, re.DOTALL)
            for bullet_match in bullet_matches:
                bullet_text = clean_html(bullet_match.group(1))
                if bullet_text:
                    bullet_points.append(bullet_text)
            
            sections.append({
                'title': section_title,
                'bullet_points': bullet_points
            })
        
        # Generate a unique filename
        filename = f"resume_{uuid.uuid4().hex}.pdf"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Create PDF using ReportLab
        doc = SimpleDocTemplate(filepath, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=72)
        
        styles = getSampleStyleSheet()
        
        # Create custom styles
        styles.add(ParagraphStyle(
            name='Name',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=1,  # Center alignment
            spaceAfter=10
        ))
        
        styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=styles['Normal'],
            fontSize=10,
            alignment=1,  # Center alignment
            spaceAfter=20
        ))
        
        styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=styles['Heading2'],
            fontSize=12,
            textTransform='uppercase',
            spaceBefore=15,
            spaceAfter=6
        ))
        
        styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=styles['Normal'],
            fontSize=10,
            leftIndent=20,
            spaceAfter=2
        ))
        
        # Build the PDF content
        elements = []
        
        # Add name
        elements.append(Paragraph(name, styles['Name']))
        
        # Add contact info
        elements.append(Paragraph(contact_info, styles['ContactInfo']))
        
        # Add sections
        for section in sections:
            # Add section title
            elements.append(Paragraph(section['title'], styles['SectionTitle']))
            elements.append(Spacer(1, 0.1*inch))
            
            # Add bullet points
            for point in section['bullet_points']:
                # Use standard bullet character
                elements.append(Paragraph(f"• {point}", styles['BulletPoint']))
            
            # Add space after each section
            elements.append(Spacer(1, 0.2*inch))
        
        # Build the PDF
        doc.build(elements)
        
        return jsonify({
            'status': 'success',
            'pdf_filename': filename
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error generating PDF: {str(e)}\n{error_details}")
        return jsonify({'error': f'Error generating PDF: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True) 