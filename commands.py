def update_cache(max_age_hours = 48):
    if not os.path.exists('folder_cache.json'):
        build_folder_index()
        print("===Кэш обновлен===")
        return

    file_age = time.time() - os.path.getmtime('folder_cache.json')
    if file_age > max_age_hours * 3600:
        print("Кэш устарел, обновляю...")
        build_folder_index()

"""==========================================[Открыть браузер]=========================================="""

def open_browser(target = ""):
    url = "https://ya.ru/"
    webbrowser.open(url)
    return speak.say('Открываю браузер')
import datetime
import json
import os.path
import threading
import time
import webbrowser
from tts_service import main
from main import voice_processing
speak = main.DioTTS()

"""==========================================[Время]=========================================="""
def show_time():
    hours = {
        "1": "час", "21": "час",
        "2": "часа", "3": "часа", "4": "часа", "22": "часа", "23": "часа", "24": "часа",
    }
    minutes = {
        "1": "1 минута", "21": "21 минута", "31": "31 минута", "41": "41 минута", "51": "51 минута",
        "2": "2 минуты", "3": "3 минуты", "4": "4 минуты", "22": "22 минуты", "23": "23 минуты", "24": "24 минуты", "32": "32 минуты", "33": "33 минуты", "34": "34 минуты", "42": "42 минуты", "43": "43 минуты", "44": "44 минуты", "52": "52 минуты", "53": "53 минуты", "54": "54 минуты",
    }
    h = datetime.datetime.now().strftime("%H")
    m = datetime.datetime.now().strftime("%M")
    print(f"{h}-{m}")
    if h in hours and m in minutes:
        speak.say(f'Сейчас {hours[h]} {minutes[m]}')
    elif h in hours:
        speak.say(f'Сейчас {hours[h]} {m} минут')
    elif m in minutes:
        speak.say(f'Сейчас {h} часов {minutes[m]}')
    else:
        speak.say(f'Сейчас {h} часов {m} минут')

"""==========================================[Открыть папку]=========================================="""
def open_folder(folder_name = ""):
    update_cache()

    print(folder_name)

    found_path = find_folder_cache(folder_name)
    if found_path:
        os.startfile(found_path)
        return speak.say(f'Открываю {folder_name}')
    else:
        return speak.say(f'Папку "{folder_name}" не нашёл')

def build_folder_index(max_depth = 30):
    cache = {}

    for drive in ['D:\\','Z:\\','G:\\']:
        for root, dirs, _ in os.walk(drive):
            depth = root.count('\\') - drive.count('\\')
            if depth > max_depth:
                break

            for dir_name in dirs:
                if dir_name.lower() not in cache:
                    cache[dir_name.lower()] = []
                cache[dir_name.lower()].append(os.path.join(root, dir_name))

    with open('folder_cache.json', 'w', encoding='utf-8') as f:
        json.dump(cache, f)

    return cache

def find_folder_cache(folder_name):
    print("===Поиск начался===")
    if os.path.exists('folder_cache.json'):
        print("Файл с кэшем найден")
        with open('folder_cache.json', 'r', encoding='utf-8') as f:
            print("Файл открыт")
            cache = json.load(f)

    else:
        print("Файл с кэшем не найден")
        cache = build_folder_index()

    if folder_name.lower() in cache:
        # print(folder_name)
        path = cache[folder_name.lower()]
        if len(path) == 1:
            return path[0]
        else:
            return select_folder(path, folder_name)

    return None

def select_folder(paths, folder_name):
    message = f"Найдено несколько папок {folder_name}. "
    for i, path in enumerate(paths, 1):
        path = path.split('\\')
        path = '\\'.join(path[-2:])
        message += f"{i}: {path}. "
    message += "Папку под каким номером нужно открыть?"

    # print(paths)
    print(message.split(' '))
    speak.say(message)

    while True:
        response = voice_processing(chunk_multiplier=5)

        # Если это просто цифра
        if response.isdigit():
            print(paths[int(response) - 1])
            return paths[int(response) - 1]

        number_map = {
            'один': 1, 'одну': 1, 'первый': 1, 'первую': 1,
            'два': 2, 'две': 2, 'второй': 2, 'вторую': 2,
            'три': 3, 'третий': 3, 'третью': 3,
            'четыре': 4, 'четвертый': 4, 'четвертую': 4,
            'пять': 5, 'пятый': 5, 'пятую': 5,
            'шесть': 6, 'шестой': 6, 'шестую': 6,
            'семь': 7, 'седьмой': 7, 'седьмую': 7,
            'восемь': 8, 'восьмой': 8, 'восьмую': 8,
            'девять': 9, 'девятый': 9, 'девятую': 9,
            'десять': 10, 'десятый': 10, 'десятую': 10,
            'номер один': 1, 'номер 1': 1,
            'номер два': 2, 'номер 2': 2,
            'номер три': 3, 'номер 3': 3,
        }

        for word, num in number_map.items():
            if word in response:
                print(paths[num - 1])
                return paths[num - 1]

# commands = {"привет": "Привет, меня зовут Kibou",
#             "как дела": "У меня все хорошо. Спасибо, что спросили",
#             "врем": f'Сейчас {datetime.datetime.now().strftime("%H:%M")}',
#             "час": time(),
#             "пока": "До скорого"}
"""==========================================[Таймер]=========================================="""
def timer_worker(seconds):
    time.sleep(seconds)
    print("Время вышло")
    return speak.say("Время возобновило ход")


def parse_time(text):
    words = text.lower().split()
    number_words = {
        'ноль': 0, 'один': 1, 'одна': 1, 'одну': 1, 'два': 2, 'две': 2, 'три': 3, 'четыре': 4,
        'пять': 5, 'шесть': 6, 'семь': 7, 'восемь': 8, 'девять': 9,
        'десять': 10, 'одиннадцать': 11, 'двенадцать': 12, 'тринадцать': 13,
        'четырнадцать': 14, 'пятнадцать': 15, 'шестнадцать': 16, 'семнадцать': 17,
        'восемнадцать': 18, 'девятнадцать': 19, 'двадцать': 20, 'тридцать': 30,
        'сорок': 40, 'пятьдесят': 50, 'шестьдесят': 60, 'семьдесят': 70,
        'восемьдесят': 80, 'девяносто': 90, 'сто': 100, 'двести': 200,
        'триста': 300, 'четыреста': 400, 'пятьсот': 500
    }

    total_seconds = 0
    current = 0

    i = 0
    while i < len(words):
        word = words[i]

        # Число
        if word in number_words:
            current = number_words[word]
            # составное число (двадцать пять)
            if i + 1 < len(words) and words[i + 1] in number_words:
                current += number_words[words[i + 1]]
                i += 1
            i += 1

        # Единица времени
        elif word in ['минут', 'минуты', 'минуту', 'мин', 'минута']:
            total_seconds += current * 60
            current = 0
            i += 1

        elif word in ['секунд', 'секунды', 'секунду', 'сек', 'секунда']:
            total_seconds += current * 1
            current = 0
            i += 1

        # Слова-паразиты
        else:
            current = 0
            i += 1

    return total_seconds

def timer(seconds):
    try:
        #seconds = parse_time(text)
        print(f"Таймер на: {seconds} секунд")
        thread = threading.Thread(target=timer_worker, args=(seconds,))
        speak.say("Время остановилось")
        thread.start()
    except:
        return print("Ошибка")
"""============================================================================================"""