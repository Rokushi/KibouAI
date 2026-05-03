import json
import commands
import time
from build_vosk_vocab import build_english_folder_list
from voice_utils import voice_processing, voice_processing_x, voice_detecting, say

# Загружаем список английских названий папок
try:
    with open('english_folder_names.json', 'r', encoding='utf-8') as f:
        english_keywords = json.load(f) + ["[unk]"]
except FileNotFoundError:
    english_keywords = build_english_folder_list()

def listen_for_trigger(trigger = "кибо"):
    try:
        while True:
            audio_data = voice_detecting()
            text = voice_processing(data=audio_data)
            print(f"Текст: '{text}'")
            if trigger in text.lower().split():
                return True

        # while True:
        #     partial_text = voice_processing(chunk_multiplier=2, model=ru_model)
        #     if partial_text:
        #         words = partial_text.lower().split()
        #         print(words)
        #         if words and (trigger in words[-1] or words[-1].startswith(trigger)):
        #             return True
    except KeyboardInterrupt:
        print("\nОстановка")
    except Exception as e:
        print(f"[ОШИБКА]: {e}")

def listen():
    try:
        while True:
            audio_data = voice_detecting()

            if not audio_data:
                continue

            text = voice_processing(data=audio_data)
            if text:
                print(f"Текст: '{text}'")
                return user_query(text)

    # text = ""
    # try:
    #     while text == "":
    #         text = voice_processing(chunk_multiplier=7)
    #
    #     print(f"Текст: {text}")
    #     user_query(text)
    except KeyboardInterrupt:
        print("\nОстановка")
    except Exception as e:
        print(f"[ОШИБКА]: {e}")

"""======[Уточнение названия папки ]======"""
def get_folder_name():
    say("Какую папку открыть?")

    while True:
        en_text, ru_text = voice_processing_x(grammar=json.dumps(english_keywords))

        if en_text in english_keywords:
            print(f"ENG: {en_text}")
            return commands.open_folder(en_text)
        elif ru_text:
            print(f"RU: {ru_text}")
            return commands.open_folder(ru_text)

        say("Не понял какую папку открыть. Повторите название.")

"""======[Уточнение времени для таймера]======"""
def get_timer_duration():
    say("Сколько времени нужно?")
    text = voice_processing()
    seconds = commands.parse_time(text) if text else None
    if seconds:
        return commands.timer(seconds)
    else:
        say("Не понял сколько нужно времени. Повторите.")
        return get_timer_duration()

"""======[Определение действия]======"""
def user_query(text):
    commands_list = {
        # Браузер
    "открой браузер": commands.open_browser,
    "открыть браузер": commands.open_browser,
    "запусти браузер": commands.open_browser,
    "запустить браузер": commands.open_browser,
    "открой интернет": commands.open_browser,
    "запусти интернет": commands.open_browser,

    # Папки (без названия — нужно уточнение)
    "открой папку": get_folder_name,
    "открыть папку": get_folder_name,
    "покажи папку": get_folder_name,
    "открой директорию": get_folder_name,

    # Время
    "сколько времени": commands.show_time,
    "который час": commands.show_time,
    "время": commands.show_time,
    "скажи время": commands.show_time,
    "текущее время": commands.show_time,

    # Таймер
    "поставь таймер": get_timer_duration,
    "таймер": get_timer_duration,
    "засеки время": get_timer_duration,
    "запусти таймер": get_timer_duration,

    # Выход
    "закрой": exit,
    "закрыть": exit,
    "выйти": exit,
    "стоп": exit,
    "остановись": exit,
    "заверши работу": exit,
    "выход": exit,
    }

    for phrase, func in commands_list.items():
        if phrase in text:
            return func()

    print(f"Команды '{text}' нет")
    return say(f"Команды {text} нет")

    # for action in commands_list:
    #
    #     if action == "open_browser":
    #         commands.open_browser()
    #
    #     elif action == "open_folder":
    #         name = params.get("name", "")
    #         if name:
    #             commands.open_folder(name)
    #         else:
    #             folder_name = get_folder_name()
    #             if folder_name:
    #                 commands.open_folder(folder_name)
    #             else:
    #                 say("Не понял, какая папка")
    #
    #     elif action == "timer":
    #         time = params.get("seconds", "")
    #         if time:
    #            commands.timer(time)
    #         else:
    #             time = get_timer_duration()
    #             commands.timer(time) if time else say("Не понял, сколько нужно времени")
    #
    #     elif action == "show_time":
    #         commands.show_time()
    #
    #     elif action == "exit":
    #         say("Прощай!")
    #         exit()
    # else:
    #     say("Такой команды нет")

"""======[Основной код]======"""
def main():
    while True:
        print("Ожидание...")
        say("Ожидание")

        try:
            # Ждём слово-триггер
            if listen_for_trigger():
                say("Что такое?")
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
