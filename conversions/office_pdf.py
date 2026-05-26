import subprocess
import os
import glob

def convert_office_to_pdf(file_path, output_dir):
    """Utilise l'instance LibreOffice binaire installée pour convertir Word/Excel/PPT en PDF"""
    cmd = [
        'libreoffice',
        '--headless',
        '--convert-to', 'pdf',
        '--outdir', output_dir,
        file_path
    ]
    
    # Exécution de la commande système
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=90)
    
    if result.returncode != 0:
        raise Exception(f"LibreOffice error: {result.stderr}")
        
    # On cherche le fichier .pdf généré dans le dossier
    pdf_files = glob.glob(os.path.join(output_dir, "*.pdf"))
    if not pdf_files:
        raise FileNotFoundError("Le fichier PDF n'a pas été généré par LibreOffice.")
        
    return pdf_files[0]