import os
import shutil
import uuid
from flask import Flask, render_template, request, send_file, abort, send_from_directory
from werkzeug.utils import secure_filename

# Imports d'origine
from conversions.pdf_word import convert_pdf_to_word
from conversions.office_pdf import convert_office_to_pdf
from conversions.image_pdf import convert_pdf_to_jpg, convert_image_to_pdf
from conversions.pdf_tools import merge_pdfs, split_pdf, compress_pdf, remove_pdf_password, add_page_numbers, add_watermark, protect_pdf
from conversions.image_tools import jpg_to_png, png_to_jpg, resize_image, to_webp, compress_image, to_black_and_white
from conversions.video_tools import compress_video, video_to_mp3, video_to_gif, trim_video
from conversions.audio_tools import mp3_to_wav, wav_to_mp3
from conversions.doc_tools import txt_to_pdf, html_to_pdf

# Nouveaux modules ajoutés
from conversions.office_ppt import convert_word_to_ppt, convert_ppt_to_word, convert_pdf_to_ppt
from conversions.advanced_tools import convert_pdf_to_audio, ocr_file_to_txt, anonymize_pdf, extract_pdf_images

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024

@app.route('/google-site-verification.html')
def google_verify():
    return '<html><head><meta name="google-site-verification" content="-XEHZKgk1w1fOxoLSRdeIokKVrSG4yAH7_Ltnb8Gikw"/></head><body>google-site-verification: -XEHZKgk1w1fOxoLSRdeIokKVrSG4yAH7_Ltnb8Gikw</body></html>', 200

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'sitemap.xml', mimetype='application/xml')

@app.route('/googlec29be3f3b9d13ec3.html')
def google_verify2():
    return 'google-site-verification: googlec29be3f3b9d13ec3', 200, {'Content-Type': 'text/html'}

@app.route('/robots.txt')
def robots():
    content = "User-agent: *\nAllow: /\nSitemap: https://convertisseurpdf.vidsave.tech/sitemap.xml"
    return content, 200, {'Content-Type': 'text/plain'}

TOOLS = {
    # PDF
    'pdf-to-word':     {'title': 'PDF en Word',         'desc': 'Convertissez vos fichiers PDF en documents Word (.docx) modifiables.',     'endpoint': '/convert/pdf-to-word',     'accept': '.pdf'},
    'word-to-pdf':     {'title': 'Word en PDF',          'desc': 'Convertissez vos documents Word (.docx) en fichiers PDF propres.',          'endpoint': '/convert/word-to-pdf',     'accept': '.docx'},
    'pdf-to-jpg':      {'title': 'PDF en JPG',           'desc': "Extrayez les pages de votre PDF sous forme d'images JPG.",                 'endpoint': '/convert/pdf-to-jpg',      'accept': '.pdf'},
    'image-to-pdf':    {'title': 'Images en PDF',        'desc': 'Transformez vos images (PNG, JPG) en un document PDF unique.',              'endpoint': '/convert/image-to-pdf',    'accept': '.jpg,.jpeg,.png', 'multiple': True},
    'excel-to-pdf':    {'title': 'Excel en PDF',         'desc': 'Convertissez vos feuilles de calcul Excel (.xlsx) au format PDF.',          'endpoint': '/convert/excel-to-pdf',    'accept': '.xlsx'},
    'pdf-to-excel':    {'title': 'PDF en Excel',         'desc': 'Extrayez les tableaux de vos fichiers PDF vers un fichier Excel.',          'endpoint': '/convert/pdf-to-excel',    'accept': '.pdf'},
    'ppt-to-pdf':      {'title': 'PowerPoint en PDF',    'desc': 'Convertissez vos présentations (.pptx) en fichiers PDF.',                  'endpoint': '/convert/ppt-to-pdf',      'accept': '.pptx'},
    'merge-pdf':       {'title': 'Fusionner PDF',        'desc': 'Assemblez plusieurs fichiers PDF en un seul document.',                     'endpoint': '/convert/merge-pdf',       'accept': '.pdf', 'multiple': True},
    'split-pdf':       {'title': 'Diviser PDF',          'desc': "Séparez les pages d'un PDF ou extrayez une plage spécifique.",              'endpoint': '/convert/split-pdf',       'accept': '.pdf'},
    'compress-pdf':    {'title': 'Compresser PDF',       'desc': 'Réduisez la taille de vos fichiers PDF sans perte de qualité visible.',     'endpoint': '/convert/compress-pdf',    'accept': '.pdf'},
    'remove-password': {'title': 'Déverrouiller PDF',    'desc': "Supprimez le mot de passe d'un PDF protégé.",                              'endpoint': '/convert/remove-password', 'accept': '.pdf', 'password': True},
    'add-page-numbers':{'title': 'Numéroter PDF',        'desc': 'Ajoutez automatiquement des numéros de page à votre PDF.',                 'endpoint': '/convert/add-page-numbers','accept': '.pdf'},
    'watermark-pdf':   {'title': 'Filigrane PDF',        'desc': 'Ajoutez un texte en filigrane sur toutes les pages de votre PDF.',         'endpoint': '/convert/watermark-pdf',   'accept': '.pdf', 'watermark': True},
    'protect-pdf':     {'title': 'Protéger PDF',         'desc': 'Protégez votre PDF avec un mot de passe.',                                 'endpoint': '/convert/protect-pdf',     'accept': '.pdf', 'password': True},
    'txt-to-pdf':      {'title': 'TXT en PDF',           'desc': 'Convertissez vos fichiers texte (.txt) en documents PDF.',                 'endpoint': '/convert/txt-to-pdf',      'accept': '.txt'},
    'html-to-pdf':     {'title': 'HTML en PDF',          'desc': 'Convertissez vos pages HTML en documents PDF.',                            'endpoint': '/convert/html-to-pdf',     'accept': '.html,.htm'},
    
    # Nouveaux outils PDF et Comparateur
    'pdf-to-ppt':      {'title': 'PDF en PowerPoint',    'desc': 'Convertissez vos fichiers PDF en présentations PowerPoint (.pptx).',        'endpoint': '/convert/pdf-to-ppt',      'accept': '.pdf'},
    'compare-pdf':     {'title': 'Comparer PDF',         'desc': 'Affichez et comparez deux fichiers PDF locaux côte à côte de manière privée.', 'endpoint': '#', 'accept': '.pdf'},
    
    # Outils avancés (Audio / OCR / Securité)
    'pdf-to-audio':    {'title': 'PDF en Livre Audio',   'desc': 'Convertissez le texte de votre PDF en un fichier audio MP3 agréable à écouter.', 'endpoint': '/convert/pdf-to-audio',    'accept': '.pdf'},
    'ocr-doc':         {'title': 'OCR - Image/PDF en Texte', 'desc': 'Extrayez et copiez le texte présent sur un PDF scanné ou une simple photo.', 'endpoint': '/convert/ocr-doc',         'accept': '.pdf,.png,.jpg,.jpeg'},
    'anonymize-pdf':   {'title': 'Anonymiser un PDF',    'desc': 'Supprimez toutes les métadonnées cachées (nom complet, date, logiciel) de votre PDF.', 'endpoint': '/convert/anonymize-pdf',   'accept': '.pdf'},
    'extract-images':  {'title': "Extraire les Images d'un PDF", 'desc': 'Récupérez uniquement les illustrations et les photos de votre PDF dans un dossier ZIP.', 'endpoint': '/convert/extract-images',  'accept': '.pdf'},

    # Images
    'jpg-to-png':      {'title': 'JPG en PNG',           'desc': 'Convertissez vos images JPG en format PNG avec transparence.',             'endpoint': '/convert/jpg-to-png',      'accept': '.jpg,.jpeg', 'multiple': True},
    'png-to-jpg':      {'title': 'PNG en JPG',           'desc': 'Convertissez vos images PNG en format JPG optimisé.',                      'endpoint': '/convert/png-to-jpg',      'accept': '.png', 'multiple': True},
    'resize-image':    {'title': 'Redimensionner Image', 'desc': 'Redimensionnez vos images à la taille exacte souhaitée.',                  'endpoint': '/convert/resize-image',    'accept': '.jpg,.jpeg,.png,.webp', 'multiple': True, 'resize': True},
    'to-webp':         {'title': 'Image en WebP',        'desc': 'Convertissez vos images JPG/PNG en format WebP léger.',                   'endpoint': '/convert/to-webp',         'accept': '.jpg,.jpeg,.png', 'multiple': True},
    'compress-image':  {'title': 'Compresser Image',     'desc': 'Réduisez le poids de vos images sans perte de qualité visible.',           'endpoint': '/convert/compress-image',  'accept': '.jpg,.jpeg,.png', 'multiple': True},
    'black-and-white': {'title': 'Image Noir & Blanc',   'desc': 'Convertissez vos images en noir et blanc instantanément.',                 'endpoint': '/convert/black-and-white', 'accept': '.jpg,.jpeg,.png', 'multiple': True},
    
    # PowerPoint / Word
    'word-to-ppt':     {'title': 'Word en PowerPoint',    'desc': 'Convertissez vos documents Word (.docx) en présentations PowerPoint (.pptx).', 'endpoint': '/convert/word-to-ppt',     'accept': '.docx'},
    'ppt-to-word':     {'title': 'PowerPoint en Word',    'desc': 'Convertissez vos présentations (.pptx) en documents Word (.docx).',          'endpoint': '/convert/ppt-to-word',     'accept': '.pptx'},

    # Audio
    'mp3-to-wav':      {'title': 'MP3 en WAV',           'desc': 'Convertissez vos fichiers MP3 en format WAV haute qualité.',               'endpoint': '/convert/mp3-to-wav',      'accept': '.mp3'},
    'wav-to-mp3':      {'title': 'WAV en MP3',           'desc': 'Convertissez vos fichiers WAV en MP3 compressé.',                          'endpoint': '/convert/wav-to-mp3',      'accept': '.wav'},
    
    # Vidéo
    'compress-video':  {'title': 'Compresser Vidéo',     'desc': 'Réduisez la taille de vos vidéos MP4 sans perte de qualité visible.',      'endpoint': '/convert/compress-video',  'accept': '.mp4,.mov,.avi,.mkv'},
    'video-to-mp3':    {'title': 'Vidéo en MP3',         'desc': 'Extrayez la piste audio de vos vidéos en fichier MP3.',                    'endpoint': '/convert/video-to-mp3',    'accept': '.mp4,.mov,.avi,.mkv,.webm'},
    'video-to-gif':    {'title': 'Vidéo en GIF',         'desc': 'Convertissez vos vidéos en GIF animé.',                                    'endpoint': '/convert/video-to-gif',    'accept': '.mp4,.mov,.avi,.mkv,.webm'},
    'trim-video':      {'title': 'Couper Vidéo',         'desc': 'Coupez votre vidéo en définissant un début et une fin.',                   'endpoint': '/convert/trim-video',      'accept': '.mp4,.mov,.avi,.mkv,.webm', 'trim': True},
}

def create_temp_dir():
    path = os.path.join('/tmp', str(uuid.uuid4()))
    os.makedirs(path, exist_ok=True)
    return path

@app.route('/')
def index():
    return render_template('index.html', tools=TOOLS)

@app.route('/outil/<name>')
def tool(name):
    if name not in TOOLS:
        abort(404)
    if name == 'compare-pdf':
        return render_template('compare.html', tool_id=name, tool=TOOLS[name])
    return render_template('tool.html', tool_id=name, tool=TOOLS[name])

# API d'origine
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
        return f"Erreur : {str(e)}", 500
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
        return f"Erreur LibreOffice : {str(e)}", 500
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
        from conversions.pdf_tools import convert_pdf_to_excel
        convert_pdf_to_excel(in_path, out_path)
        return send_file(out_path, as_attachment=True, download_name=os.path.basename(out_path))
    except Exception as e:
        return f"Erreur : {str(e)}", 500
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
        return f"Erreur : {str(e)}", 500
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
        return f"Erreur : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/compress-pdf', methods=['POST'])
def api_compress_pdf():
    if 'file' not in request.files: return "Fichier manquant", 400
    file = request.files['file']
    tmp_dir = create_temp_dir()
    in_path = os.path.join(tmp_dir, secure_filename(file.filename))
    file.save(in_path)
    out_path = os.path.join(tmp_dir, "compresse.pdf")
    try:
        compress_pdf(in_path, out_path)
        return send_file(out_path, as_attachment=True, download_name="pdf_compresse.pdf")
    except Exception as e:
        return f"Erreur : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/remove-password', methods=['POST'])
def api_remove_password():
    if 'file' not in request.files: return "Fichier manquant", 400
    file = request.files['file']
    password = request.form.get('password', '')
    tmp_dir = create_temp_dir()
    in_path = os.path.join(tmp_dir, secure_filename(file.filename))
    file.save(in_path)
    out_path = os.path.join(tmp_dir, "deverrouille.pdf")
    try:
        remove_pdf_password(in_path, password, out_path)
        return send_file(out_path, as_attachment=True, download_name="pdf_deverrouille.pdf")
    except Exception as e:
        return f"Mot de passe incorrect ou erreur : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/add-page-numbers', methods=['POST'])
def api_add_page_numbers():
    if 'file' not in request.files: return "Fichier manquant", 400
    file = request.files['file']
    tmp_dir = create_temp_dir()
    in_path = os.path.join(tmp_dir, secure_filename(file.filename))
    file.save(in_path)
    out_path = os.path.join(tmp_dir, "numerote.pdf")
    try:
        add_page_numbers(in_path, out_path)
        return send_file(out_path, as_attachment=True, download_name="pdf_numerote.pdf")
    except Exception as e:
        return f"Erreur : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/watermark-pdf', methods=['POST'])
def api_watermark_pdf():
    if 'file' not in request.files: return "Fichier manquant", 400
    file = request.files['file']
    text = request.form.get('watermark', 'CONFIDENTIEL')
    tmp_dir = create_temp_dir()
    in_path = os.path.join(tmp_dir, secure_filename(file.filename))
    file.save(in_path)
    out_path = os.path.join(tmp_dir, "filigrane.pdf")
    try:
        add_watermark(in_path, out_path, text)
        return send_file(out_path, as_attachment=True, download_name="pdf_filigrane.pdf")
    except Exception as e:
        return f"Erreur : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/protect-pdf', methods=['POST'])
def api_protect_pdf():
    if 'file' not in request.files: return "Fichier manquant", 400
    file = request.files['file']
    password = request.form.get('password', '')
    if not password: return "Mot de passe requis", 400
    tmp_dir = create_temp_dir()
    in_path = os.path.join(tmp_dir, secure_filename(file.filename))
    file.save(in_path)
    out_path = os.path.join(tmp_dir, "protege.pdf")
    try:
        protect_pdf(in_path, out_path, password)
        return send_file(out_path, as_attachment=True, download_name="pdf_protege.pdf")
    except Exception as e:
        return f"Erreur : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/txt-to-pdf', methods=['POST'])
def api_txt_to_pdf():
    if 'file' not in request.files: return "Fichier manquant", 400
    file = request.files['file']
    tmp_dir = create_temp_dir()
    in_path = os.path.join(tmp_dir, secure_filename(file.filename))
    file.save(in_path)
    out_path = os.path.join(tmp_dir, "document.pdf")
    try:
        txt_to_pdf(in_path, out_path)
        return send_file(out_path, as_attachment=True, download_name="document.pdf")
    except Exception as e:
        return f"Erreur : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/html-to-pdf', methods=['POST'])
def api_html_to_pdf():
    if 'file' not in request.files: return "Fichier manquant", 400
    file = request.files['file']
    tmp_dir = create_temp_dir()
    in_path = os.path.join(tmp_dir, secure_filename(file.filename))
    file.save(in_path)
    out_path = os.path.join(tmp_dir, "page.pdf")
    try:
        html_to_pdf(in_path, out_path)
        return send_file(out_path, as_attachment=True, download_name="page.pdf")
    except Exception as e:
        return f"Erreur : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/jpg-to-png', methods=['POST'])
def api_jpg_to_png():
    files = request.files.getlist('file')
    if not files or files[0].filename == '': return "Fichier manquant", 400
    tmp_dir = create_temp_dir()
    paths = []
    for file in files:
        p = os.path.join(tmp_dir, secure_filename(file.filename))
        file.save(p)
        paths.append(p)
    try:
        out_path, is_zip = jpg_to_png(paths, tmp_dir)
        name = "images_converties.zip" if is_zip else os.path.basename(out_path)
        return send_file(out_path, as_attachment=True, download_name=name)
    except Exception as e:
        return f"Erreur : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/png-to-jpg', methods=['POST'])
def api_png_to_jpg():
    files = request.files.getlist('file')
    if not files or files[0].filename == '': return "Fichier manquant", 400
    tmp_dir = create_temp_dir()
    paths = []
    for file in files:
        p = os.path.join(tmp_dir, secure_filename(file.filename))
        file.save(p)
        paths.append(p)
    try:
        out_path, is_zip = png_to_jpg(paths, tmp_dir)
        name = "images_converties.zip" if is_zip else os.path.basename(out_path)
        return send_file(out_path, as_attachment=True, download_name=name)
    except Exception as e:
        return f"Erreur : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/resize-image', methods=['POST'])
def api_resize_image():
    files = request.files.getlist('file')
    if not files or files[0].filename == '': return "Fichier manquant", 400
    width = request.form.get('width', 800)
    height = request.form.get('height', 600)
    tmp_dir = create_temp_dir()
    paths = []
    for file in files:
        p = os.path.join(tmp_dir, secure_filename(file.filename))
        file.save(p)
        paths.append(p)
    try:
        out_path, is_zip = resize_image(paths, tmp_dir, width, height)
        name = "images_redimensionnees.zip" if is_zip else os.path.basename(out_path)
        return send_file(out_path, as_attachment=True, download_name=name)
    except Exception as e:
        return f"Erreur : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/to-webp', methods=['POST'])
def api_to_webp():
    files = request.files.getlist('file')
    if not files or files[0].filename == '': return "Fichier manquant", 400
    tmp_dir = create_temp_dir()
    paths = []
    for file in files:
        p = os.path.join(tmp_dir, secure_filename(file.filename))
        file.save(p)
        paths.append(p)
    try:
        out_path, is_zip = to_webp(paths, tmp_dir)
        name = "images_webp.zip" if is_zip else os.path.basename(out_path)
        return send_file(out_path, as_attachment=True, download_name=name)
    except Exception as e:
        return f"Erreur : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/compress-image', methods=['POST'])
def api_compress_image():
    files = request.files.getlist('file')
    if not files or files[0].filename == '': return "Fichier manquant", 400
    tmp_dir = create_temp_dir()
    paths = []
    for file in files:
        p = os.path.join(tmp_dir, secure_filename(file.filename))
        file.save(p)
        paths.append(p)
    try:
        out_path, is_zip = compress_image(paths, tmp_dir)
        name = "images_compressees.zip" if is_zip else os.path.basename(out_path)
        return send_file(out_path, as_attachment=True, download_name=name)
    except Exception as e:
        return f"Erreur : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/black-and-white', methods=['POST'])
def api_black_and_white():
    files = request.files.getlist('file')
    if not files or files[0].filename == '': return "Fichier manquant", 400
    tmp_dir = create_temp_dir()
    paths = []
    for file in files:
        p = os.path.join(tmp_dir, secure_filename(file.filename))
        file.save(p)
        paths.append(p)
    try:
        out_path, is_zip = to_black_and_white(paths, tmp_dir)
        name = "images_nb.zip" if is_zip else os.path.basename(out_path)
        return send_file(out_path, as_attachment=True, download_name=name)
    except Exception as e:
        return f"Erreur : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/mp3-to-wav', methods=['POST'])
def api_mp3_to_wav():
    if 'file' not in request.files: return "Fichier manquant", 400
    file = request.files['file']
    tmp_dir = create_temp_dir()
    in_path = os.path.join(tmp_dir, secure_filename(file.filename))
    file.save(in_path)
    out_path = os.path.join(tmp_dir, "audio.wav")
    try:
        mp3_to_wav(in_path, out_path)
        return send_file(out_path, as_attachment=True, download_name="audio_converti.wav")
    except Exception as e:
        return f"Erreur : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/wav-to-mp3', methods=['POST'])
def api_wav_to_mp3():
    if 'file' not in request.files: return "Fichier manquant", 400
    file = request.files['file']
    tmp_dir = create_temp_dir()
    in_path = os.path.join(tmp_dir, secure_filename(file.filename))
    file.save(in_path)
    out_path = os.path.join(tmp_dir, "audio.mp3")
    try:
        wav_to_mp3(in_path, out_path)
        return send_file(out_path, as_attachment=True, download_name="audio_converti.mp3")
    except Exception as e:
        return f"Erreur : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/compress-video', methods=['POST'])
def api_compress_video():
    if 'file' not in request.files: return "Fichier manquant", 400
    file = request.files['file']
    tmp_dir = create_temp_dir()
    in_path = os.path.join(tmp_dir, secure_filename(file.filename))
    file.save(in_path)
    out_path = os.path.join(tmp_dir, "video_compresse.mp4")
    try:
        compress_video(in_path, out_path)
        return send_file(out_path, as_attachment=True, download_name="video_compresse.mp4")
    except Exception as e:
        return f"Erreur : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/video-to-mp3', methods=['POST'])
def api_video_to_mp3():
    if 'file' not in request.files: return "Fichier manquant", 400
    file = request.files['file']
    tmp_dir = create_temp_dir()
    in_path = os.path.join(tmp_dir, secure_filename(file.filename))
    file.save(in_path)
    out_path = os.path.join(tmp_dir, "audio.mp3")
    try:
        video_to_mp3(in_path, out_path)
        return send_file(out_path, as_attachment=True, download_name="audio_extrait.mp3")
    except Exception as e:
        return f"Erreur : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/video-to-gif', methods=['POST'])
def api_video_to_gif():
    if 'file' not in request.files: return "Fichier manquant", 400
    file = request.files['file']
    tmp_dir = create_temp_dir()
    in_path = os.path.join(tmp_dir, secure_filename(file.filename))
    file.save(in_path)
    out_path = os.path.join(tmp_dir, "animation.gif")
    try:
        video_to_gif(in_path, out_path)
        return send_file(out_path, as_attachment=True, download_name="animation.gif")
    except Exception as e:
        return f"Erreur : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/trim-video', methods=['POST'])
def api_trim_video():
    if 'file' not in request.files: return "Fichier manquant", 400
    file = request.files['file']
    start = request.form.get('start', '0')
    end = request.form.get('end', '30')
    tmp_dir = create_temp_dir()
    in_path = os.path.join(tmp_dir, secure_filename(file.filename))
    file.save(in_path)
    out_path = os.path.join(tmp_dir, "video_coupee.mp4")
    try:
        trim_video(in_path, out_path, start, end)
        return send_file(out_path, as_attachment=True, download_name="video_coupee.mp4")
    except Exception as e:
        return f"Erreur : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

# NOUVEAUX ENDPOINTS APIS AVANCÉS & PPTX

@app.route('/convert/word-to-ppt', methods=['POST'])
def api_word_to_ppt():
    if 'file' not in request.files: return "Fichier manquant", 400
    file = request.files['file']
    tmp_dir = create_temp_dir()
    in_path = os.path.join(tmp_dir, secure_filename(file.filename))
    file.save(in_path)
    try:
        out_path = convert_word_to_ppt(in_path, tmp_dir)
        return send_file(out_path, as_attachment=True, download_name=os.path.basename(out_path))
    except Exception as e:
        return f"Erreur LibreOffice : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/ppt-to-word', methods=['POST'])
def api_ppt_to_word():
    if 'file' not in request.files: return "Fichier manquant", 400
    file = request.files['file']
    tmp_dir = create_temp_dir()
    in_path = os.path.join(tmp_dir, secure_filename(file.filename))
    file.save(in_path)
    try:
        out_path = convert_ppt_to_word(in_path, tmp_dir)
        return send_file(out_path, as_attachment=True, download_name=os.path.basename(out_path))
    except Exception as e:
        return f"Erreur LibreOffice : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/pdf-to-ppt', methods=['POST'])
def api_pdf_to_ppt():
    if 'file' not in request.files: return "Fichier manquant", 400
    file = request.files['file']
    tmp_dir = create_temp_dir()
    in_path = os.path.join(tmp_dir, secure_filename(file.filename))
    file.save(in_path)
    out_path = os.path.join(tmp_dir, in_path.rsplit('.', 1)[0] + '.pptx')
    try:
        convert_pdf_to_ppt(in_path, out_path)
        return send_file(out_path, as_attachment=True, download_name=os.path.basename(out_path))
    except Exception as e:
        return f"Erreur : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/pdf-to-audio', methods=['POST'])
def api_pdf_to_audio():
    if 'file' not in request.files: return "Fichier manquant", 400
    file = request.files['file']
    tmp_dir = create_temp_dir()
    in_path = os.path.join(tmp_dir, secure_filename(file.filename))
    file.save(in_path)
    out_path = os.path.join(tmp_dir, "audiobook.mp3")
    try:
        convert_pdf_to_audio(in_path, out_path)
        return send_file(out_path, as_attachment=True, download_name="livre_audio.mp3")
    except Exception as e:
        return f"Erreur de traitement : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/ocr-doc', methods=['POST'])
def api_ocr_doc():
    if 'file' not in request.files: return "Fichier manquant", 400
    file = request.files['file']
    tmp_dir = create_temp_dir()
    in_path = os.path.join(tmp_dir, secure_filename(file.filename))
    file.save(in_path)
    out_path = os.path.join(tmp_dir, "texte_extrait.txt")
    try:
        ocr_file_to_txt(in_path, out_path)
        return send_file(out_path, as_attachment=True, download_name="texte_extrait.txt")
    except Exception as e:
        return f"Erreur OCR : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/anonymize-pdf', methods=['POST'])
def api_anonymize_pdf():
    if 'file' not in request.files: return "Fichier manquant", 400
    file = request.files['file']
    tmp_dir = create_temp_dir()
    in_path = os.path.join(tmp_dir, secure_filename(file.filename))
    file.save(in_path)
    out_path = os.path.join(tmp_dir, "pdf_anonymise.pdf")
    try:
        anonymize_pdf(in_path, out_path)
        return send_file(out_path, as_attachment=True, download_name="pdf_anonymise.pdf")
    except Exception as e:
        return f"Erreur : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/convert/extract-images', methods=['POST'])
def api_extract_images():
    if 'file' not in request.files: return "Fichier manquant", 400
    file = request.files['file']
    tmp_dir = create_temp_dir()
    in_path = os.path.join(tmp_dir, secure_filename(file.filename))
    file.save(in_path)
    out_path = os.path.join(tmp_dir, "images_extraites.zip")
    try:
        extract_pdf_images(in_path, out_path)
        return send_file(out_path, as_attachment=True, download_name="images_extraites.zip")
    except Exception as e:
        return f"Erreur : {str(e)}", 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
