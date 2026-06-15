from utils.audio_processor import download_youtube_audio, chunk_audio_file
from core.transcriber import transcribe_all

source_audio_path = "https://www.youtube.com/watch?v=XTvgJA23Vj8"
target_language = "bn" # Toggle between "en", "hi", or "bn"

print("=" * 50)
print("[MAIN] Download Step")
# 1. Download the audio locally first
_, ai_ready_wav = download_youtube_audio(source_audio_path)

# 2. Chunk the downloaded file using a 10-minute strategy
print("=" * 50)
print("[MAIN] Chunking Step")
chunks = chunk_audio_file(ai_ready_wav, cut_strategy=10)
print(
    f"[MAIN] Total Chunks: "
    f"{len(chunks)}"
)
print("=" * 50)
print("[MAIN] Transcription Step")
# Set language="en" for local Whisper, "hi" for Hindi, or "bn" for Bengali
transcript = transcribe_all(chunks, language=target_language)       
print("Final Transcript:")
print(transcript)