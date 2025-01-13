from docx import Document
from docx.shared import Inches
import os

def create_or_open_word_document(file_path):
    """Funkcja do otwierania lub tworzenia nowego dokumentu Word."""
    if os.path.exists(file_path):
        doc = Document(file_path)  # Otwórz istniejący dokument
    else:
        doc = Document()  # Utwórz nowy dokument
    return doc


def save_to_word(file_path, frames, ocr_results, text_results):
    """Funkcja do zapisywania wyników w dokumencie Word."""
    doc = create_or_open_word_document(file_path)
    if frames and len(frames) > 0:
        for frame in frames:
            doc.add_paragraph().add_run("Frame Image:").bold = True
            doc.add_picture(frame, width=Inches(3))
    
    if ocr_results and os.path.exists(ocr_results):
        try:
            # Read the content of the OCR file
            with open(ocr_results, 'r', encoding='utf-8') as file:
                ocr_results = file.readlines()
            
            # Process each line from the file
            for ocr_result in ocr_results: 
                print(ocr_result.strip())  # strip to remove any extra whitespace/newlines
                doc.add_paragraph(ocr_result.strip())
            
            # Empty the file after processing
            with open(ocr_results, 'w', encoding='utf-8') as file:
                file.write('')
                
        except Exception as e:
            print(f"Error processing OCR file: {e}")
    
    if text_results and text_results.strip():
        doc.add_paragraph(text_results)

    # Zapisz dokument
    doc.save(file_path)
