import whisper
import os
import time
import requests
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

load_dotenv()
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")
start = time.time()

_model = None

SARVAM_API_KEY=os.getenv("SARVAM_API_KEY")
SARVAM_STT_MODEL=os.getenv("SARVAM_STT_MODEL", "saaras:v3")

def translate_to_english(text: str, source_lang: str = 'auto', max_retries: int = 3) -> str:
    """Helper to translate text with retries to handle transient network errors."""
    if not text or not text.strip():
        return text
    
    # Normalize language code (e.g., 'bn-IN' -> 'bn') for Google Translator
    clean_lang = source_lang.split('-')[0] if '-' in source_lang else source_lang

    for attempt in range(max_retries):
        try:
            return GoogleTranslator(source=clean_lang, target='en').translate(text)
        except Exception as e:
            print(f"[TRANSLATION ERROR] Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait 1s before retrying
    return text

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

def transcribe_chunk_sarvam(chunk_path: str, language_code: str = "hi-IN") -> str:
    """
    Sarvam's real-time endpoint allows max 30s audio per request.
    If the chunk is longer, split it into <=30s sub-chunks, transcribe
    each, and join the results.
    """
    from pydub import AudioSegment

    SARVAM_MAX_SEC = 30
    audio = AudioSegment.from_file(chunk_path)
    duration_sec = len(audio) / 1000.0

    if duration_sec > SARVAM_MAX_SEC:
        print(f"[SARVAM] Chunk {duration_sec:.1f}s exceeds {SARVAM_MAX_SEC}s, splitting...")
        sub_texts = []
        sub_len_ms = SARVAM_MAX_SEC * 1000
        total_ms = len(audio)
        base, ext = os.path.splitext(chunk_path)

        for idx, start_ms in enumerate(range(0, total_ms, sub_len_ms)):
            end_ms = min(start_ms + sub_len_ms, total_ms)
            sub_audio = audio[start_ms:end_ms]
            sub_path = f"{base}_sub_{idx + 1}{ext}"
            sub_audio.export(sub_path, format="wav")

            print(f"[SARVAM] Sub-chunk {idx + 1}: {start_ms/1000:.1f}s - {end_ms/1000:.1f}s")
            sub_text = _transcribe_chunk_sarvam_single(sub_path, language_code)
            translated_sub = translate_to_english(sub_text, source_lang=language_code)
            sub_texts.append(translated_sub)

            os.remove(sub_path)

        return " ".join(t for t in sub_texts if t).strip()

    raw_text = _transcribe_chunk_sarvam_single(chunk_path, language_code)
    return translate_to_english(raw_text, source_lang=language_code)


def _transcribe_chunk_sarvam_single(chunk_path: str, language_code: str = "hi-IN") -> str:
    if not SARVAM_API_KEY:
        print("[ERROR] SARVAM_API_KEY is missing from environment variables.")
        return ""

    url = "https://api.sarvam.ai/speech-to-text"
    headers = {"api-subscription-key": SARVAM_API_KEY}
    data = {
        "model": SARVAM_STT_MODEL,
        "language_code": language_code
    }

    print("=" * 50)
    print("[SARVAM] Starting Transcription")
    print(f"[SARVAM] File: {os.path.basename(chunk_path)}")

    start_time = time.time()
    try:
        with open(chunk_path, "rb") as f:
            files = {"file": (os.path.basename(chunk_path), f, "audio/wav")}
            response = requests.post(url, headers=headers, data=data, files=files)
            if response.status_code != 200:
                print(f"[SARVAM ERROR] {response.status_code}: {response.text}")
                return ""

            text = response.json().get("transcript", "")
            elapsed = time.time() - start_time
            print(f"[SARVAM] Completed in {elapsed:.2f} sec")
            return text
    except Exception as e:
        print(f"[SARVAM ERROR] {e}")
        return ""
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
        task="translate",
        verbose=False
    )

    print("<<< EXITING model.transcribe()")

    elapsed = time.time() - start

    print(
        f"[TRANSCRIBE] Completed "
        f"in {elapsed:.2f} sec"
    )

    return result["text"]
def transcribe_all(chunks: list, language: str = "en") -> str:

    full_transcript = "" 

    engine = "Whisper (Local)" if language.lower() == "en" else "Sarvam AI (Cloud)"
    print(f"Using {engine} for transcription.")

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
        
        if language.lower() == "en":
            text = transcribe_chunk_whisper(chunk)
        else:
            # Map common language names to Sarvam language codes
            lang_map = {
                "hi": "hi-IN", "hindi": "hi-IN", "hinglish": "hi-IN",
                "bn": "bn-IN", "bengali": "bn-IN"
            }
            
            lang_code = lang_map.get(language.lower(), language)
            text = transcribe_chunk_sarvam(chunk, language_code=lang_code)
            # text is now already translated by transcribe_chunk_sarvam

        full_transcript += text + " "  
        print(f"[PIPELINE] Chunk {i+1}/{len(chunks)} Finished")
        print("Accumulated Transcript:")
        print(full_transcript.strip())
        print("=" * 50)

    print("Transcription complete.")

    return full_transcript.strip()  