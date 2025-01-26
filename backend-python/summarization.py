from docx import Document
import os
from dotenv import load_dotenv
from groq import Groq

def extract_text_from_word(file_path):
    """Extract text from a Word document."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist.")

    doc = Document(file_path)
    return "\n".join(para.text for para in doc.paragraphs)

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

def send_query_to_groq(prompt, model="llama-3.3-70b-versatile"):
    """Funkcja do wysyłania zapytania do Groq i zwracania odpowiedzi."""
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Zrób z prompta podsumowanie, ma być ono po polsku i w około 10 zdaniach proszę" + prompt,
                }
            ],
            model=model,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {e}"