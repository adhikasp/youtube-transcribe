#!/usr/bin/env python3

import os
from pathlib import Path
import google.generativeai as genai
import argparse
import dotenv

dotenv.load_dotenv()

# Configure Google Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Please set GOOGLE_API_KEY environment variable")
genai.configure(api_key=GOOGLE_API_KEY)

def summarize_text(input_file_path):
    """
    Summarize the transcript using Google Gemini API
    
    Args:
        input_file_path (str): Path to the transcript text file
    
    Returns:
        str: Summarized text
    """
    # Initialize Gemini model
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Create output filename
    output_file = Path(input_file_path).with_suffix('.summary.md')
    
    # Read the transcript
    with open(input_file_path, 'r', encoding='utf-8') as f:
        transcript = f.read()
    
    # Create the prompt for summarization
    prompt = """
    Please provide a comprehensive summary of this transcript. Include:
    1. Main topics discussed
    2. Key points and important details
    3. Any significant conclusions or decisions
    4. Timeline of major points (if applicable)
    
    Format the summary in a clear, structured way.
    """
    
    # Generate summary with streaming enabled
    response = model.generate_content([prompt, transcript], stream=True)
    
    # Collect the summary
    summary = ""
    for chunk in response:
        if chunk.text:
            summary += chunk.text
            
    # Write summary to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(summary.strip())
    
    return summary.strip()

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Summarize transcript text file')
    parser.add_argument('input_path', type=str, help='Path to the transcript text file')
    args = parser.parse_args()

    try:
        print(f"Summarizing {args.input_path}...")
        summary = summarize_text(args.input_path)
        output_file = Path(args.input_path).with_suffix('.summary.txt')
        print("\nSummary completed!")
        print(f"Summary saved to: {output_file}")
        print(summary)
    except Exception as e:
        print(f"Error during summarization: {str(e)}")

if __name__ == "__main__":
    main() 