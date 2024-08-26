import os
import sys
from openai import OpenAI
from pydub import AudioSegment
from pydub.utils import make_chunks
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLineEdit, QCheckBox, QLabel, QMessageBox, QProgressBar
from PyQt6.QtCore import Qt

# Initialize the OpenAI client
groq = OpenAI(api_key="KEY",
              base_url="https://api.groq.com/openai/v1")

# Function to load audio file based on its extension
def load_audio(file_path):
    if file_path.endswith('.mp3'):
        return AudioSegment.from_mp3(file_path)
    elif file_path.endswith('.wav'):
        return AudioSegment.from_wav(file_path)
    else:
        raise ValueError("Unsupported file format. Please use MP3 or WAV.")

# Function to transcribe audio
def transcribe_audio(audio_file_path, api_key, update_progress):
    groq.api_key = api_key
    audio = load_audio(audio_file_path)
    chunk_length_ms = 136533
    chunks = make_chunks(audio, chunk_length_ms)

    total_chunks = len(chunks)
    transcript_parts = []
    for i, chunk in enumerate(chunks):
        chunk_name = f"chunk{i}.mp3"
        chunk.export(chunk_name, format="mp3")
        
        with open(chunk_name, "rb") as chunk_file:
            transcript = groq.audio.transcriptions.create(
                model="whisper-large-v3",
                file=chunk_file,
                response_format="text"
            )
        
        transcript_parts.append(transcript)
        update_progress(i + 1, total_chunks, f"Transcribing chunk {i+1} of {total_chunks}")
        
        os.remove(chunk_name)

    update_progress(total_chunks, total_chunks, "Transcription complete")
    return "\n".join(transcript_parts)

class TranscriptionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_api_key()

    def initUI(self):
        self.setWindowTitle('Audio Transcription App')
        self.layout = QVBoxLayout()

        self.api_key_label = QLabel('API Key:')
        self.api_key_input = QLineEdit()
        self.remember_api_key_checkbox = QCheckBox('Remember API Key')
        self.audio_file_label = QLabel('Select Audio File:')
        self.audio_file_button = QPushButton('Browse')
        self.audio_file_button.clicked.connect(self.select_audio_file)
        self.transcribe_button = QPushButton('Transcribe')
        self.transcribe_button.clicked.connect(self.start_transcription)

        # Set a minimum width for the progress bar to match the buttons
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        #self.progress_bar.setMinimumWidth(self.audio_file_button.sizeHint().width())

        self.status_label = QLabel('Ready')
        self.open_when_done_checkbox = QCheckBox('Open transcribed text file when done')

        self.layout.addWidget(self.api_key_label)
        self.layout.addWidget(self.api_key_input)
        self.layout.addWidget(self.remember_api_key_checkbox)
        self.layout.addWidget(self.audio_file_label)
        self.layout.addWidget(self.audio_file_button)
        self.layout.addWidget(self.transcribe_button)
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.open_when_done_checkbox)

        self.setLayout(self.layout)

    def select_audio_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.mp3 *.wav)")
        if file_path:
            self.audio_file_path = file_path
            self.audio_file_label.setText(f'Selected Audio File: {file_path}')

    def start_transcription(self):
        api_key = self.api_key_input.text()
        if not api_key:
            QMessageBox.warning(self, 'Error', 'Please enter an API key.')
            return

        if not hasattr(self, 'audio_file_path'):
            QMessageBox.warning(self, 'Error', 'Please select an audio file.')
            return

        try:
            self.progress_bar.setValue(0)
            self.status_label.setText('Splitting into chunks...')
            transcript = transcribe_audio(self.audio_file_path, api_key, self.update_progress)
            self.save_transcript(transcript)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Transcription failed: {str(e)}')

        if self.remember_api_key_checkbox.isChecked():
            self.save_api_key(api_key)

    def update_progress(self, current_chunk, total_chunks, status_text):
        progress = int((current_chunk / total_chunks) * 100)
        self.progress_bar.setValue(progress)
        self.status_label.setText(status_text)

    def save_transcript(self, transcript):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Transcript", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, "w") as output_file:
                output_file.write(transcript)
            QMessageBox.information(self, 'Success', 'Transcription complete. Transcript saved.')
            if self.open_when_done_checkbox.isChecked():
                os.startfile(file_path)

    def save_api_key(self, api_key):
        with open('api_key.txt', 'w') as f:
            f.write(api_key)

    def load_api_key(self):
        if os.path.exists('api_key.txt'):
            with open('api_key.txt', 'r') as f:
                api_key = f.read().strip()
                self.api_key_input.setText(api_key)
                self.remember_api_key_checkbox.setChecked(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TranscriptionApp()
    ex.show()
    sys.exit(app.exec())
