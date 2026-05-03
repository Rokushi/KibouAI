import json
import pyaudio
import os
import torch
import sounddevice as sd
import numpy as np
import silero_vad
import time
from vosk import Model, KaldiRecognizer

original_stderr = os.dup(2)
null_fd = os.open(os.devnull, os.O_WRONLY)
os.dup2(null_fd, 2)

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

SPEAKER = 'eugene'
LANGUAGE = 'ru'
MODEL_ID = 'v4_ru'
SAMPLE_RATE = 24000

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                          model='silero_tts',
                          language=LANGUAGE,
                          speaker=MODEL_ID)
model.to(device)

vad_model = silero_vad.load_silero_vad()

def voice_detecting(timeout=2.0, silence_duration=0.7, CHUNK=512):
    audio_buffer = []
    speaking = False
    silent_chunks = 0
    start_time = time.time()

    chunks_per_seconds = RATE / CHUNK
    silence_limit = int(silence_duration * chunks_per_seconds)

    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)

        audio_int16 = np.frombuffer(data, dtype=np.int16)
        audio_float32 = audio_int16.astype(np.float32) / 32768.0

        speach_prob = vad_model(torch.from_numpy(audio_float32), RATE).item()

        if speach_prob > 0.5:
            if not speaking:
                speaking = True
                start_time = time.time()
            silent_chunks = 0
            audio_buffer.append(data)

        elif speaking:
            silent_chunks += 1
            audio_buffer.append(data)

            if silent_chunks >= silence_limit:
                break

        else:
            if time.time() - start_time > timeout:
                break

    if not audio_buffer:
        return b''

    return b''.join(audio_buffer)

"""======[Обработка голоса пользователя]======"""
def voice_processing(chunk_multiplier=5, model=None, grammar=None, data=None):
    rec_model = model if model else ru_model

    rec = KaldiRecognizer(rec_model, RATE) if grammar is None else KaldiRecognizer(rec_model, RATE, grammar)
    rec.SetWords(True)
    if data == None:
        data = stream.read(CHUNK * chunk_multiplier, exception_on_overflow=False)
    rec.AcceptWaveform(data)
    text = json.loads(rec.PartialResult()).get('partial', '').strip().lower()

    return text

"""======[Обработка голоса пользователя для определения названия папки]======"""
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

def say(text: str):
    audio = model.apply_tts(text=text,
                            speaker=SPEAKER,
                            sample_rate=SAMPLE_RATE,
                            put_accent=True)
    sd.play(audio, SAMPLE_RATE)
    sd.wait()

os.dup2(original_stderr, 2)
os.close(null_fd)
os.close(original_stderr)