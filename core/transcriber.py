import whisper
import os
import time
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")
start = time.time()

_model = None


def load_model():

    global _model  

    if _model is None: 
        print("=" * 50)
        print("[MODEL] Loading Whisper")
        print(f"[MODEL] Model Name: {WHISPER_MODEL}")
        _model = whisper.load_model(WHISPER_MODEL) 
        print(
    f"[MODEL] Loaded in "
    f"{time.time()-start:.2f} sec"
)
        print("Whisper model loaded.")
    return _model 


import time
import os

def transcribe_chunk_whisper(chunk_path: str) -> str:

    model = load_model()

    print("=" * 50)
    print("[TRANSCRIBE] Starting")

    print(
        f"[TRANSCRIBE] File: "
        f"{os.path.basename(chunk_path)}"
    )

    start = time.time()

    print(">>> ENTERING model.transcribe()")

    result = model.transcribe(
        chunk_path,
        task="transcribe",
        verbose=True
    )

    print("<<< EXITING model.transcribe()")

    elapsed = time.time() - start

    print(
        f"[TRANSCRIBE] Completed "
        f"in {elapsed:.2f} sec"
    )

    return result["text"]
def transcribe_all(chunks: list) -> str:

    full_transcript = "" 

    print("Using Whisper for local transcription.")

    for i, chunk in enumerate(chunks):  
        print(f"Transcribing chunk {i + 1}/{len(chunks)}...")
        print("=" * 50)
        print(
              f"[PIPELINE] Chunk "
              f"{i+1}/{len(chunks)}"
              )
        print(
              f"[PIPELINE] Processing: "
              f"{chunk}"
              )
        text = transcribe_chunk_whisper(chunk)  
        print(f"[PIPELINE] Chunk "f"{i+1}/{len(chunks)} Finished")
        full_transcript += text + " "  

    print("Transcription complete.")

    return full_transcript.strip()  