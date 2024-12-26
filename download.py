#!/usr/bin/env python3

import os
from pathlib import Path
import argparse
import yt_dlp

def download_audio(url, output_dir=None):
    """
    Download audio from a YouTube video
    
    Args:
        url (str): YouTube video URL
        output_dir (str, optional): Directory to save the audio file
    
    Returns:
        str: Path to the downloaded audio file
    """
    if output_dir:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Configure yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best',  # Choose best quality audio
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',  # Convert to WAV for better compatibility
        }],
        'outtmpl': '%(title)s.%(ext)s',  # Output template
        'quiet': False,
        'no_warnings': False,
        'progress': True
    }
    
    # Add output directory if specified
    if output_dir:
        ydl_opts['outtmpl'] = os.path.join(output_dir, ydl_opts['outtmpl'])
    
    try:
        # Download the audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading audio from: {url}")
            info = ydl.extract_info(url, download=True)
            
            # Get the output file path
            output_file = Path(ydl.prepare_filename(info)).with_suffix('.wav')
            print(f"\nDownload completed: {output_file}")
            return str(output_file)
            
    except Exception as e:
        print(f"Error downloading audio: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Download audio from YouTube video')
    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument('--output-dir', '-o', help='Output directory (optional)')
    args = parser.parse_args()
    
    try:
        output_file = download_audio(args.url, args.output_dir)
        print(f"Audio saved to: {output_file}")
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 