from pathlib import Path
from pyannote.audio import Pipeline
import os

def load_pipeline_from_pretrained(path_to_config: str | Path) -> Pipeline:
    path_to_config = Path(path_to_config)

    print(f"Loading pyannote pipeline from {path_to_config}...")

    # Store current working directory
    cwd = Path.cwd().resolve()

    # Navigate to the directory containing the config file
    cd_to = path_to_config.parent.resolve()

    print(f"Expected directory to change to: {cd_to}")
    if not cd_to.exists():
        raise FileNotFoundError(f"Directory does not exist: {cd_to}")

    print(f"Changing working directory to {cd_to}")
    os.chdir(cd_to)

    # Load the pipeline
    pipeline = Pipeline.from_pretrained(path_to_config)

    print(f"Changing working directory back to {cwd}")
    os.chdir(cwd)

    return pipeline

PATH_TO_CONFIG = "C:/Users/nosta/Desktop/5sem/IO/Projekt/Record-Video/backend-python/models/pyannote_diarization_config.yaml"
pipeline = load_pipeline_from_pretrained(PATH_TO_CONFIG)


def diarize_audio(wav_file_path):
    # Wczytanie pliku audio przy użyciu pipeline
    diarization = pipeline(wav_file_path)

    # Przechodzenie po wynikach diarizacji i drukowanie wyników
    results = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        results.append(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")
    
    # Zwrócenie wyników jako lista
    return results
