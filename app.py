from flask import Flask, render_template, request, send_file, jsonify
from docx import Document
from docx2pdf import convert
import os
from datetime import datetime
import json
import tempfile
from pathlib import Path

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Assurez-vous que le dossier uploads existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def create_letter(template_path, company_name, job_title, skills, motivation):
    doc = Document(template_path)
    
    # Remplacer les placeholders dans le document
    for paragraph in doc.paragraphs:
        text = paragraph.text
        text = text.replace("[COMPANY_NAME]", company_name)
        text = text.replace("[JOB_TITLE]", job_title)
        text = text.replace("[SKILLS]", skills)
        text = text.replace("[MOTIVATION]", motivation)
        paragraph.text = text
    
    # Créer un nom de fichier unique
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    docx_filename = f"lettre_motivation_{timestamp}.docx"
    pdf_filename = f"lettre_motivation_{timestamp}.pdf"
    
    # Chemins complets
    docx_path = os.path.join(app.config['UPLOAD_FOLDER'], docx_filename)
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
    
    # Sauvegarder le document
    doc.save(docx_path)
    
    # Convertir en PDF
    convert(docx_path, pdf_path)
    
    return pdf_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_letter():
    try:
        data = request.get_json()
        
        company_name = data.get('company_name', '')
        job_title = data.get('job_title', '')
        skills = data.get('skills', '')
        motivation = data.get('motivation', '')
        
        # Utiliser le template par défaut
        template_path = 'templates/default.docx'
        
        # Générer la lettre
        pdf_path = create_letter(template_path, company_name, job_title, skills, motivation)
        
        # Retourner le chemin du fichier PDF
        return jsonify({
            'success': True,
            'pdf_path': pdf_path
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(
            os.path.join(app.config['UPLOAD_FOLDER'], filename),
            as_attachment=True
        )
    except Exception as e:
        return str(e), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
