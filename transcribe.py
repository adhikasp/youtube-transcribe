#!/usr/bin/env python3

import os
from pathlib import Path
import google.generativeai as genai
import argparse
import dotenv
from pydub import AudioSegment
import tempfile

dotenv.load_dotenv()

# Configure Google Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Please set GOOGLE_API_KEY environment variable")
genai.configure(api_key=GOOGLE_API_KEY)

def transcribe_audio(audio_file_path):
    """
    Transcribe audio file to text using Google Gemini API
    
    Args:
        audio_file_path (str): Path to the audio file
    
    Returns:
        str: Transcribed text
    """
    # Initialize Gemini model
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Create output filename from input audio path
    output_file = Path(audio_file_path).with_suffix('.txt')
    # Clean output file if it exists
    if output_file.exists():
        output_file.unlink()
    
    # Load audio file
    audio = AudioSegment.from_file(audio_file_path)
    
    # Split into 5-minute segments (300000 milliseconds)
    segment_length = 300000  # 5 minutes
    segments = []
    
    for i in range(0, len(audio), segment_length):
        segment = audio[i:i + segment_length]
        segments.append(segment)
    
    full_transcript = ""
    
    # Process each segment
    for i, segment in enumerate(segments):
        print(f"Processing segment {i+1}/{len(segments)}...")
        
        # Save segment to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            segment.export(temp_file.name, format='wav')
            
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
            
            # Append segment transcript to full transcript
            full_transcript += segment_transcript + " "
            
            # Write ongoing progress to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(full_transcript.strip())
            print(f"Progress saved to {output_file}")
    
    return full_transcript.strip()

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Transcribe audio file to text')
    parser.add_argument('audio_path', type=str, help='Path to the audio file')
    args = parser.parse_args()

    try:
        transcribed_text = transcribe_audio(args.audio_path)
        print("\nTranscription completed!")
        print(f"Full transcript saved to: {Path(args.audio_path).with_suffix('.txt')}")
    except Exception as e:
        print(f"Error during transcription: {str(e)}")

if __name__ == "__main__":
    main()
