def convert_audio_to_text(audio_file_path, diarization_results):
    """
    Konwertuje plik audio na tekst używając modelu Whisper i dodaje wyniki diarizacji,
    tworząc plik tekstowy z informacjami o speakerze, czasie i treści mowy.
    
    Args:
        audio_file_path (str): Ścieżka do pliku audio (wav)
        diarization_results (list): Lista wyników diarizacji zawierająca informacje o speakerze, czasie startu i końca
    
    Returns:
        str: Ścieżka do wygenerowanego pliku tekstowego
    """
    try:
        import whisper
        
        # Ładowanie modelu Whisper
        model = whisper.load_model("base")
        
        # Transkrypcja pliku audio
        result = model.transcribe(audio_file_path)
        
        # Tworzenie pliku tekstowego
        text_file_path = audio_file_path.rsplit('.', 1)[0] + '_transcription.txt'
        
        with open(text_file_path, 'w', encoding='utf-8') as f:
            # Przechodzimy przez wyniki diarizacji i zapisujemy odpowiednie dane
            for i, segment in enumerate(result["segments"]):
                # Sprawdzamy, do którego mówcy należy segment
                segment_text = segment["text"]
                speaker_info = diarization_results[i] if i < len(diarization_results) else {}
                speaker = speaker_info.get("speaker", "Unknown")
                start_time = speaker_info.get("start_time", "Unknown")
                end_time = speaker_info.get("end_time", "Unknown")
                
                # Zapisanie w formacie: speaker | start | end | text
                f.write(f"{speaker} | {start_time} | {end_time} | {segment_text}\n")
            
        print(f"Pomyślnie utworzono transkrypcję z diarizacją: {text_file_path}")
        return text_file_path
        
    except Exception as e:
        print(f"Wystąpił błąd podczas transkrypcji: {e}")
        raise
