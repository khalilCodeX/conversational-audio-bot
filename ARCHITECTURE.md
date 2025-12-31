# Architecture Overview

This document describes the architecture of the Conversational Audio Bot application.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              STREAMLIT UI (app.py)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────────────┐  │
│  │    Voice    │  │    Text     │  │         Conversation                │  │
│  │ Interaction │  │ Interaction │  │           Analysis                  │  │
│  └──────┬──────┘  └──────┬──────┘  └─────────────────┬───────────────────┘  │
└─────────┼────────────────┼───────────────────────────┼──────────────────────┘
          │                │                           │
          ▼                │                           │
┌─────────────────────┐    │                           │
│   AudioProcessor    │    │                           │
│  (audio_utils.py)   │    │                           │
├─────────────────────┤    │                           │
│ • record_audio()    │    │                           │
│ • preprocess_audio()│    │                           │
│ • transcribe_audio()├────┼───────────────────────────┤
│ • text_to_speech()  │    │                           │
└─────────┬───────────┘    │                           │
          │                │                           │
          │                ▼                           ▼
          │         ┌─────────────────────────────────────┐
          │         │          LLMProcessor               │
          │         │         (llm_utils.py)              │
          │         ├─────────────────────────────────────┤
          │         │ • generate_response()               │
          │         │ • customize_for_call_center()       │
          │         │ • customize_for_lead_generation()   │
          │         │ • analyze_conversation()            │
          │         └─────────────────┬───────────────────┘
          │                           │
          ▼                           ▼
┌─────────────────────┐    ┌─────────────────────────────┐
│   OpenAI Whisper    │    │    OpenAI GPT-4 (LangChain) │
│   (Speech-to-Text)  │    │    (Chat Completions)       │
└─────────────────────┘    └─────────────────────────────┘
```

## Component Details

### 1. Main Application (`app.py`)

The entry point and UI layer built with Streamlit.

**Responsibilities:**
- Render the web interface with tabs (Voice, Text, Analysis)
- Manage session state (messages, settings)
- Coordinate between AudioProcessor and LLMProcessor
- Display conversation history and audio visualizations

**Key Functions:**
| Function | Description |
|----------|-------------|
| `main()` | Application entry point, renders UI |
| `handle_audio_input()` | Records audio, transcribes, gets AI response |
| `handle_uploaded_audio()` | Processes uploaded audio files |
| `handle_llm_response()` | Sends text to LLM, plays TTS response |
| `handle_text_input()` | Handles text input with Enter key |
| `display_conversation_history()` | Renders chat messages |
| `settings_section()` | Sidebar settings panel |
| `visualize_audio()` | Displays audio waveform |

**Session State:**
```python
st.session_state.messages           # Conversation history
st.session_state.recording_duration # Recording length (seconds)
st.session_state.tts_lang          # TTS language (en/zh)
st.session_state.mode              # customer_service / lead_generation
```

---

### 2. Audio Processor (`utils/audio_utils.py`)

Handles all audio-related operations.

**Class: `AudioProcessor`**

| Method | Input | Output | Description |
|--------|-------|--------|-------------|
| `__init__()` | `sample_rate` | - | Initialize with sample rate (default: 16000 Hz) |
| `record_audio()` | `duration` | `str` (path) | Record from microphone, save WAV |
| `preprocess_audio()` | `audio_path` | `str` (path) | Resample, normalize, convert to mono |
| `transcribe_audio()` | `audio_path` | `str` (text) | Transcribe using OpenAI Whisper |
| `text_to_speech()` | `text`, `lang` | `str` (path) | Convert text to speech using gTTS |
| `cleanup()` | - | - | Remove temporary files |

**External Dependencies:**
- `sounddevice` - Microphone recording
- `soundfile` - Audio file I/O
- `librosa` - Audio preprocessing
- `openai` - Whisper API for transcription
- `gTTS` - Google Text-to-Speech

**Data Flow:**
```
Microphone/File → record/load → preprocess → transcribe → text
Text → gTTS → MP3 file → play in browser
```

---

### 3. LLM Processor (`utils/llm_utils.py`)

Handles all LLM interactions using LangChain.

**Class: `LLMProcessor`**

| Method | Input | Output | Description |
|--------|-------|--------|-------------|
| `__init__()` | `model_name`, `temperature` | - | Initialize ChatOpenAI |
| `generate_response()` | `prompt`, `conversation_history`, `system_prompt` | `str` | Generate AI response |
| `customize_for_call_center()` | - | - | Set customer service persona |
| `customize_for_lead_generation()` | - | - | Set sales persona |
| `analyze_conversation()` | `conversation_history` | `dict` | Extract insights from conversation |

**Message Format:**
```python
conversation_history = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"},
]
```

**LangChain Message Types:**
- `SystemMessage` - Sets AI behavior/persona
- `HumanMessage` - User messages
- `AIMessage` - Assistant responses

---

## Data Flow

### Voice Input Flow
```
1. User clicks "Start Recording"
2. AudioProcessor.record_audio() → WAV file
3. AudioProcessor.preprocess_audio() → Normalized WAV
4. AudioProcessor.transcribe_audio() → Text (via Whisper)
5. LLMProcessor.generate_response() → AI response text
6. AudioProcessor.text_to_speech() → MP3 audio
7. Display text + play audio in UI
```

### Text Input Flow
```
1. User types message + Enter
2. LLMProcessor.generate_response() → AI response text
3. AudioProcessor.text_to_speech() → MP3 audio
4. Display text + play audio in UI
```

---

## Configuration

### Environment Variables (`.env`)
```env
OPENAI_API_KEY=sk-...     # Required: OpenAI API key
SAMPLE_RATE=16000         # Audio sample rate in Hz
LLM_MODEL=gpt-4           # Model name for chat
```

### Key Dependencies (`pyproject.toml`)
| Package | Purpose |
|---------|---------|
| `streamlit` | Web UI framework |
| `langchain` | LLM orchestration |
| `langchain-openai` | OpenAI integration |
| `openai` | Whisper API |
| `sounddevice` | Microphone recording |
| `librosa` | Audio processing |
| `gTTS` | Text-to-speech |

---

## Modes

### Customer Service Mode
- Professional, helpful tone
- Focuses on resolving issues
- Offers escalation to human agents

### Lead Generation Mode
- Friendly, sales-oriented tone
- Collects customer information
- Suggests next steps (demos, follow-ups)

---

## Limitations

1. **Microphone Access** - Requires local audio device; won't work in WSL/remote without config
2. **API Costs** - Uses OpenAI APIs (GPT-4, Whisper) which have usage costs
3. **TTS Quality** - gTTS is free but lower quality than paid alternatives
4. **No Persistence** - Conversation history is lost on page refresh

---

## Future Improvements

- [ ] Add database for conversation persistence
- [ ] Support for more TTS providers (ElevenLabs, Azure)
- [ ] Real-time streaming responses
- [ ] WebRTC for better audio in browser
- [ ] Multi-language support beyond EN/ZH
- [ ] User authentication and sessions
