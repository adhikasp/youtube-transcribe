#!/usr/bin/env python3

import os
from pathlib import Path
import google.generativeai as genai
import argparse
import dotenv
from pydub import AudioSegment
import tempfile
import concurrent.futures
from typing import List, Tuple
from dataclasses import dataclass

dotenv.load_dotenv()

# Configure Google Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Please set GOOGLE_API_KEY environment variable")
genai.configure(api_key=GOOGLE_API_KEY)

@dataclass
class TranscriptionSegment:
    """A segment of transcription with its order index"""
    index: int
    text: str

def transcribe_segment(segment_data: Tuple[int, AudioSegment]) -> TranscriptionSegment:
    """
    Transcribe a single audio segment
    
    Args:
        segment_data: Tuple of (segment_index, audio_segment)
    
    Returns:
        TranscriptionSegment: Transcribed text with its order index
    """
    index, segment = segment_data
    print(f"Processing segment {index+1}...")
    
    # Initialize Gemini model for this segment
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Save segment to temporary file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        segment.export(temp_file.name, format='wav')
        
        try:
            # Upload and transcribe segment
            audio_file = genai.upload_file(temp_file.name)
            prompt = "Please transcribe this audio segment completely. Add the speaker name or identifier for each sentence."
            
            response = model.generate_content([prompt, audio_file], stream=True)
            
            # Collect segment transcript
            segment_transcript = ""
            for chunk in response:
                if chunk.text:
                    segment_transcript += chunk.text
            
            # Clean up
            genai.delete_file(audio_file.name)
            os.unlink(temp_file.name)
            
            return TranscriptionSegment(index, segment_transcript.strip())
            
        except Exception as e:
            print(f"Error processing segment {index+1}: {str(e)}")
            raise
        finally:
            # Ensure temp file is deleted even if an error occurs
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)

def transcribe_audio(audio_file_path: str, max_workers: int = 3) -> str:
    """
    Transcribe audio file to text using Google Gemini API
    
    Args:
        audio_file_path (str): Path to the audio file
        max_workers (int, optional): Maximum number of parallel workers. Defaults to 3.
    
    Returns:
        str: Transcribed text
    """
    # Create output filename from input audio path
    output_file = Path(audio_file_path).with_suffix('.txt')
    # Clean output file if it exists
    if output_file.exists():
        output_file.unlink()
    
    # Load audio file
    print("Loading audio file...")
    audio = AudioSegment.from_file(audio_file_path)
    
    # Split into 5-minute segments (300000 milliseconds)
    segment_length = 300000  # 5 minutes
    segments = []
    
    for i in range(0, len(audio), segment_length):
        segment = audio[i:i + segment_length]
        segments.append((len(segments), segment))
    
    print(f"Split audio into {len(segments)} segments")
    print(f"Using {max_workers} parallel workers")
    
    # Process segments in parallel
    transcribed_segments: List[TranscriptionSegment] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all segments for processing
        future_to_segment = {
            executor.submit(transcribe_segment, segment_data): segment_data[0]
            for segment_data in segments
        }
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_segment):
            segment_index = future_to_segment[future]
            try:
                result = future.result()
                transcribed_segments.append(result)
                print(f"Completed segment {segment_index+1}/{len(segments)}")
            except Exception as e:
                print(f"Segment {segment_index+1} failed: {str(e)}")
                raise
    
    # Sort segments by index and combine
    transcribed_segments.sort(key=lambda x: x.index)
    full_transcript = "\n\n".join(segment.text for segment in transcribed_segments)
    
    # Write transcript to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_transcript.strip())
    print(f"Full transcript saved to {output_file}")
    
    return full_transcript.strip()

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Transcribe audio file to text')
    parser.add_argument('audio_path', type=str, help='Path to the audio file')
    parser.add_argument(
        '--max-workers',
        '-w',
        type=int,
        default=3,
        help='Maximum number of parallel workers (default: 3)'
    )
    args = parser.parse_args()

    try:
        transcribed_text = transcribe_audio(args.audio_path, args.max_workers)
        print("\nTranscription completed!")
        print(f"Full transcript saved to: {Path(args.audio_path).with_suffix('.txt')}")
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
