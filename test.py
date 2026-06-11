from utils.audio_processor import download_youtube_audio, chunk_audio_file
from core.transcriber import transcribe_all

source_audio_path = "https://www.youtube.com/watch?v=3ymvdLPf7y0"

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
transcript = transcribe_all(chunks)       
print("Final Transcript:")
print(transcript)