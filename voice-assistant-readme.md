# Voice Assistant - Installation Guide

A self-hosted voice assistant with customizable speech-to-text and text-to-speech APIs.

## Quick Install (Windows)

### Method 1: One-Click Installer (Recommended)

1. **Download these files to a folder:**
   - `install.bat` (the installer)
   - `voice-assistant.py` (the main program)

2. **Run the installer:**
   - Right-click `install.bat`
   - Select "Run as administrator" (recommended)
   - Follow the prompts

3. **Launch the application:**
   - Double-click `launch.bat`
   - Or use the desktop shortcut (if created)

The installer will:
- Check for Python and install it if needed
- Install all required dependencies
- Create a launcher script
- Optionally create a desktop shortcut

### Method 2: Manual Installation

If you prefer to install manually or the automatic installer doesn't work:

1. **Install Python 3.8 or higher:**
   - Download from [python.org](https://www.python.org/downloads/)
   - **Important:** Check "Add Python to PATH" during installation

2. **Install dependencies:**
   ```bash
   pip install SpeechRecognition pyttsx3 requests pyaudio pydub
   ```

   If `pyaudio` fails:
   ```bash
   pip install pipwin
   pipwin install pyaudio
   ```

3. **Run the application:**
   ```bash
   python voice-assistant.py
   ```

## Configuration

### First-Time Setup

1. **For LM Studio (Local LLM):**
   - API URL: `http://127.0.0.1:1234/v1/chat/completions`
   - API Key: `not-needed`
   - Model: `local-model`

2. **For OpenAI:**
   - API URL: `https://api.openai.com/v1/chat/completions`
   - API Key: Your OpenAI API key
   - Model: `gpt-4` or `gpt-3.5-turbo`

3. **Click "Save Config"**

### Speech Detection Settings

Adjust these sliders to fine-tune when the assistant stops listening:

- **Pause Threshold** (0.3-2.0s): Silence duration after speech before stopping
  - Lower = more responsive, may cut you off
  - Higher = waits longer, won't interrupt
  - Recommended: 0.8s

- **Phrase Threshold** (0.1-1.0s): Minimum speech length to process
  - Filters out very short sounds
  - Recommended: 0.3s

- **Non-speaking Duration** (0.1-1.0s): Silence before listening starts
  - Helps filter background noise
  - Recommended: 0.5s

### Custom Speech APIs (Optional)

#### Speech-to-Text (STT)
If you want to use your own speech recognition API instead of Google:

1. Check "Use Custom Speech API"
2. Enter your API endpoint (e.g., `http://127.0.0.1:8000/v1/audio/transcriptions`)
3. Enter API key if required
4. Click "Save Config"

**Expected API format:**
- Method: POST
- Content-Type: multipart/form-data
- Fields: `file` (audio.wav), `model` (whisper-1)
- Response: `{"text": "transcribed text"}`

#### Text-to-Speech (TTS)
If you want to use your own TTS API instead of the built-in voice:

1. Check "Use Custom TTS API"
2. Enter your API endpoint (e.g., `http://127.0.0.1:8000/v1/audio/speech`)
3. Enter API key if required
4. Enter voice name (e.g., `alloy`, `echo`, etc.)
5. Click "Save Config"

**Expected API format:**
- Method: POST
- Content-Type: application/json
- Body: `{"model": "tts-1", "input": "text", "voice": "alloy"}`
- Response: Audio file (MP3/WAV)

## Usage

### Single Question Mode
1. Click "🎤 Listen Once"
2. Speak your question
3. Wait for the response

### Continuous Conversation Mode
1. Click "🔄 Continuous Mode"
2. The assistant will keep listening after each response
3. Click "⏹ Stop Continuous" to exit

### Stop Speaking
- Click "⏹ Stop Speaking" to interrupt the current response

## Troubleshooting

### Python not found
- Make sure Python is installed and added to PATH
- Restart your computer after installing Python
- Re-run `install.bat`

### PyAudio installation fails
- Try: `pip install pipwin` then `pipwin install pyaudio`
- Or download wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)

### Microphone not working
- Check Windows microphone permissions
- Settings → Privacy → Microphone → Allow apps to access microphone

### No sound output
- Check your default audio device in Windows
- Try restarting the application

### API connection errors
- Verify the API URL is correct
- Check that your local server (LM Studio, etc.) is running
- Check firewall settings

### Google Speech Recognition errors
- Requires internet connection
- May have usage limits
- Consider using a custom STT API for unlimited local use

## Self-Hosted Setup

For complete privacy, you can run everything locally:

1. **LLM**: Use LM Studio, Ollama, or similar
2. **STT**: Use Whisper API (various implementations available)
3. **TTS**: Use Coqui TTS, Piper, or similar

This gives you a fully offline, private voice assistant!

## Files Included

- `voice-assistant.py` - Main application
- `install.bat` - Automatic installer
- `launch.bat` - Created by installer to launch the app
- `README.md` - This file

## System Requirements

- Windows 10/11 (or Linux/Mac with manual setup)
- Python 3.8 or higher
- Microphone
- Speakers or headphones
- 100MB free disk space

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Ensure all dependencies are installed
3. Check console output for error messages

## License

Free to use and modify for personal or commercial use.
