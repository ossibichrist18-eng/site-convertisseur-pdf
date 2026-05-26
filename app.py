import os
import shutil
from flask import Flask, render_template, request, send_file, abort
from werkzeug.utils import secure_filename

# Import des modules de conversion
from conversions.pdf_word import convert_pdf_to_word
from conversions.office_pdf import convert_office_to_pdf
from conversions.image_pdf import convert_pdf_to_jpg, convert_image_to_pdf
from conversions.pdf_tools import merge_pdfs, split_pdf

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024 # Limite à 32 Mo

# Dictionnaire de configuration des outils pour éviter la duplication de templates
TOOLS = {
    'pdf-to-word': {'title': 'PDF en Word', 'desc': 'Convertissez vos fichiers PDF en documents Word (.docx) modifiables.', 'endpoint': '/convert/pdf-to-word', 'accept': '.pdf'},
    'word-to-pdf': {'title': 'Word en PDF', 'desc': 'Convertissez vos documents Word (.docx) en fichiers PDF propres.', 'endpoint': '/convert/word-to-pdf', 'accept': '.docx'},
    'pdf-to-jpg': {'title': 'PDF en JPG', 'desc': 'Extrayez les pages de votre PDF sous forme d\'images JPG.', 'endpoint': '/convert/pdf-to-jpg', 'accept': '.pdf'},
    'image-to-pdf': {'title': 'Images en PDF', 'desc': 'Transformez vos images (PNG, JPG) en un document PDF unique.', 'endpoint': '/convert/image-to-pdf', 'accept': '.jpg,.jpeg,.png', 'multiple': True},
    'excel-to-pdf': {'title': 'Excel en PDF', 'desc': 'Convertissez vos feuilles de calcul Excel (.xlsx) au format PDF.', 'endpoint': '/convert/excel-to-pdf', 'accept': '.xlsx'},
    'pdf-to-excel': {'title': 'PDF en Excel', 'desc': 'Extrayez les tableaux de vos fichiers PDF vers un fichier Excel.', 'endpoint': '/convert/pdf-to-excel', 'accept': '.pdf'},
    'ppt-to-pdf': {'title': 'PowerPoint en PDF', 'desc': 'Convertissez vos présentations (.pptx) en fichiers PDF.', 'endpoint': '/convert/ppt-to-pdf', 'accept': '.pptx'},
    'merge-pdf': {'title': 'Fusionner PDF', 'desc': 'Assemblez plusieurs fichiers PDF en un seul document.', 'endpoint': '/convert/merge-pdf', 'accept': '.pdf', 'multiple': True},
    'split-pdf': {'title': 'Diviser PDF', 'desc': 'Séparez les pages d\'un PDF ou extrayez une plage spécifique.', 'endpoint': '/convert/split-pdf', 'accept': '.pdf'}
}

def create_temp_dir():
    """Crée un dossier temporaire unique dans /tmp pour le traitement"""
    import uuid
    path = os.path.join('/tmp', str(uuid.uuid4()))
    os.makedirs(path, exist_ok=True)
    return path

# --- ROUTES PAGES VUES ---

@app.route('/')
def index():
    return render_template('index.html', tools=TOOLS)

@app.route('/outil/<name>')
def tool(name):
    if name not in TOOLS:
        abort(404)
    return render_template('tool.html', tool_id=name, tool=TOOLS[name])

# --- ROUTES API DE CONVERSION ---

@app.route('/convert/pdf-to-word', methods=['POST'])
def api_pdf_to_word():
    if 'file' not in request.files: return "Fichier manquant", 400
    file = request.files['file']
    tmp_dir = create_temp_dir()
    
    in_path = os.path.join(tmp_dir, secure_filename(file.filename))
    file.save(in_path)
    
    out_path = in_path.rsplit('.', 1)[0] + '.docx'
    
    try:
        convert_pdf_to_word(in_path, out_path)
        return send_file(out_path, as_attachment=True, download_name=os.path.basename(out_path))
    except Exception as e:
        return f"Erreur de traitement : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/word-to-pdf', methods=['POST'])
@app.route('/convert/excel-to-pdf', methods=['POST'])
@app.route('/convert/ppt-to-pdf', methods=['POST'])
def api_office_to_pdf():
    if 'file' not in request.files: return "Fichier manquant", 400
    file = request.files['file']
    tmp_dir = create_temp_dir()
    
    in_path = os.path.join(tmp_dir, secure_filename(file.filename))
    file.save(in_path)
    
    try:
        out_path = convert_office_to_pdf(in_path, tmp_dir)
        return send_file(out_path, as_attachment=True, download_name=os.path.basename(out_path))
    except Exception as e:
        return f"Erreur de conversion LibreOffice : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/pdf-to-jpg', methods=['POST'])
def api_pdf_to_jpg():
    if 'file' not in request.files: return "Fichier manquant", 400
    file = request.files['file']
    tmp_dir = create_temp_dir()
    
    in_path = os.path.join(tmp_dir, secure_filename(file.filename))
    file.save(in_path)
    
    try:
        out_zip = convert_pdf_to_jpg(in_path, tmp_dir)
        return send_file(out_zip, as_attachment=True, download_name=os.path.basename(out_zip))
    except Exception as e:
        return f"Erreur : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/image-to-pdf', methods=['POST'])
def api_image_to_pdf():
    files = request.files.getlist('file')
    if not files or files[0].filename == '': return "Fichiers manquants", 400
    
    tmp_dir = create_temp_dir()
    paths = []
    
    for file in files:
        p = os.path.join(tmp_dir, secure_filename(file.filename))
        file.save(p)
        paths.append(p)
        
    out_path = os.path.join(tmp_dir, "images_converties.pdf")
    
    try:
        convert_image_to_pdf(paths, out_path)
        return send_file(out_path, as_attachment=True, download_name="images_combinees.pdf")
    except Exception as e:
        return f"Erreur : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/pdf-to-excel', methods=['POST'])
def api_pdf_to_excel():
    if 'file' not in request.files: return "Fichier manquant", 400
    file = request.files['file']
    tmp_dir = create_temp_dir()
    
    in_path = os.path.join(tmp_dir, secure_filename(file.filename))
    file.save(in_path)
    out_path = in_path.rsplit('.', 1)[0] + '.xlsx'
    
    try:
        # Import local tardif de camelot pour éviter de charger de lourdes libs si non utilisé
        from conversions.pdf_tools import convert_pdf_to_excel
        convert_pdf_to_excel(in_path, out_path)
        return send_file(out_path, as_attachment=True, download_name=os.path.basename(out_path))
    except Exception as e:
        return f"Aucun tableau structuré détecté ou erreur : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/merge-pdf', methods=['POST'])
def api_merge_pdf():
    files = request.files.getlist('file')
    if not files or files[0].filename == '': return "Fichiers manquants", 400
    
    tmp_dir = create_temp_dir()
    paths = []
    for file in files:
        p = os.path.join(tmp_dir, secure_filename(file.filename))
        file.save(p)
        paths.append(p)
        
    out_path = os.path.join(tmp_dir, "fusion.pdf")
    
    try:
        merge_pdfs(paths, out_path)
        return send_file(out_path, as_attachment=True, download_name="document_fusionne.pdf")
    except Exception as e:
        return f"Erreur de fusion : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/split-pdf', methods=['POST'])
def api_split_pdf():
    if 'file' not in request.files: return "Fichier manquant", 400
    file = request.files['file']
    tmp_dir = create_temp_dir()
    
    in_path = os.path.join(tmp_dir, secure_filename(file.filename))
    file.save(in_path)
    
    try:
        out_zip = split_pdf(in_path, tmp_dir)
        return send_file(out_zip, as_attachment=True, download_name="pages_extraites.zip")
    except Exception as e:
        return f"Erreur de division : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)