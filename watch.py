#!/usr/bin/env python3

import os
from pathlib import Path
import google.generativeai as genai
import argparse
import dotenv
import time
from prompt import my_prompt

dotenv.load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY", ""))

def analyze_video(video_path: str) -> str:
    """
    Analyze video content using Gemini Vision
    
    Args:
        video_path (str): Path to the video file
    
    Returns:
        str: Analysis of the video content
    """
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    output_file = Path(video_path).with_suffix('.analysis.md')
    
    print("Uploading video to Gemini...")
    # Check if file already exists in Gemini storage
    existing_files = genai.list_files()
    video_name = Path(video_path).name
    video_file = None
    for file in existing_files:
        if file.display_name == video_name:
            print(f"Found existing file {video_name}, reusing...")
            video_file = file
            break
    if video_file is None:
        print(f"Uploading new file {video_name}...")
        video_file = genai.upload_file(video_path)
    # Videos need to be processed before you can use them.
    while video_file.state.name == "PROCESSING":
        print("processing video...")
        time.sleep(2)
        video_file = genai.get_file(video_file.name)
    
    prompt = my_prompt
    print("Analyzing video with Gemini Vision...")
    try:
        response = model.generate_content([prompt, video_file], stream=True)
        
        # Collect the analysis
        analysis = ""
        for chunk in response:
            if chunk.text:
                analysis += chunk.text
                
        # Write analysis to file
        analysis = analysis.strip()
        output_file.write_text(analysis)
        print(f"Analysis saved to: {output_file}")
        
        # Cleanup
        genai.delete_file(video_file.name)
        
        return analysis
        
    except Exception as e:
        raise Exception(f"Failed to analyze video: {str(e)}")

def main():
    # Download the video first from youtube
    # yt-dlp -f "bestvideo[height<=480]+bestaudio/best[height<=480]" https://www.youtube.com/watch?v=jAX9PORnevM

    parser = argparse.ArgumentParser(description='Analyze video content using Gemini Vision')
    parser.add_argument('video_path', help='Path to the video file')
    
    args = parser.parse_args()
    try:
        print(f"\nAnalyzing video: {args.video_path}")
        analysis = analyze_video(args.video_path)
        print("\nAnalysis completed successfully!\n\n")
        print(analysis)
    except Exception as e:
        print(f"Analysis failed: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 