import os
import re
import json


def build_english_folder_list():
    english_folders = set()

    # Диски для сканирования (как в твоём build_folder_index)
    drives = ['D:\\', 'Z:\\', 'G:\\']

    english_word_pattern = re.compile(r'\b[a-zA-Z\s]+\b')

    for drive in drives:
        for root, dirs, _ in os.walk(drive):
            for dir_name in dirs:
                words = english_word_pattern.findall(dir_name)

                # Фильтруем: оставляем только сами английские слова
                if words:
                    # Объединяем найденные куски в одну строку
                    full_english_name = ' '.join(words).strip()
                    # Убираем лишние пробелы
                    full_english_name = re.sub(r'\s+', ' ', full_english_name)
                    # Добавляем в нижнем регистре
                    english_folders.add(full_english_name.lower())

    # Сохраняем в файл
    with open('english_folder_names.json', 'w', encoding='utf-8') as f:
        json.dump(list(english_folders), f, ensure_ascii=False, indent=2)

    print(f"Найдено {len(english_folders)} папок с английскими названиями")
    return english_folders