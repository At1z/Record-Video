import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("API_KEY"),
)

def send_query_to_groq(prompt, model="llama-3.3-70b-versatile"):
    """Funkcja do wysyłania zapytania do Groq i zwracania odpowiedzi."""
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model,
        )
        # Zwróć odpowiedź od modelu
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {e}"
