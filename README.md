# Conversational Audio Bot

An AI-powered voice and text customer service assistant built with Streamlit, OpenAI, and LangChain.

## Features

- 🎤 **Voice Input** - Record audio or upload audio files (WAV/MP3)
- ⌨️ **Text Input** - Type messages directly
- 🔊 **Text-to-Speech** - AI responses are converted to audio
- 💬 **Conversation History** - Full chat history with context awareness
- 📊 **Conversation Analysis** - AI-powered analysis of customer interactions
- 🎯 **Multiple Modes** - Customer Service and Lead Generation personas

## Quick Start

### Prerequisites

- Python 3.10+
- Poetry (recommended) or pip
- OpenAI API key
- PortAudio (for microphone recording on Linux)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd conversational-audio-bot
   ```

2. **Install system dependencies (Linux only - for microphone support)**
   ```bash
   sudo apt-get update && sudo apt-get install -y portaudio19-dev python3-dev
   ```

3. **Install Python dependencies**
   
   Using Poetry:
   ```bash
   poetry install
   poetry shell
   ```
   
   Or using pip:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # .venv\Scripts\activate   # Windows
   pip install -e .
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your-openai-api-key-here
   SAMPLE_RATE=16000
   LLM_MODEL=gpt-4
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

   The app will open at `http://localhost:8501`

## Usage

### Voice Interaction
1. Go to the **Voice Interaction** tab
2. Click **Start Recording** to record from your microphone (requires audio device)
3. Or use **Upload audio file** to upload a WAV/MP3 file
4. The audio is transcribed and the AI responds with text and audio

### Text Interaction
1. Go to the **Text Interaction** tab
2. Type your message and press Enter
3. The AI responds with text and audio

### Conversation Analysis
1. Have a conversation first
2. Go to the **Conversation Analysis** tab
3. Click **Analyze Conversation** to get AI insights

### Settings (Sidebar)
- **Recording Duration** - Adjust recording length (5-20 seconds)
- **TTS Language** - Choose English or Chinese
- **Mode** - Switch between Customer Service and Lead Generation
- **Clear History** - Reset conversation

## Troubleshooting

### "Recording failed" / "Error querying device -1"
This means no microphone is available. Common in WSL or remote environments.
- **Solution**: Use the file upload feature or text input instead

### "Import could not be resolved" errors
Run `poetry install` or `pip install -e .` to install dependencies.

### OpenAI API key errors
Ensure your `.env` file has `OPENAI_API_KEY` (not `OPEN_AI_KEY`).

## Project Structure

```
conversational-audio-bot/
├── app.py                 # Main Streamlit application
├── utils/
│   ├── audio_utils.py     # Audio recording, processing, TTS
│   └── llm_utils.py       # LLM integration with LangChain
├── pyproject.toml         # Project dependencies (Poetry)
├── .env                   # Environment variables (create this)
├── README.md              # This file
└── ARCHITECTURE.md        # Detailed architecture documentation
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed technical documentation including:
- System architecture diagram
- Component details
- Data flow
- Configuration options

## License

See [LICENSE](LICENSE) for details.
