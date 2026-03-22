import os
import sys
import static_ffmpeg

# 1. Активируем FFmpeg через static_ffmpeg (должно добавить пути автоматически)
static_ffmpeg.add_paths()

# 2. Но на всякий случай добавим пути вручную, если add_paths() не сработал
#    Ищем папку, куда static_ffmpeg положил бинарники
static_ffmpeg_dir = os.path.dirname(static_ffmpeg.__file__)
possible_dirs = [
    os.path.join(static_ffmpeg_dir, "bin"),
    os.path.join(static_ffmpeg_dir, "ffmpeg", "bin"),
    os.path.join(sys.prefix, "Library", "bin"),  # если вдруг conda
    r"D:\Greenery\PycharmProjects\KibouAI\tts_service\venv_tts\lib\site-packages\static_ffmpeg\bin\win32",
]

for dll_dir in possible_dirs:
    if os.path.exists(dll_dir):
        os.add_dll_directory(dll_dir)
        print(f"Добавлен путь к DLL: {dll_dir}")
import torch
import torchaudio
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

from TTS.config.shared_configs import BaseDatasetConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
import torch.serialization
torch.serialization.add_safe_globals([BaseDatasetConfig, XttsConfig, XttsAudioConfig, XttsArgs])

CHECKPOINT_DIR = os.path.dirname(__file__)
CONFIG_PATH = r"D:\Greenery\PycharmProjects\KibouAI\tts_service\config.json"
VOCAB_PATH = r"D:\Greenery\PycharmProjects\KibouAI\tts_service\vocab.json"
SPEAKER_WAV = [rf"D:\Greenery\PycharmProjects\KibouAI\tts_service\wavs\Dio_{i}.wav" for i in range(180, 241)]

_model = None
_config = None

def load_model():
    global _model, _config
    if _model is not None:
        return

    print("[1/5] Загрузка конфига...")
    _config = XttsConfig()
    _config.load_json(CONFIG_PATH)

    print("[2/5] Инициализация модели...")
    _model = Xtts.init_from_config(_config)

    print("[3/5] Загрузка чекпоинта...")
    _model.load_checkpoint(
        _config,
        checkpoint_dir=CHECKPOINT_DIR,
        checkpoint_path=os.path.join(CHECKPOINT_DIR, "best_model.pth"),
        vocab_path=VOCAB_PATH,
        eval=True,
        strict=False,
        speaker_file_path=None
    )

    print("[4/5] Перемещение на GPU...")
    _model.cuda()
    print("Модель загружена")

def synthes_speech(text: str):
    if _model is None:
        load_model()

    print("[5/5] Синтез речи...")
    with torch.no_grad():
        outputs = _model.synthesize(
            text=text,
            config=_config,
            speaker_wav=SPEAKER_WAV,
            temperature=0.4, #креативность
            top_k=50,
            top_p=0.85,
            language="ru",
        )
    return torch.tensor(outputs["wav"])