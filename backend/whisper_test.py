from flask import Flask, jsonify
from flask_cors import CORS
import whisper
import sounddevice as sd
import numpy as np
import scipy.io.wavfile
import threading
import os
from googletrans import Translator
import tempfile
import atexit
from pathlib import Path

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",
            "http://localhost:5173",
            "https://your-frontend.vercel.app"
        ]
    }
})

fs = 44100
channels = 1

audio_buffer = []
recording = False
stream = None  # GLOBAL stream to keep audio stream alive

AUDIO_TEMP_DIR = Path(__file__).parent / "audio_temp"
AUDIO_TEMP_DIR.mkdir(exist_ok=True)

model = None

def get_model():
    global model
    if model is None:
        print("Loading Whisper model...")
        model = whisper.load_model("base")
    return model

def audio_callback(indata, frames, time, status):
    global audio_buffer, recording
    if recording:
        audio_buffer.append(indata.copy())

@app.route('/start', methods=['GET'])
def start_recording():
    global recording, audio_buffer, stream
    if recording:
        return jsonify({"error": "Already recording"}), 400

    audio_buffer = []
    recording = True

    try:
        if stream is None:
            stream = sd.InputStream(
                samplerate=fs,
                channels=channels,
                callback=audio_callback,
                blocksize=1024
            )
            stream.start()
        print("Recording started")
        return jsonify({"status": "recording started"})
    except Exception as e:
        recording = False
        return jsonify({"error": str(e)}), 500

@app.route('/stop', methods=['GET'])
def stop_recording():
    global recording, audio_buffer, stream
    if not recording:
        return jsonify({"error": "Not recording"}), 400

    recording = False

    try:
        if stream is not None:
            stream.stop()
            stream.close()
            stream = None

        if not audio_buffer:
            return jsonify({"error": "No audio recorded"}), 400

        audio_data = np.concatenate(audio_buffer, axis=0)

        # Save to temp wav file
        with tempfile.NamedTemporaryFile(
            dir=AUDIO_TEMP_DIR,
            suffix=".wav",
            delete=False
        ) as f:
            temp_path = f.name
            # Convert float audio to int16 PCM
            scipy.io.wavfile.write(temp_path, fs, (audio_data * 32767).astype(np.int16))

            # Transcribe & translate
            try:
                model = get_model()
                result = model.transcribe(temp_path, task="translate", language="zh")
                english_text = result["text"]

                translator = Translator()
                thai_translation = translator.translate(english_text, dest='th')

                return jsonify({
                    "english": english_text,
                    "thai": thai_translation.text
                })
            finally:
                # Clean temp file
                try:
                    os.unlink(temp_path)
                except:
                    pass

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@atexit.register
def cleanup():
    print("Cleaning up temp files...")
    for file in AUDIO_TEMP_DIR.glob("*.wav"):
        try:
            file.unlink()
        except:
            pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
