import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile
import openai
from gtts import gTTS
import os
import librosa
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class AudioProcessor:
    def __init__(self, sample_rate: int = 16000):
        """
        Initialize Audio Processor
        
        Args:
            sample_rate: Sample rate for audio processing
        """
        self.sample_rate = sample_rate
        self.temp_dir = tempfile.mkdtemp()
        print(f"AudioProcessor initialized with sample rate {self.sample_rate} Hz")
        print(f"Temporary files will be stored in: {self.temp_dir}")

    def record_audio(self, duration: int = 10) -> Optional[str]:
        """
        Record audio from the microphone
        
        Args:
            duration: Duration to record in seconds
        """
        try:
            print(f"Recording audio for {duration} seconds...")
            reording  = sd.rec(int(duration * self.sample_rate), 
                               samplerate=self.sample_rate, 
                               channels=1,
                               dtype='float32')
            
            sd.wait()  # Wait until recording is finished

            # Ensure 1D mono array
            if reording.ndim > 1:
                reording = reording[:,0]
            
            # Clip and normalize to avoid distortion
            recording = np.clip(reording, -1.0, 1.0)
            max_amplitude = np.max(np.abs(recording))
            if max_amplitude > 0:
                recording = recording / max_amplitude
            else:
                print("Warning: Recorded audio is silent.")

            # Save audio to a temporary file
            temp_path = os.path.abspath(os.path.join(self.temp_dir, "recording.wav"))
            sf.write(temp_path, recording, self.sample_rate)
            print(f"Audio recorded and saved to {temp_path} with samples: {recording.shape[0]}")
            return temp_path

        except Exception as e:
            print(f"Recording error: {str(e)}")
            return None
        
    def preprocess_audio(self, audio_path: str) -> Optional[str]:
        """
        Preprocess audio: resample to target sample rate and convert to mono.
        
        Args:
            audio_path: Input WAV file
            
        Returns:
            Path to processed audio file or None if error
        """
        try:
            data, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)

            max_amp = np.max(np.abs(data))
            if max_amp > 0:
                data = data / max_amp

            processed_path = os.path.abspath(os.path.join(self.temp_dir, "processed_audio.wav"))
            sf.write(processed_path, data, self.sample_rate)
            print(f"Audio preprocessed and saved to {processed_path} "
                  f"with samples: {data.shape[0]}, sample rate: {self.sample_rate}")
            
            return processed_path

        except Exception as e:
            print(f"Preprocessing error: {str(e)}")
            return None
        
    def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """
        Transcribe audio using OpenAI Whisper API.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Transcribed text or None if error
        """
        try:
            if not os.path.exists(audio_path):
                print(f"Audio file {audio_path} does not exist.")
                return None
            
            with open(audio_path, "rb") as audio_file:
                client = openai.OpenAI()
                transcript = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-1",
                    language="en"
                )
            print(f"Transcription completed: {transcript.text}")
            return transcript.text

        except Exception as e:
            print(f"Transcription error: {str(e)}")
            return None

    def text_to_speech(self, text: str, lang: str = 'en') -> Optional[str]:
        """
        Convert text to speech using gTTS.
        
        Args:
            text: Input text to convert
            lang: Language for TTS
            
        Returns:
            Path to the generated audio file or None if error
        """
        try:
           tts = gTTS(text=text, lang=lang)
           tts_path = os.path.abspath(os.path.join(self.temp_dir, "response.mp3"))
           tts.save(tts_path)
           print(f"TTS audio saved to {tts_path}")
           return tts_path

        except Exception as e:
            print(f"TTS error: {str(e)}")
            return None

    def cleanup(self) -> None:
        """
        Cleanup temporary files
        """
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
            print(f"Temporary files in {self.temp_dir} have been cleaned up.")

        except Exception as e:
            print(f"Cleanup error: {str(e)}")