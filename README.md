# Youtube Video Transcription and Summarization Tool

A Python-based tool to download YouTube videos, transcribe them to text, and generate summaries using Google's Gemini AI.

Useful for creating a summary of a podcast or youtube video that don't have transcript yet.

## Features

- Download audio from YouTube videos
- Transcribe audio to text using Google Gemini AI
- Generate comprehensive summaries of transcripts
- Support for long-form content through automatic segmentation

## Prerequisites

- Python 3.12+
- Google Gemini API key
- FFmpeg (for audio processing)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/adhikasp/video-transcribe.git
   cd video-transcribe
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables by creating a `.env` file:
   ```bash
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

## Usage

### Download Audio from YouTube

```bash
python download.py <youtube_url> [--output-dir OUTPUT_DIR]
```

### Transcribe Audio to Text

```bash
python transcribe.py <audio_file_path>
```

### Generate Summary from Transcript

```bash
python summarize.py <transcript_file_path>
```

## How It Works

1. **Download**: Uses `yt-dlp` to download the best quality audio from YouTube videos and converts it to WAV format.
2. **Transcribe**: Splits audio into 5-minute segments and uses Google Gemini AI to transcribe each segment, maintaining speaker identification.
3. **Summarize**: Processes the transcript using Google Gemini AI to generate a structured summary including main topics, key points, and timeline.

## Output Files

- Audio files are saved as `.wav`
- Transcripts are saved as `.txt`
- Summaries are saved as `.summary.md`

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
