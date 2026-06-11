import os
from whisper import audio
from streamlit import audio
import yt_dlp
from pydub import AudioSegment

DOWNLOAD_DIR = "downloads"

# Ensure the download directory exists
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> tuple[str, str]:
    """
    Downloads a YouTube audio stream and produces two WAV files:
    1. A standard master WAV copy.
    2. A downsampled, mono WAV optimized for AI processing.
    """
    print("=" * 50)
    print("[DOWNLOAD] Starting download")
    print(f"[DOWNLOAD] URL: {url}")
    output_template = os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s')
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'noplaylist': True,       
        'no_warnings': True,      
        'quiet': True,            
        'restrictfilenames': True, 
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # 1. Download original stream (.webm / .m4a)
        info_dict = ydl.extract_info(url, download=True)
        print("[DOWNLOAD] Download completed")
        print(f"[DOWNLOAD] Title: {info_dict['title']}")
        original_file_path = ydl.prepare_filename(info_dict)
        
        # 2. Prepare targeted structural paths
        base_path, _ = os.path.splitext(original_file_path)
        original_wav_path = f"{base_path}.wav"
        converted_wav_path = f"{base_path}_converted.wav"
        
        # 3. Load into pydub
        audio = AudioSegment.from_file(original_file_path)
        
        print("[DOWNLOAD] Audio loaded successfully")
        print(
            f"[DOWNLOAD] Duration: {len(audio)/1000:.2f} sec"
        )

        print(
            f"[DOWNLOAD] Channels: {audio.channels}"
        )

        print(
            f"[DOWNLOAD] Sample Rate: {audio.frame_rate}"
        )
        
        # 4. Version A: Standard WAV copy
        audio.export(original_wav_path, format="wav")
        
        # 5. Version B: Downsampled to 16000Hz, Mono (1 channel) for AI
        converted_audio = audio.set_frame_rate(16000).set_channels(1)
        converted_audio.export(converted_wav_path, format="wav")
        
        # 6. Cleanup transient streaming file to save space
        if os.path.exists(original_file_path) and original_file_path != original_wav_path:
            os.remove(original_file_path)
        
    return original_wav_path, converted_wav_path


def chunk_audio_file(file_path: str, cut_strategy = None) -> list[str]:
    """
    Splits an audio file into smaller chunks based on a single parameter.
    
    cut_strategy can be:
      - None: Defaults to cutting every 10 minutes.
      - float/int: Cuts the audio into equal intervals of that many minutes.
      - list of float/int: Cuts the audio at those exact timestamp markers (in minutes).
    """
    audio = AudioSegment.from_file(file_path)
    print("=" * 50)
    print("[CHUNKING] Started")

    print(
        f"[CHUNKING] Total Length: "
        f"{len(audio)/1000:.2f} sec"
    )
    total_duration_ms = len(audio)
    chunks_paths = []
    
    base_name = os.path.splitext(file_path)[0]
    cut_timestamps_ms = [0] 
    
    # Strategy 1: Specific cut timestamps
    if isinstance(cut_strategy, list):
        for pt in sorted(cut_strategy):
            ms_point = int(pt * 60 * 1000)
            if ms_point < total_duration_ms:
                cut_timestamps_ms.append(ms_point)
                
    # Strategy 2: Equal duration intervals
    elif isinstance(cut_strategy, (int, float)):
        chunk_length_ms = int(cut_strategy * 60 * 1000)
        for ms_point in range(chunk_length_ms, total_duration_ms, chunk_length_ms):
            cut_timestamps_ms.append(ms_point)
            
    # Strategy 3: Default 10-minute intervals
    else:
        default_chunk_length_ms = 10 * 60 * 1000  
        for ms_point in range(default_chunk_length_ms, total_duration_ms, default_chunk_length_ms):
            cut_timestamps_ms.append(ms_point)
            
    cut_timestamps_ms.append(total_duration_ms)
    
    # Execute Slicing
    for index in range(len(cut_timestamps_ms) - 1):
        start_ms = cut_timestamps_ms[index]
        end_ms = cut_timestamps_ms[index + 1]
        
        if start_ms == end_ms:
            continue
        print(
    f"[CHUNK {index+1}] "
    f"Start={start_ms/1000:.1f}s "
    f"End={end_ms/1000:.1f}s "
    f"Duration={(end_ms-start_ms)/1000:.1f}s"
)    
        chunk = audio[start_ms:end_ms]
        chunk_filename = f"{base_name}_chunk_{index + 1}.wav"
        chunk.export(chunk_filename, format="wav")
        print(
            f"[CHUNK {index+1}] Saved -> "
            f"{chunk_filename}"
        )
        chunks_paths.append(chunk_filename)
        
    return chunks_paths


# --- Single execution chain running both functions together ---
if __name__ == "__main__":
    # 1. Define the one single link to process
    target_url = "https://www.youtube.com/watch?v=iixoHNA_pqQ"
    
    print("Step 1: Downloading and converting YouTube track...")
    # 2. Trigger download (Returns paths: master wav, and whisper-ready wav)
    master_wav, ai_ready_wav = download_youtube_audio(target_url)
    
    print(f"-> Master WAV created: {master_wav}")
    print(f"-> AI-Ready WAV created: {ai_ready_wav}\n")
    
    print("Step 2: Splitting the AI-ready audio file into chunks...")
    # 3. Pass the *ai_ready_wav* directly into the chunking mechanism
    # (Change cut_strategy here as you wish: e.g. None, 3, or [1.5, 4.5])
    generated_chunks = chunk_audio_file(ai_ready_wav, cut_strategy=10)
    
    # 4. Summary Output
    print("\n--- Pipeline Complete! ---")
    print(f"Total Chunks Created: {len(generated_chunks)}")
    for chunk in generated_chunks:
        print(f" Saved chunk: {chunk}")