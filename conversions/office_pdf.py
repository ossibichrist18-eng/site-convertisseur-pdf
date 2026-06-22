import os
import subprocess

def convert_office_to_pdf(input_path, output_dir):
    """Convertit un fichier Word, Excel ou PowerPoint en PDF via LibreOffice."""
    subprocess.run([
        'soffice', '--headless', 
        '--convert-to', 'pdf', 
        '--outdir', output_dir, 
        input_path
    ], check=True)
    filename = os.path.basename(input_path).rsplit('.', 1)[0] + '.pdf'
    return os.path.join(output_dir, filename)