import pytesseract
from PIL import Image
import os
from dotenv import load_dotenv
from groq import Groq

def validate_text_with_groq(text, client):
    """
    Sprawdza tekst przez Groq API aby upewnić się, że zawiera sensowne słowa/zdania.
    """
    if not text.strip():
        return ""
        
    prompt = f"""Przeanalizuj poniższy tekst i zwróć tylko sensowne słowa i zdania w języku polskim lub angielskim.
    Jeśli widzisz literówkę to ją popraw. 
    Jeśli tekst nie zawiera sensownych słów, zwróć pustą linię.
    Output ma być w takim samym formacie jak go dostałeś
    
    Tekst do analizy: {text}
    """
    
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error during Groq API validation: {e}")
        return ""

def perform_ocr_on_frames(frame_paths, output_file="uploads/ocr_results.txt", lang="pol"):
    """
    Wykonuje OCR na każdej klatce, waliduje tekst przez Groq i zapisuje sensowne wyniki.
    """
    # Inicjalizacja Groq API
    load_dotenv()
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
              
    extracted_texts = {}

    # Wczytaj istniejące wyniki
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            extracted_texts = {
                line.split(":", 1)[0]: line.split(":", 1)[1].strip() 
                for line in f 
                if ":" in line
            }

    # Przetwarzaj nowe klatki
    for frame_path in frame_paths:
        frame_name = os.path.basename(frame_path)
        if frame_name in extracted_texts:
            continue  # Pomijaj już przetworzone klatki

        try:
            # Wykonaj OCR
            img = Image.open(frame_path)
            raw_text = pytesseract.image_to_string(img, lang=lang)
            
            # Waliduj tekst przez Groq API
            validated_text = validate_text_with_groq(raw_text, client)
            
            # Zapisz tylko jeśli tekst przeszedł walidację
            if validated_text:
                extracted_texts[frame_name] = validated_text
                print(f"Extracted and validated text from {frame_path}")
                
                # Zapisz do pliku
                with open(output_file, "a", encoding="utf-8") as f:
                    f.write(f"{frame_name}: {validated_text}\n")
            else:
                print(f"No valid text found in {frame_path}")

        except Exception as e:
            print(f"Error processing {frame_path}: {e}")
            
    return output_file