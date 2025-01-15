import pytesseract # type: ignore
from PIL import Image
import os

def perform_ocr_on_frames(frame_paths, output_file="uploads/ocr_results.txt", lang="pol"):
    """
    Wykonuje OCR na każdej klatce i aktualizuje plik tekstowy z wynikami.
    """
    output_dir = os.path.dirname(output_file)
    # Tworzenie folderu, jeśli nie istnieje
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
              
    extracted_texts = {}

    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            extracted_texts = {line.split(":", 1)[0]: line.split(":", 1)[1].strip() for line in f if ":" in line}

    for frame_path in frame_paths:
        frame_name = os.path.basename(frame_path)
        if frame_name in extracted_texts:
            continue  # Pomijaj już przetworzone klatki

        try:
            img = Image.open(frame_path)
            text = pytesseract.image_to_string(img, lang=lang)
            extracted_texts[frame_name] = text.strip()
            print(f"Extracted text from {frame_path}")

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"{frame_name}: {text.strip()}\n")

        except Exception as e:
            print(f"Error extracting text from {frame_path}: {e}")
    return output_file