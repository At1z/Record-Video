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
    
    # Dodaj nagłówki do dokumentu
    doc.add_heading('Frames:', level=1)
    for frame in frames:
        doc.add_paragraph(f'Frame: {frame}')
        doc.add_paragraph().add_run("Frame Image:").bold = True
        doc.add_picture(frame, width=Inches(3))  # Możesz dostosować rozmiar zdjęcia
    
    doc.add_heading('OCR Results:', level=1)
    for ocr_result in ocr_results:
        doc.add_paragraph(f'OCR: {ocr_result}')
    
    doc.add_heading('Audio to Text Results:', level=1)

    # Assuming 'text_results' is the string returned by 'convert_audio_to_text'
    if text_results:  # Check if 'text_results' is not empty
        doc.add_paragraph('Text from audio transcription:')
        doc.add_paragraph(text_results)

    # Zapisz dokument
    doc.save(file_path)
