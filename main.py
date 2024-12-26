#!/usr/bin/env python3

import argparse
from pathlib import Path
import sys
import os

from download import download_audio
from transcribe import transcribe_audio
from summarize import summarize_text

def cleanup_files(*file_paths: str):
    """
    Remove the specified files if they exist
    
    Args:
        *file_paths: Variable number of file paths to remove
    """
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Cleaned up: {file_path}")
        except Exception as e:
            print(f"Warning: Failed to remove {file_path}: {str(e)}", file=sys.stderr)

def process_video(url: str, output_dir: str = None) -> str:
    """
    Process a YouTube video: download audio, transcribe, and generate summary
    
    Args:
        url (str): YouTube video URL
        output_dir (str, optional): Directory to save output files
    
    Returns:
        str: Path to the final summary file
    """
    print(f"\n=== Starting to process video: {url} ===\n")
    
    try:
        # Step 1: Download audio
        print("Step 1: Downloading audio...")
        audio_path = download_audio(url, output_dir)
        print(f"Audio downloaded successfully: {audio_path}\n")
        
        # Step 2: Transcribe audio
        print("Step 2: Transcribing audio...")
        transcript = transcribe_audio(audio_path)
        transcript_path = Path(audio_path).with_suffix('.txt')
        print(f"Transcription completed: {transcript_path}\n")
        
        # Step 3: Generate summary
        print("Step 3: Generating summary...")
        summary = summarize_text(transcript_path)
        summary_path = transcript_path.with_suffix('.summary.md')
        print(f"Summary generated: {summary_path}\n")
        
        # Step 4: Cleanup intermediate files
        print("Step 4: Cleaning up intermediate files...")
        cleanup_files(audio_path, str(transcript_path))
        
        print("\n=== Processing completed successfully! ===")
        print(f"Summary file saved to: {summary_path}")
        print(f"\n{summary}")
        
        return str(summary_path)
        
    except Exception as e:
        print(f"\nError during processing: {str(e)}", file=sys.stderr)
        raise

def main():
    parser = argparse.ArgumentParser(
        description='Download, transcribe, and summarize a YouTube video'
    )
    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument(
        '--output-dir', 
        '-o', 
        help='Output directory (optional)'
    )
    parser.add_argument(
        '--keep-files',
        action='store_true',
        help='Keep intermediate files (audio and transcript)'
    )
    args = parser.parse_args()
    
    try:
        summary_path = process_video(args.url, args.output_dir)
        if args.keep_files:
            print("\nIntermediate files were kept as requested.")
    except Exception as e:
        print(f"Failed to process video: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 