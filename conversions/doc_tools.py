import subprocess
import os

def txt_to_pdf(input_path, output_path):
    """Convertit un fichier texte (.txt) en PDF via LibreOffice."""
    output_dir = os.path.dirname(output_path)
    subprocess.run([
        'soffice', '--headless', 
        '--convert-to', 'pdf', 
        '--outdir', output_dir, 
        input_path
    ], check=True)
    generated = input_path.rsplit('.', 1)[0] + '.pdf'
    if os.path.exists(generated):
        os.replace(generated, output_path)

def html_to_pdf(input_path, output_path):
    """Convertit un fichier HTML en PDF via LibreOffice."""
    output_dir = os.path.dirname(output_path)
    subprocess.run([
        'soffice', '--headless', 
        '--convert-to', 'pdf', 
        '--outdir', output_dir, 
        input_path
    ], check=True)
    generated = input_path.rsplit('.', 1)[0] + '.pdf'
    if os.path.exists(generated):
        os.replace(generated, output_path)