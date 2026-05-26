import os
from zipfile import ZipFile
# from pypdf import PdfMerger, PdfReader, PdfWriter
def merge_pdfs(pdf_paths, output_path):
    """Fusionne plusieurs fichiers PDF dans l'ordre de la liste"""
    merger = PdfMerger()
    for pdf in pdf_paths:
        merger.append(pdf)
    merger.write(output_path)
    merger.close()

def split_pdf(pdf_path, output_dir):
    """Sépare chaque page d'un PDF dans des fichiers individuels et crée un ZIP"""
    reader = PdfReader(pdf_path)
    zip_path = os.path.join(output_dir, "pages.zip")
    
    with ZipFile(zip_path, 'w') as zipf:
        for idx, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            
            page_filename = f"page_{idx+1}.pdf"
            page_path = os.path.join(output_dir, page_filename)
            
            with open(page_path, "wb") as f:
                writer.write(f)
                
            zipf.write(page_path, arcname=page_filename)
            
    return zip_path

def convert_pdf_to_excel(pdf_path, excel_path):
    """Extrait des tableaux de données structurées d'un PDF vers Excel via Camelot et OpenPyXL"""
    import camelot
    import openpyxl
    
    # Extraction en mode 'lattice' (tableaux délimités par des lignes)
    tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
    
    if len(tables) == 0:
        # Fallback en mode 'stream' (tableaux basés uniquement sur les espaces blancs)
        tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
        
    wb = openpyxl.Workbook()
    # Supprimer la feuille par défaut
    wb.remove(wb.active)
    
    if len(tables) == 0:
        raise Exception("Aucune structure tabulaire n'a pu être extraite de ce document.")
        
    for idx, table in enumerate(tables):
        ws = wb.create_sheet(title=f"Tableau {idx+1}")
        for row in table.data:
            ws.append(row)
            
    wb.save(excel_path)