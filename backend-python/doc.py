from docx import Document
from docx.shared import Inches
import os
import requests

def create_or_open_word_document(file_path):
    """Funkcja do otwierania lub tworzenia nowego dokumentu Word."""
    if os.path.exists(file_path):
        doc = Document(file_path)
    else:
        doc = Document()
    return doc

def extract_text_from_word(file_path):
    """Extract text from a Word document."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist.")

    doc = Document(file_path)
    return "\n".join(para.text for para in doc.paragraphs)

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

def save_to_word(file_path, frames, ocr_results, text_results):
    """Funkcja do zapisywania wyników w dokumencie Word."""
    doc = create_or_open_word_document(file_path)
    if frames and len(frames) > 0:
        for frame in frames:
            doc.add_paragraph().add_run("Frame Image:").bold = True
            doc.add_picture(frame, width=Inches(6))

    if ocr_results and os.path.exists(ocr_results):
        try:
            with open(ocr_results, 'r', encoding='utf-8') as file:
                ocr_results = file.readlines()
            previous_paragraph = None
            for ocr_result in ocr_results:
                clean_text = ocr_result.strip()
                #print(clean_text)
                if previous_paragraph:
                    previous_paragraph.add_run('\n' + clean_text)
                else:
                    previous_paragraph = doc.add_paragraph(clean_text)
            os.remove(ocr_results)
        except Exception as e:
            print(f"Wystąpił błąd: {e}")

    if text_results and text_results.strip():
        doc.add_paragraph(text_results)

    doc.save(file_path)
