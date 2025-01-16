from docx import Document
from docx.shared import Inches
import requests
import os

def create_or_open_word_document(file_path):
    """Funkcja do otwierania lub tworzenia nowego dokumentu Word."""
    if os.path.exists(file_path):
        doc = Document(file_path)
    else:
        doc = Document()
    return doc

def send_text_to_api(api_url, api_key, text):
    """Send text to an API and retrieve the summary."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {"text": text}
    response = requests.post(api_url, headers=headers, json=data)

    if response.status_code == 200:
        print("Summary received successfully.")
        return response.json().get("summary", "")
    else:
        raise Exception(f"API request failed: {response.status_code} - {response.text}")
    
def save_to_word(file_path, frames, ocr_results_path, text_results):
    """Funkcja do zapisywania wyników w dokumencie Word."""
    doc = create_or_open_word_document(file_path)
    
    # Add frames if they exist
    if frames and len(frames) > 0:
        for frame in frames:
            doc.add_paragraph().add_run("Frame Image:").bold = True
            doc.add_picture(frame, width=Inches(6))

    # Handle OCR results
    if ocr_results_path and os.path.exists(ocr_results_path):
        try:
            with open(ocr_results_path, 'r', encoding='utf-8') as file:
                ocr_text = file.readlines()
            
            if ocr_text:
                doc.add_paragraph().add_run("OCR Results:").bold = True
                previous_paragraph = None
                for line in ocr_text:
                    clean_text = line.strip()
                    if clean_text:
                        if previous_paragraph:
                            previous_paragraph.add_run('\n' + clean_text)
                        else:
                            previous_paragraph = doc.add_paragraph(clean_text)
                
                # Clear the OCR results file after adding to Word
                with open(ocr_results_path, "w", encoding="utf-8") as f:
                    pass

        except Exception as e:
            print(f"Error processing OCR results: {e}")

    # Add text results if they exist
    if text_results and isinstance(text_results, str) and text_results.strip():
        doc.add_paragraph().add_run("Audio Transcription:").bold = True
        doc.add_paragraph(text_results)

    doc.save(file_path)