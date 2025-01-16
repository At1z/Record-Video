import requests
from doc import extract_text_from_word

def send_summary_to_grocka(api_url, api_key, summary_text):
    """Funkcja do wysyłania podsumowania do API Grocka."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "summary": summary_text
    }
    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 200:
        print("Summary sent successfully")
    else:
        print(f"Failed to send summary: {response.status_code} - {response.text}")

# Przykład użycia
file_path = ".docx"
api_url = "https://api.grocka.com/summary"
api_key = "your_api_key"

# Wyodrębnij tekst z dokumentu Word
summary_text = extract_text_from_word(file_path)

# Wyślij podsumowanie do API Grocka
send_summary_to_grocka(api_url, api_key, summary_text)

#nieskonczona robota