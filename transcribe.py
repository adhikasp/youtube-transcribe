#!/usr/bin/env python3

import os
from pathlib import Path
import google.generativeai as genai
import argparse
import dotenv
from pydub import AudioSegment
import tempfile
import concurrent.futures
from dataclasses import dataclass
import time

dotenv.load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY", ""))

@dataclass
class Segment:
    """Audio segment with its position in sequence"""
    index: int
    text: str = ""
    audio: AudioSegment = None

def transcribe_segment(segment: Segment, retries: int = 10) -> str:
    """Transcribe an audio segment with retry logic"""
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    prompt = "Please transcribe this audio segment completely. Add the speaker name or identifier for each sentence."
    
    # Keep original audio data for retries
    audio_data = segment.audio
    
    for attempt in range(retries):
        temp = None
        try:
            temp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            audio_data.export(temp.name, format='wav')
            audio_file = genai.upload_file(temp.name)
            
            response = model.generate_content([prompt, audio_file], stream=True)
            transcript = "".join(chunk.text for chunk in response if chunk.text)
            
            # Cleanup
            genai.delete_file(audio_file.name)
            
            # Clear audio data only after successful transcription
            segment.audio = None
            return transcript.strip()
            
        except Exception as e:
            if attempt == retries - 1:
                raise Exception(f"Failed to transcribe segment {segment.index + 1}") from e
            
            delay = 2 ** attempt
            print(f"Segment {segment.index + 1} failed (attempt {attempt + 1}/{retries}). Error: {str(e)}. Retrying in {delay}s...")
            time.sleep(delay)
        finally:
            # Ensure temp file is always cleaned up
            if temp:
                try:
                    temp.close()
                    os.unlink(temp.name)
                except:
                    pass

def transcribe_audio(audio_path: str, max_workers: int = 3) -> str:
    """Transcribe audio file to text using parallel processing"""
    # Prepare input/output
    audio = AudioSegment.from_file(audio_path)
    output_file = Path(audio_path).with_suffix('.txt')
    
    # Split audio into 5-minute segments
    segments = []
    segment_duration = 5 * 60 * 1000  # 5 minutes in milliseconds
    
    for i, pos in enumerate(range(0, len(audio), segment_duration)):
        # Create a new AudioSegment for each segment to avoid memory issues
        segment_audio = audio[pos:pos + segment_duration]
        segment = Segment(i, audio=segment_audio)
        segments.append(segment)
    
    # Clear the full audio to free memory
    audio = None
    
    print(f"Processing {len(segments)} segments using {max_workers} workers...")
    
    # Process segments in parallel with better error handling
    results = []
    failed_segments = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(transcribe_segment, segment): segment for segment in segments}
        
        for future in concurrent.futures.as_completed(futures):
            segment = futures[future]
            try:
                segment.text = future.result()
                results.append(segment)
                print(f"Completed segment {segment.index + 1}/{len(segments)}")
            except Exception as e:
                print(f"Error in segment {segment.index + 1}: {str(e)}")
                failed_segments.append(segment.index + 1)
    
    if failed_segments:
        raise Exception(f"Transcription failed for segments: {failed_segments}")
    
    # Combine results and save
    transcript = "\n\n".join(segment.text for segment in sorted(results, key=lambda s: s.index))
    output_file.write_text(transcript)
    print(f"Transcript saved to {output_file}")
    
    return transcript

def main():
    parser = argparse.ArgumentParser(description='Transcribe audio file to text')
    parser.add_argument('audio_path', help='Path to the audio file')
    parser.add_argument('--max-workers', '-w', type=int, default=3,
                       help='Maximum number of parallel workers (default: 3)')
    
    args = parser.parse_args()
    try:
        transcribe_audio(args.audio_path, args.max_workers)
        print("\nTranscription completed successfully!")
    except Exception as e:
        print(f"Transcription failed: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
