import datetime
import json
import os.path
import threading
import time
import webbrowser
from voice_utils import voice_processing
from tts_service.main import is_running

if is_running():
    from tts_service.main import DioTTS
    speak = DioTTS()
    say = speak.say
else:
    from voice_utils import say

"""==========================================[Открыть браузер]=========================================="""

def open_browser(target = ""):
    url = "https://ya.ru/"
    webbrowser.open(url)
    return speak.say('Открываю браузер')

"""==========================================[Время]=========================================="""
def show_time():
    hours = {
        "0": "ноль часов",
        "1": "один час", "21": "двадцать один час",
        "2": "два часа", "3": "три часа", "4": "четыре часа",
        "22": "двадцать два часа", "23": "двадцать три часа",
        "5": "пять часов", "6": "шесть часов", "7": "семь часов",
        "8": "восемь часов", "9": "девять часов", "10": "десять часов",
        "11": "одиннадцать часов", "12": "двенадцать часов",
        "13": "тринадцать часов", "14": "четырнадцать часов",
        "15": "пятнадцать часов", "16": "шестнадцать часов",
        "17": "семнадцать часов", "18": "восемнадцать часов",
        "19": "девятнадцать часов", "20": "двадцать часов",
        "24": "двадцать четыре часа"
    }
    minutes = {
        "0": "ноль минут",
        "1": "одна минута", "21": "двадцать одна минута",
        "31": "тридцать одна минута", "41": "сорок одна минута", "51": "пятьдесят одна минута",

        "2": "две минуты", "3": "три минуты", "4": "четыре минуты",
        "22": "двадцать две минуты", "23": "двадцать три минуты", "24": "двадцать четыре минуты",
        "32": "тридцать две минуты", "33": "тридцать три минуты", "34": "тридцать четыре минуты",
        "42": "сорок две минуты", "43": "сорок три минуты", "44": "сорок четыре минуты",
        "52": "пятьдесят две минуты", "53": "пятьдесят три минуты", "54": "пятьдесят четыре минуты",

        "5": "пять минут", "6": "шесть минут", "7": "семь минут",
        "8": "восемь минут", "9": "девять минут", "10": "десять минут",
        "11": "одиннадцать минут", "12": "двенадцать минут",
        "13": "тринадцать минут", "14": "четырнадцать минут",
        "15": "пятнадцать минут", "16": "шестнадцать минут",
        "17": "семнадцать минут", "18": "восемнадцать минут",
        "19": "девятнадцать минут", "20": "двадцать минут",
        "25": "двадцать пять минут", "26": "двадцать шесть минут",
        "27": "двадцать семь минут", "28": "двадцать восемь минут",
        "29": "двадцать девять минут", "30": "тридцать минут",
        "35": "тридцать пять минут", "36": "тридцать шесть минут",
        "37": "тридцать семь минут", "38": "тридцать восемь минут",
        "39": "тридцать девять минут", "40": "сорок минут",
        "45": "сорок пять минут", "46": "сорок шесть минут",
        "47": "сорок семь минут", "48": "сорок восемь минут",
        "49": "сорок девять минут", "50": "пятьдесят минут",
        "55": "пятьдесят пять минут", "56": "пятьдесят шесть минут",
        "57": "пятьдесят семь минут", "58": "пятьдесят восемь минут",
        "59": "пятьдесят девять минут"
    }
    h = datetime.datetime.now().strftime("%H").lstrip("0") or "0"
    m = datetime.datetime.now().strftime("%M").lstrip("0") or "0"
    print(f"{h}:{m}")
    say(f'Сейчас {hours[h]} {minutes[m]}')

"""==========================================[Открыть папку]=========================================="""
def open_folder(folder_name = ""):
    update_cache()

    print(folder_name)

    found_path = find_folder_cache(folder_name)
    if found_path:
        os.startfile(found_path)
        return say(f'Открываю {folder_name}')
    else:
        return say(f'Папку "{folder_name}" не нашёл')

def update_cache(max_age_hours = 48):
    if not os.path.exists('folder_cache.json'):
        build_folder_index()
        print("===Кэш обновлен===")
        return

    file_age = time.time() - os.path.getmtime('folder_cache.json')
    if file_age > max_age_hours * 3600:
        print("Кэш устарел, обновляю...")
        build_folder_index()

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
    say(message)

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

"""==========================================[Таймер]=========================================="""
def timer_worker(seconds):
    time.sleep(seconds)
    print("Время вышло")
    return say("Время вышло")


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
        say("Время остановилось")
        thread.start()
    except:
        return print("Ошибка")
"""============================================================================================"""