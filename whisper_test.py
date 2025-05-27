import whisper
import sounddevice as sd
import numpy as np
import scipy.io.wavfile
import os
from googletrans import Translator

fs = 44100  # Sample rate
duration = 5  # seconds

print("Recording...")
audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
sd.wait()
print("Done recording")


def save_wav(filename, audio):
    scipy.io.wavfile.write(filename, fs, (audio * 32767).astype(np.int16))

filename = os.path.join(os.getcwd(), "input.wav")
save_wav(filename, audio)

model = whisper.load_model("base")
result = model.transcribe(filename, task="translate", language="Chinese")
english_text = result["text"]
print(" Transcribed (English):", english_text)
translator = Translator()
thai_translation = translator.translate(english_text, dest='th')
print(" Thai Translation:", thai_translation.text)


