import tkinter as tk
from tkinter import ttk, scrolledtext
import speech_recognition as sr
import pyttsx3
import threading
import requests
import json
from pathlib import Path
import os

class VoiceAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Assistant")
        self.root.geometry("650x750")
        
        # Initialize speech components
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 180)
        
        # Load config
        self.config_file = Path.home() / '.voice_assistant_config.json'
        self.load_config()
        
        # UI Setup
        self.setup_ui()
        
        self.is_listening = False
        self.is_speaking = False
        self.continuous_mode = False
        self.stop_continuous = False
        
    def load_config(self):
        """Load API configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.api_url = config.get('api_url', 'http://127.0.0.1:1234/v1/chat/completions')
                self.api_key = config.get('api_key', 'not-needed')
                self.model = config.get('model', 'local-model')
                self.pause_threshold = config.get('pause_threshold', 0.8)
                self.phrase_threshold = config.get('phrase_threshold', 0.3)
                self.non_speaking_duration = config.get('non_speaking_duration', 0.5)
                self.use_custom_stt = config.get('use_custom_stt', False)
                self.stt_api_url = config.get('stt_api_url', 'http://127.0.0.1:8000/v1/audio/transcriptions')
                self.stt_api_key = config.get('stt_api_key', 'not-needed')
                self.use_custom_tts = config.get('use_custom_tts', False)
                self.tts_api_url = config.get('tts_api_url', 'http://127.0.0.1:8000/v1/audio/speech')
                self.tts_api_key = config.get('tts_api_key', 'not-needed')
                self.tts_voice = config.get('tts_voice', 'alloy')
        else:
            self.api_url = 'http://127.0.0.1:1234/v1/chat/completions'
            self.api_key = 'not-needed'
            self.model = 'local-model'
            self.pause_threshold = 0.8
            self.phrase_threshold = 0.3
            self.non_speaking_duration = 0.5
            self.use_custom_stt = False
            self.stt_api_url = 'http://127.0.0.1:8000/v1/audio/transcriptions'
            self.stt_api_key = 'not-needed'
            self.use_custom_tts = False
            self.tts_api_url = 'http://127.0.0.1:8000/v1/audio/speech'
            self.tts_api_key = 'not-needed'
            self.tts_voice = 'alloy'
    
    def save_config(self):
        """Save API configuration to file"""
        config = {
            'api_url': self.api_url_entry.get(),
            'api_key': self.api_key_entry.get(),
            'model': self.model_entry.get(),
            'pause_threshold': self.pause_scale.get(),
            'phrase_threshold': self.phrase_scale.get(),
            'non_speaking_duration': self.non_speaking_scale.get(),
            'use_custom_stt': self.use_custom_stt_var.get(),
            'stt_api_url': self.stt_api_url_entry.get(),
            'stt_api_key': self.stt_api_key_entry.get(),
            'use_custom_tts': self.use_custom_tts_var.get(),
            'tts_api_url': self.tts_api_url_entry.get(),
            'tts_api_key': self.tts_api_key_entry.get(),
            'tts_voice': self.tts_voice_entry.get()
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f)
        self.api_url = config['api_url']
        self.api_key = config['api_key']
        self.model = config['model']
        self.pause_threshold = config['pause_threshold']
        self.phrase_threshold = config['phrase_threshold']
        self.non_speaking_duration = config['non_speaking_duration']
        self.use_custom_stt = config['use_custom_stt']
        self.stt_api_url = config['stt_api_url']
        self.stt_api_key = config['stt_api_key']
        self.use_custom_tts = config['use_custom_tts']
        self.tts_api_url = config['tts_api_url']
        self.tts_api_key = config['tts_api_key']
        self.tts_voice = config['tts_voice']
        
        # Update recognizer settings
        self.recognizer.pause_threshold = self.pause_threshold
        self.recognizer.phrase_threshold = self.phrase_threshold
        self.recognizer.non_speaking_duration = self.non_speaking_duration
        
        self.status_label.config(text="Configuration saved!", foreground="green")
        self.root.after(2000, lambda: self.status_label.config(text="Ready", foreground="black"))
    
    def setup_ui(self):
        """Create the user interface"""
        # Make window larger to accommodate new settings
        self.root.geometry("650x750")
        # Config Frame
        config_frame = ttk.LabelFrame(self.root, text="API Configuration", padding=10)
        config_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(config_frame, text="API URL:").grid(row=0, column=0, sticky="w", pady=2)
        self.api_url_entry = ttk.Entry(config_frame, width=50)
        self.api_url_entry.insert(0, self.api_url)
        self.api_url_entry.grid(row=0, column=1, pady=2, padx=5)
        
        ttk.Label(config_frame, text="API Key:").grid(row=1, column=0, sticky="w", pady=2)
        self.api_key_entry = ttk.Entry(config_frame, width=50, show="*")
        self.api_key_entry.insert(0, self.api_key)
        self.api_key_entry.grid(row=1, column=1, pady=2, padx=5)
        
        ttk.Label(config_frame, text="Model:").grid(row=2, column=0, sticky="w", pady=2)
        self.model_entry = ttk.Entry(config_frame, width=50)
        self.model_entry.insert(0, self.model)
        self.model_entry.grid(row=2, column=1, pady=2, padx=5)
        
        # Speech-to-Text API Settings
        stt_frame = ttk.LabelFrame(self.root, text="Speech-to-Text Settings", padding=10)
        stt_frame.pack(fill="x", padx=10, pady=5)
        
        self.use_custom_stt_var = tk.BooleanVar(value=self.use_custom_stt)
        ttk.Checkbutton(stt_frame, text="Use Custom Speech API (instead of Google)", 
                       variable=self.use_custom_stt_var).grid(row=0, column=0, columnspan=2, sticky="w", pady=5)
        
        ttk.Label(stt_frame, text="Speech API URL:").grid(row=1, column=0, sticky="w", pady=2)
        self.stt_api_url_entry = ttk.Entry(stt_frame, width=50)
        self.stt_api_url_entry.insert(0, self.stt_api_url)
        self.stt_api_url_entry.grid(row=1, column=1, pady=2, padx=5)
        
        ttk.Label(stt_frame, text="Speech API Key:").grid(row=2, column=0, sticky="w", pady=2)
        self.stt_api_key_entry = ttk.Entry(stt_frame, width=50, show="*")
        self.stt_api_key_entry.insert(0, self.stt_api_key)
        self.stt_api_key_entry.grid(row=2, column=1, pady=2, padx=5)
        
        # Text-to-Speech API Settings
        tts_frame = ttk.LabelFrame(self.root, text="Text-to-Speech Settings", padding=10)
        tts_frame.pack(fill="x", padx=10, pady=5)
        
        self.use_custom_tts_var = tk.BooleanVar(value=self.use_custom_tts)
        ttk.Checkbutton(tts_frame, text="Use Custom TTS API (instead of pyttsx3)", 
                       variable=self.use_custom_tts_var).grid(row=0, column=0, columnspan=2, sticky="w", pady=5)
        
        ttk.Label(tts_frame, text="TTS API URL:").grid(row=1, column=0, sticky="w", pady=2)
        self.tts_api_url_entry = ttk.Entry(tts_frame, width=50)
        self.tts_api_url_entry.insert(0, self.tts_api_url)
        self.tts_api_url_entry.grid(row=1, column=1, pady=2, padx=5)
        
        ttk.Label(tts_frame, text="TTS API Key:").grid(row=2, column=0, sticky="w", pady=2)
        self.tts_api_key_entry = ttk.Entry(tts_frame, width=50, show="*")
        self.tts_api_key_entry.insert(0, self.tts_api_key)
        self.tts_api_key_entry.grid(row=2, column=1, pady=2, padx=5)
        
        ttk.Label(tts_frame, text="Voice:").grid(row=3, column=0, sticky="w", pady=2)
        self.tts_voice_entry = ttk.Entry(tts_frame, width=50)
        self.tts_voice_entry.insert(0, self.tts_voice)
        self.tts_voice_entry.grid(row=3, column=1, pady=2, padx=5)
        
        # Speech Detection Settings
        speech_frame = ttk.LabelFrame(self.root, text="Speech Detection Settings", padding=10)
        speech_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(speech_frame, text="Pause Threshold (silence after speech):").grid(row=0, column=0, sticky="w", pady=2)
        self.pause_scale = tk.Scale(speech_frame, from_=0.3, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, length=200)
        self.pause_scale.set(self.pause_threshold)
        self.pause_scale.grid(row=0, column=1, pady=2, padx=5)
        ttk.Label(speech_frame, text="seconds").grid(row=0, column=2, sticky="w")
        
        ttk.Label(speech_frame, text="Phrase Threshold (min speech length):").grid(row=1, column=0, sticky="w", pady=2)
        self.phrase_scale = tk.Scale(speech_frame, from_=0.1, to=1.0, resolution=0.1, orient=tk.HORIZONTAL, length=200)
        self.phrase_scale.set(self.phrase_threshold)
        self.phrase_scale.grid(row=1, column=1, pady=2, padx=5)
        ttk.Label(speech_frame, text="seconds").grid(row=1, column=2, sticky="w")
        
        ttk.Label(speech_frame, text="Non-speaking Duration (before speech):").grid(row=2, column=0, sticky="w", pady=2)
        self.non_speaking_scale = tk.Scale(speech_frame, from_=0.1, to=1.0, resolution=0.1, orient=tk.HORIZONTAL, length=200)
        self.non_speaking_scale.set(self.non_speaking_duration)
        self.non_speaking_scale.grid(row=2, column=1, pady=2, padx=5)
        ttk.Label(speech_frame, text="seconds").grid(row=2, column=2, sticky="w")
        
        ttk.Button(speech_frame, text="Save Config", command=self.save_config).grid(row=3, column=1, pady=5)
        
        # Control Frame
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill="x", padx=10)
        
        self.listen_button = ttk.Button(control_frame, text="🎤 Listen Once", command=self.listen_once)
        self.listen_button.pack(side="left", padx=5)
        
        self.continuous_button = ttk.Button(control_frame, text="🔄 Continuous Mode", command=self.toggle_continuous)
        self.continuous_button.pack(side="left", padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="⏹ Stop Speaking", command=self.stop_speaking, state="disabled")
        self.stop_button.pack(side="left", padx=5)
        
        # Status
        self.status_label = ttk.Label(control_frame, text="Ready", foreground="black")
        self.status_label.pack(side="left", padx=20)
        
        # Conversation Display
        conv_frame = ttk.LabelFrame(self.root, text="Conversation", padding=10)
        conv_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.conversation_text = scrolledtext.ScrolledText(conv_frame, wrap=tk.WORD, height=15)
        self.conversation_text.pack(fill="both", expand=True)
        self.conversation_text.tag_config("user", foreground="blue")
        self.conversation_text.tag_config("assistant", foreground="green")
        
    def listen_once(self):
        """Listen for a single voice input"""
        if not self.is_listening:
            self.is_listening = True
            self.listen_button.config(state="disabled")
            threading.Thread(target=self.listen_and_process, daemon=True).start()
    
    def toggle_continuous(self):
        """Toggle continuous listening mode"""
        if not self.continuous_mode:
            self.continuous_mode = True
            self.stop_continuous = False
            self.continuous_button.config(text="⏹ Stop Continuous")
            self.listen_button.config(state="disabled")
            threading.Thread(target=self.continuous_listen, daemon=True).start()
        else:
            self.stop_continuous = True
            self.continuous_mode = False
            self.continuous_button.config(text="🔄 Continuous Mode")
            self.listen_button.config(state="normal")
            self.status_label.config(text="Ready", foreground="black")
    
    def continuous_listen(self):
        """Continuously listen and respond"""
        while self.continuous_mode and not self.stop_continuous:
            if not self.is_speaking:
                self.listen_and_process()
            else:
                # Wait a bit if still speaking
                threading.Event().wait(0.5)
        
        # Reset buttons when stopped
        self.root.after(0, lambda: self.listen_button.config(state="normal"))
        
    def listen_and_process(self):
        """Listen to microphone and process the input"""
        try:
            # Update recognizer settings
            self.recognizer.pause_threshold = self.pause_scale.get()
            self.recognizer.phrase_threshold = self.phrase_scale.get()
            self.recognizer.non_speaking_duration = self.non_speaking_scale.get()
            
            with sr.Microphone() as source:
                self.status_label.config(text="Listening...", foreground="blue")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=30)
                
            self.status_label.config(text="Processing...", foreground="orange")
            
            # Transcribe audio
            if self.use_custom_stt_var.get():
                text = self.transcribe_with_custom_api(audio)
            else:
                text = self.recognizer.recognize_google(audio)
            
            if not text:
                return
            
            self.conversation_text.insert(tk.END, f"You: {text}\n\n", "user")
            self.conversation_text.see(tk.END)
            
            # Get AI response
            response = self.get_ai_response(text)
            
            if response:
                self.conversation_text.insert(tk.END, f"Assistant: {response}\n\n", "assistant")
                self.conversation_text.see(tk.END)
                
                # Speak the response
                self.speak(response)
            
        except sr.WaitTimeoutError:
            self.status_label.config(text="No speech detected", foreground="red")
            self.root.after(2000, lambda: self.status_label.config(text="Ready" if not self.continuous_mode else "Listening...", foreground="black" if not self.continuous_mode else "blue"))
        except sr.UnknownValueError:
            self.status_label.config(text="Could not understand audio", foreground="red")
            self.root.after(2000, lambda: self.status_label.config(text="Ready" if not self.continuous_mode else "Listening...", foreground="black" if not self.continuous_mode else "blue"))
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}", foreground="red")
            print(f"Error: {e}")
        finally:
            self.is_listening = False
            if not self.continuous_mode:
                self.listen_button.config(state="normal")
                if not self.is_speaking:
                    self.status_label.config(text="Ready", foreground="black")
    
    def transcribe_with_custom_api(self, audio):
        """Transcribe audio using custom Speech API (OpenAI Whisper-compatible)"""
        try:
            # Convert audio to WAV format
            wav_data = audio.get_wav_data()
            
            # Prepare the request
            headers = {
                'Authorization': f'Bearer {self.stt_api_key}'
            }
            
            files = {
                'file': ('audio.wav', wav_data, 'audio/wav')
            }
            
            data = {
                'model': 'whisper-1'  # Standard model name for Whisper-compatible APIs
            }
            
            response = requests.post(self.stt_api_url, headers=headers, files=files, data=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Extract transcription
            if 'text' in result:
                return result['text']
            elif 'transcription' in result:
                return result['transcription']
            else:
                print(f"Unexpected STT response format: {result}")
                self.conversation_text.insert(tk.END, f"STT API returned unexpected format\n\n", "assistant")
                return None
                
        except Exception as e:
            print(f"Custom STT Error: {e}")
            self.conversation_text.insert(tk.END, f"Speech API Error: {str(e)}\n\n", "assistant")
            return None
    
    def get_ai_response(self, text):
        """Send text to OpenAI-compatible API and get response"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            data = {
                'model': self.model,
                'messages': [
                    {'role': 'user', 'content': text}
                ]
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Debug: Print the full response
            print("API Response:", json.dumps(result, indent=2))
            
            # Try to extract the response
            if 'choices' in result:
                return result['choices'][0]['message']['content']
            elif 'error' in result:
                self.conversation_text.insert(tk.END, f"API Error: {result['error']}\n\n", "assistant")
                return None
            else:
                self.conversation_text.insert(tk.END, f"Unexpected API response format. Check console for details.\n\n", "assistant")
                return None
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP Error: {e.response.status_code}"
            try:
                error_detail = e.response.json()
                error_msg += f"\n{json.dumps(error_detail, indent=2)}"
            except:
                error_msg += f"\n{e.response.text}"
            self.conversation_text.insert(tk.END, f"{error_msg}\n\n", "assistant")
            print(error_msg)
            return None
        except Exception as e:
            self.conversation_text.insert(tk.END, f"API Error: {str(e)}\n\n", "assistant")
            print(f"Full error: {e}")
            return None
    
    def speak(self, text):
        """Convert text to speech"""
        self.is_speaking = True
        self.stop_button.config(state="normal")
        self.status_label.config(text="Speaking...", foreground="green")
        
        def speak_thread():
            try:
                if self.use_custom_tts_var.get():
                    # Use custom TTS API
                    self.speak_with_custom_api(text)
                else:
                    # Use pyttsx3
                    tts = pyttsx3.init()
                    tts.setProperty('rate', 180)
                    tts.say(text)
                    tts.runAndWait()
                    tts.stop()
            except Exception as e:
                print(f"TTS Error: {e}")
            finally:
                self.is_speaking = False
                self.root.after(0, lambda: self.stop_button.config(state="disabled"))
                if not self.continuous_mode:
                    self.root.after(0, lambda: self.status_label.config(text="Ready", foreground="black"))
                else:
                    self.root.after(0, lambda: self.status_label.config(text="Listening...", foreground="blue"))
        
        threading.Thread(target=speak_thread, daemon=True).start()
    
    def speak_with_custom_api(self, text):
        """Generate speech using custom TTS API (OpenAI TTS-compatible)"""
        try:
            headers = {
                'Authorization': f'Bearer {self.tts_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'tts-1',
                'input': text,
                'voice': self.tts_voice
            }
            
            response = requests.post(self.tts_api_url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            # Save and play audio
            import tempfile
            import wave
            import pyaudio
            
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                f.write(response.content)
                audio_file = f.name
            
            # Play audio using pydub and pyaudio for better format support
            try:
                from pydub import AudioSegment
                from pydub.playback import play
                
                audio = AudioSegment.from_file(audio_file)
                play(audio)
            except ImportError:
                # Fallback: if pydub not available, try direct playback (assumes WAV)
                import os
                if os.name == 'nt':  # Windows
                    import winsound
                    winsound.PlaySound(audio_file, winsound.SND_FILENAME)
                else:
                    # Try using system command
                    os.system(f'ffplay -nodisp -autoexit "{audio_file}" 2>/dev/null')
            
            # Clean up
            import os
            try:
                os.unlink(audio_file)
            except:
                pass
                
        except Exception as e:
            print(f"Custom TTS Error: {e}")
            self.conversation_text.insert(tk.END, f"TTS API Error: {str(e)}\n\n", "assistant")
    
    def stop_speaking(self):
        """Stop current speech output"""
        try:
            self.tts_engine.stop()
            self.is_speaking = False
            self.stop_button.config(state="disabled")
            if not self.continuous_mode:
                self.status_label.config(text="Ready", foreground="black")
            else:
                self.status_label.config(text="Listening...", foreground="blue")
        except:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceAssistant(root)
    root.mainloop()
