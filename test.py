from utils.audio_processor import download_youtube_audio, chunk_audio_file
from core.transcriber import transcribe_all
from core.extractor import extract_meeting_info
from core.summarize import summarize_transcript

source_audio_path = "https://www.youtube.com/watch?v=pMng6oKA0dc"
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

print("=" * 50)
print("[MAIN] Summarization & Title Generation")
summary_report = summarize_transcript(transcript)

print("=" * 50)
print("[MAIN] Extraction Step")
analysis = extract_meeting_info(transcript)

# Splitting the title and summary for separate printing
# The summarizer returns "# Title\n\nSummary"
report_parts = summary_report.split("\n\n", 1)
generated_title = report_parts[0].replace("# ", "").strip() if len(report_parts) > 0 else "Meeting Analysis"
final_summary = report_parts[1].strip() if len(report_parts) > 1 else summary_report

print("\n" + "="*50)
print(f"TITLE: {generated_title}")
print("="*50)
print(f"\nSUMMARY:\n{final_summary}")

print("\n" + "="*50)
print("FINAL ANALYSIS")
print("="*50)
print(analysis)


#2:13