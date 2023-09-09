# -*- coding: utf-8 -*-
# Импорт библиотек
import io
import re
import pandas as pd
from transliterate import translit


# Функция обработки строки
def replace_function(line):
    line = line.lower()
    for symbol in ["'", '"', '(', ')', '/', '.', '!', '\\', ';', ',', '[', ']', ' ']:
        line = line.replace(symbol, '')
    replase_str = {'+': 'плюс', '%': ' процентов', '°': ' градусов', '°с': ' цельсия'
                   }
    for key in replase_str.keys():
        line = line.replace(str(key), str(replase_str[key]))
    line = translit(line, 'ru')
    return line


path = 'C:\\Users\\k1rsn\Desktop\\Перечень неисправностей.txt'  # Путь к файлу
flag_malfunction = True  # Флаг на пункт таблицы
flag_skip = False  # Пропустить следующую строку, реализовано для пропуска "Вероятная причина"
file_new = io.open('C:\\Users\\k1rsn\Desktop\\info.txt', 'w', encoding='utf-8')  # Открытие файла для записи
with io.open(path, encoding='utf-8') as file:
    for line in file:  # Чтение файла по строчно
        line = replace_function(line)  # Обработка строки
        try:  # Проверка на строчку пункта
            nums = re.findall(r'\d+', line)
            if f'{nums[0]}\n' == line:
                flag_malfunction = True
                file_new.write('key: ')
                flag_skip = False
                continue
        except:
            pass
        if flag_malfunction and line != '\n':
            if line[0] == '-':
                flag_skip = False
            if flag_skip:
                flag_skip = False
                continue
            else:
                line = line.replace('-', '')
                file_new.writelines(line)
                flag_skip = True
        else:
            flag_malfunction = False
            flag_skip = False

data = []  # Массив с данными
key = ''  # Активационной фраза
answers = ''  # Решение неисправности
with io.open('C:\\Users\\k1rsn\Desktop\\info.txt', 'r', encoding='utf-8') as file:
    for line in file:
        if line[0:5] == 'key: ':  # Проверка на активационную фразу
            data.append({'key': str(key[5:-1]).lower(), 'answers': str(answers).lower()})
            answers = ''
            key = line
        else:
            answers += f'{line[:-1]} '
df = pd.DataFrame(data=data)  # Формирование датафрейма
df = df.iloc[1:, :]  # Убирание первой строки данных
df = df.groupby(['key'], as_index=False).agg({'answers': ' или '.join})
df.to_csv(r'C:\\Users\\k1rsn\Desktop\\data.csv', index=False)  # Запись в csv
df.to_json(r'C:\\Users\\k1rsn\Desktop\\data.json', orient='records')
