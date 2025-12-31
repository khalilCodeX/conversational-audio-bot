import streamlit as st
import os
import io
import numpy as np
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from openai import OpenAI
from utils.audio_utils import AudioProcessor
from utils.llm_utils import LLMProcessor
import soundfile as sf

load_dotenv()

audio_processor = AudioProcessor()
llm_processor = LLMProcessor()

# Streamlit session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "recording_duration" not in st.session_state:
    st.session_state.recording_duration = 10
if "tts_lang" not in st.session_state:
    st.session_state.tts_lang = "en"
if "mode" not in st.session_state:
    st.session_state.mode = "customer_service"

# ---------------- Audio Visualization ----------------
def visualize_audio(audio_path):
    """Visualize audio waveform"""
    try:
        data, sr = sf.read(audio_path)
        if len(data.shape) > 1:
            data = np.mean(data, axis=1)
        times = np.arange(len(data)) / sr
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.plot(times, data)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.set_title("Audio Waveform")
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        st.image(buf)
    except Exception as e:
        st.warning(f"Unable to visualize audio: {str(e)}")

    # ---------------- Audio Handling ----------------
def handle_audio_input():
    """Handle recording and processing audio input"""
    with st.spinner(f"Recording {st.session_state.recording_duration} seconds..."):
        audio_file = audio_processor.record_audio(duration=st.session_state.recording_duration)
        if audio_file:
            st.audio(audio_file)
            visualize_audio(audio_file)
            processed_path = audio_processor.preprocess_audio(audio_file)
            transcript = audio_processor.transcribe_audio(processed_path)
            if transcript:
                st.info(f"Transcription: {transcript}")
                handle_llm_response(transcript)
            else:
                st.error("Audio transcription failed")
        else:
            st.error("Recording failed")

def handle_uploaded_audio(uploaded_file):
    """Handle uploaded audio file"""
    temp_path = os.path.join(audio_processor.temp_dir, "uploaded.wav")
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.audio(temp_path)
    visualize_audio(temp_path)
    processed_path = audio_processor.preprocess_audio(temp_path)
    transcript = audio_processor.transcribe_audio(processed_path)
    if transcript:
        st.info(f"Transcription: {transcript}")
        handle_llm_response(transcript)
    else:
        st.error("Audio transcription failed")


# ---------------- LLM Response ----------------
def handle_llm_response(user_text):
    """Generate AI response and TTS"""
    with st.spinner("Generating response..."):
        response = llm_processor.generate_response(
            user_text, 
            conversation_history=st.session_state.messages
        )
        st.session_state.messages.append({"role": "user", "content": user_text})
        st.session_state.messages.append({"role": "assistant", "content": response})

        st.success("AI response:")
        st.write(response)
        audio_response = audio_processor.text_to_speech(response, lang=st.session_state.tts_lang)
        if audio_response:
            st.audio(audio_response)


# ---------------- Text Input ----------------
def submit_text_input():
    """Callback to clear text input after submission"""
    st.session_state.user_text = ""       

# ---------------- Text Input ----------------
def handle_text_input():
    """Handle text input with Enter key submission"""
    
    def submit_text():
        """Callback to handle text submission"""
        user_input = st.session_state.user_text
        if user_input.strip():  # ignore empty input
            handle_llm_response(user_input)
            st.session_state.user_text = ""  # safe here because callback runs before widget redraw

    # Text input widget with on_change callback
    st.text_input(
        "Enter your question:",
        key="user_text",
        on_change=submit_text,
        placeholder="Type your message and press Enter"
    )

# ---------------- Conversation History ----------------
def display_conversation_history():
    st.subheader("Conversation History")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# ---------------- Settings ----------------
def settings_section():
    st.sidebar.header("Settings")
    # Recording duration
    st.session_state.recording_duration = st.sidebar.slider(
        "Recording Duration (seconds)", 5, 20, st.session_state.recording_duration
    )
    # TTS language
    st.session_state.tts_lang = st.sidebar.selectbox(
        "TTS Language", ["en", "zh"], index=0
    )
    # Mode selection
    mode = st.sidebar.radio("Select mode", ["Customer Service", "Lead Generation"])
    if mode == "Customer Service" and st.session_state.mode != "customer_service":
        st.session_state.mode = "customer_service"
        llm_processor.customize_for_call_center()
        st.sidebar.success("Switched to Customer Service mode")
    elif mode == "Lead Generation" and st.session_state.mode != "lead_generation":
        st.session_state.mode = "lead_generation"
        llm_processor.customize_for_lead_generation()
        st.sidebar.success("Switched to Lead Generation mode")
    # Clear conversation
    if st.sidebar.button("Clear Conversation History"):
        st.session_state.messages = []
        st.sidebar.success("Conversation history cleared")
        # No rerun needed; Streamlit automatically updates widgets

# ---------------- Main ----------------
def main():
    st.title("AI Voice Customer Service Assistant")
    st.write("This assistant can respond to voice or text input and generate audio replies.")

    settings_section()

    tab1, tab2, tab3 = st.tabs(["Voice Interaction", "Text Interaction", "Conversation Analysis"])

    # Voice tab
    with tab1:
        st.subheader("Voice Input")
        if st.button("Start Recording"):
            handle_audio_input()
        uploaded_file = st.file_uploader("Or upload audio file", type=["wav", "mp3"])
        if uploaded_file:
            handle_uploaded_audio(uploaded_file)

    # Text tab
    with tab2:
        st.subheader("Text Interaction")
        handle_text_input()

    # Analysis tab
    with tab3:
        st.subheader("Conversation Analysis")
        if st.session_state.messages:
            if st.button("Analyze Conversation"):
                with st.spinner("Analyzing conversation..."):
                    analysis = llm_processor.analyze_conversation(st.session_state.messages)
                    st.write(analysis["analysis"])
        else:
            st.info("Conversation history is empty")

    display_conversation_history()

if __name__ == "__main__":
    main()