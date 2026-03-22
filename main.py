from tts_service import main
import json
from llama_brain import brain
import pyaudio
import os
import commands
import time
from vosk import Model, KaldiRecognizer
from build_vosk_vocab import build_english_folder_list
from voice_utils import voice_processing, voice_processing_x, ru_model, en_model, stream, p

# original_stderr = os.dup(2)
# null_fd = os.open(os.devnull, os.O_WRONLY)
# os.dup2(null_fd, 2)

# Загружаем список английских названий папок
try:
    with open('english_folder_names.json', 'r', encoding='utf-8') as f:
        english_keywords = json.load(f) + ["[unk]"]
except FileNotFoundError:
    # Если файла нет — создаём
    english_keywords = build_english_folder_list()

if __name__ == '__main__':

    try:
        brain = brain(
            model_name="qwen3:14b",
            prompts_dir="prompts",
            temperature=0.1
        )
    except Exception as e:
        print(f"[BRAIN INITIALIZATION ERROR]: {e}")

    try:
        speak = main.DioTTS()
    except Exception as e:
        print(f"[TTS INITIALIZATION ERROR]: {e}")

    def listen_for_trigger(trigger = "кибо"):
        try:
            while True:
                partial_text = voice_processing(chunk_multiplier=2, model=ru_model)
                if partial_text:
                    words = partial_text.lower().split()
                    print(words)
                    if words and (trigger in words[-1] or words[-1].startswith(trigger)):
                        return True
        except KeyboardInterrupt:
            print("\nОстановка")
        except Exception as e:
            print(f"[ОШИБКА]: {e}")

    def listen():
        text = ""
        try:
            while text == "":
                text = voice_processing(chunk_multiplier=7)

            print(f"Текст: {text}")
            user_query(text)
        except KeyboardInterrupt:
            print("\nОстановка")
        except Exception as e:
            print(f"[ОШИБКА]: {e}")


    def get_folder_name():
        speak.say("Какую папку открыть?")

        while True:
            en_text, ru_text = voice_processing_x(grammar=json.dumps(english_keywords))
            if en_text == "" and ru_text == "":
                return None
            elif en_text in english_keywords:
                print(f"ENG: {en_text}")
                return en_text
            elif ru_text:
                print(f"RU: {ru_text}")
                return ru_text

    """======[Уточнение времени для таймера]======"""
    def get_timer_duration():
        speak.say("Сколько времени тебе нужно?")
        text = voice_processing()
        return commands.parse_time(text) if text else None

    """======[Определение действия]======"""
    def user_query(text):
        response = brain.ask_json(text)

        if response and "action" in response:
            action = response["action"]
            params = response.get("params", {})

            if action == "open_browser":
                commands.open_browser()

            elif action == "open_folder":
                name = params.get("name", "")
                if name:
                    commands.open_folder(name)
                else:
                    folder_name = get_folder_name()
                    if folder_name:
                        commands.open_folder(folder_name)
                    else:
                        speak.say("Не понял, какая папка")

            elif action == "timer":
                time = params.get("seconds", "")
                if time:
                   commands.timer(time)
                else:
                    time = get_timer_duration()
                    commands.timer(time) if time else speak.say("Не понял, сколько нужно времени")

            elif action == "show_time":
                commands.show_time()

            elif action == "exit":
                speak.say("Прощай!")
                exit()

        else:
            speak.say(response)
            brain.add_to_history(text, response)

    """======[Основной код]======"""
    while True:
        print("Ожидание...")

        try:
            # Ждём слово-триггер
            if listen_for_trigger():
                speak.say("Что такое?")
                print("Что такое?")
                # Основной диалог
                listen()

        except KeyboardInterrupt:
            print("\nОстановка")
            break
        except Exception as e:
            print(f"Ошибка {e}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Выход")

    stream.stop_stream()
    stream.close()
    p.terminate()
    #os.system("for /f \"tokens=5\" %a in ('netstat -ano ^| findstr :8000') do taskkill /F /PID %a 2>nul")

# os.dup2(original_stderr, 2)
# os.close(null_fd)
# os.close(original_stderr)
