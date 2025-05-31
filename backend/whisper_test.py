from flask import Flask, request, jsonify
from flask_cors import CORS
import whisper
from googletrans import Translator
import tempfile
import os
from pathlib import Path
import atexit

app = Flask(__name__)
CORS(app, resources={
    r"/transcribe": {
        "origins": ["https://language-azw3.onrender.com"],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "max_age": 600
    }
})

AUDIO_TEMP_DIR = Path(__file__).parent / "audio_temp"
AUDIO_TEMP_DIR.mkdir(exist_ok=True)

model = None

def get_model():
    global model
    if model is None:
        print("Loading Whisper model...")
        model = whisper.load_model("base")
    return model

@app.route('/transcribe', methods=['POST', 'OPTIONS'])
def transcribe_audio():
    if request.method == 'OPTIONS':
        # Handle preflight requests
        response = jsonify({"status": "preflight"})
        # flask-cors already adds headers, but just in case:
        response.headers.add('Access-Control-Allow-Origin', 'https://language-azw3.onrender.com')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Max-Age', '600')
        return response

    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    file = request.files['audio']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=AUDIO_TEMP_DIR, suffix=".wav", delete=False) as f:
            file.save(f)
            temp_path = f.name
            print(f"Saved audio to {temp_path}")

        if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
            return jsonify({"error": "Empty audio file"}), 400

        model = get_model()
        
        result = model.transcribe(
            temp_path,
            task="translate",
            language="zh",
            fp16=False
        )

        if not result.get("text"):
            return jsonify({"error": "No transcription result"}), 500

        translator = Translator()
        thai_translation = translator.translate(result["text"], dest='th')
        
        return jsonify({
            "english": result["text"],
            "thai": thai_translation.text,
            "status": "success"
        })

    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return jsonify({
            "error": str(e),
            "type": type(e).__name__,
            "details": "Check server logs for more information"
        }), 500

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception as e:
                print(f"Error cleaning up file: {str(e)}")

@atexit.register
def cleanup():
    print("Cleaning up temp files...")
    for file in AUDIO_TEMP_DIR.glob("*.wav"):
        try:
            file.unlink()
        except:
            pass
