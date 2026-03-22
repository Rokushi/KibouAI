import json
import pyaudio
import os
from vosk import Model, KaldiRecognizer

original_stderr = os.dup(2)
null_fd = os.open(os.devnull, os.O_WRONLY)
os.dup2(null_fd, 2)

stream = None
ru_model = None
en_model = None
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 16000

ru_model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "vosk-model-small-ru-0.22")
en_model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "vosk-model-en-us-0.42-gigaspeech")
ru_model = Model(ru_model_path)
en_model = Model(en_model_path)

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

"""======[Обработка голоса пользователя]======"""
def voice_processing(chunk_multiplier=5, model=None, grammar=None):
    rec_model = model if model else ru_model

    rec = KaldiRecognizer(rec_model, RATE) if grammar is None else KaldiRecognizer(rec_model, RATE, grammar)
    rec.SetWords(True)
    data = stream.read(CHUNK * chunk_multiplier, exception_on_overflow=False)
    rec.AcceptWaveform(data)
    text = json.loads(rec.PartialResult()).get('partial', '').strip().lower()

    return text

def voice_processing_x(chunk_multiplier=5, grammar=None):
    en_rec = KaldiRecognizer(en_model, RATE) if grammar is None else KaldiRecognizer(en_model, RATE, grammar)
    ru_rec = KaldiRecognizer(ru_model, RATE)
    en_rec.SetWords(True)
    ru_rec.SetWords(True)

    data = stream.read(CHUNK * chunk_multiplier, exception_on_overflow=False)

    en_rec.AcceptWaveform(data)
    ru_rec.AcceptWaveform(data)

    en_text = json.loads(en_rec.PartialResult()).get('partial', '').strip().lower()
    ru_text = json.loads(ru_rec.PartialResult()).get('partial', '').strip().lower()

    return en_text, ru_text

os.dup2(original_stderr, 2)
os.close(null_fd)
os.close(original_stderr)