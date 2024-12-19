def convert_audio_to_text(audio_file_path, diarization_results, tolerance=0.5):
    """
    Konwertuje plik audio na tekst używając modelu Whisper i dodaje wyniki diarizacji,
    tworząc plik tekstowy z informacjami o speakerze, czasie i treści mowy.
    
    Args:
        audio_file_path (str): Ścieżka do pliku audio (wav)
        diarization_results (list): Lista wyników diarizacji zawierająca informacje o speakerze, czasie startu i końca
        tolerance (float): Margines czasowy do dopasowania segmentów (w sekundach)
    
    Returns:
        str: Ścieżka do wygenerowanego pliku tekstowego
    """
    try:
        import whisper
        # Ładowanie modelu Whisper
        model = whisper.load_model("base")

        ## Można zmienić na "en"
        language = "pl" 
        
        # Transkrypcja pliku audio z włączonymi znacznikami czasowymi
        result = model.transcribe(audio_file_path, word_timestamps=True, language = language)

        # Utworzenie ścieżki do pliku wynikowego
        text_file_path = audio_file_path.rsplit('.', 1)[0] + '_transcription_with_diarization.txt'

        with open(text_file_path, 'w', encoding='utf-8') as f:
            for segment in result["segments"]:
                segment_text = segment["text"]
                start_time = segment["start"]
                end_time = segment["end"]

                # Przypisanie segmentu do mówcy z tolerancją
                speaker_info = None
                for speaker in diarization_results:
                    # Ensure start_time and end_time are floats
                    try:
                        speaker_start_time = float(speaker['start_time'].replace('s', ''))
                        speaker_end_time = float(speaker['end_time'].replace('s', ''))
                    except ValueError:
                        # In case there's an issue with the conversion, skip this speaker
                        continue
                    
                    if speaker_start_time - tolerance <= start_time <= speaker_end_time + tolerance:
                        speaker_info = speaker
                        break
                
                speaker = speaker_info['speaker'] if speaker_info else 'Unknown'
                
                # Zapisujemy wyniki w pliku: speaker | start_time | end_time | text
                f.write(f"{speaker} | {start_time:.2f}s | {end_time:.2f}s | {segment_text}\n")
        
        print(f"Pomyślnie utworzono transkrypcję z diarizacją: {text_file_path}")
        return text_file_path
    
    except Exception as e:
        print(f"Wystąpił błąd podczas transkrypcji: {e}")
        raise
