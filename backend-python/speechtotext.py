def convert_audio_to_text(audio_file_path, diarization_results, tolerance=0.15):
    import whisper
    model = whisper.load_model("medium")
    language = "pl"
    
    # Konwersja czasów diaryzacji na float
    processed_diarization = []
    for speaker in diarization_results:
        processed_diarization.append({
            'speaker': speaker['speaker'],
            'start': float(speaker['start_time'].replace('s', '')),
            'end': float(speaker['end_time'].replace('s', ''))
        })

    result = model.transcribe(audio_file_path, word_timestamps=True, language=language)
    text_file_path = audio_file_path.rsplit('.', 1)[0] + '_transcription_with_diarization.txt'
    transcription_text = ""  # To store the transcription with diarization
    with open(text_file_path, 'w', encoding='utf-8') as f:
        for segment in result["segments"]:
            segment_text = segment["text"]
            start_time = segment["start"]
            end_time = segment["end"]
            
            # Znajdź wszystkich mówców aktywnych w tym segmencie
            active_speakers = []
            for speaker_info in processed_diarization:
                # Sprawdź czy przedziały czasowe się nakładają
                if (start_time >= speaker_info['start'] - tolerance and 
                    start_time <= speaker_info['end'] + tolerance) or \
                   (end_time >= speaker_info['start'] - tolerance and 
                    end_time <= speaker_info['end'] + tolerance) or \
                   (start_time <= speaker_info['start'] and 
                    end_time >= speaker_info['end']):
                    active_speakers.append(speaker_info['speaker'])
            
            # Jeśli znaleziono aktywnych mówców, zapisz segment z wszystkimi mówcami
            if active_speakers:
                speakers_str = " & ".join(sorted(set(active_speakers)))
            else:
                speakers_str = "Unknown"
            
            f.write(f"{speakers_str} | {start_time:.2f}s | {end_time:.2f}s | {segment_text}\n")
            transcription_text += f"{speakers_str} | {start_time:.2f}s | {end_time:.2f}s | {segment_text}\n"

    print(f"Pomyślnie utworzono transkrypcję z diarizacją: {text_file_path}")
    return transcription_text