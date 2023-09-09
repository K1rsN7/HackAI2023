import keyboard
from vosk import Model, KaldiRecognizer  # оффлайн-распознавание от Vosk
from termcolor import colored  # вывод цветных логов (для выделения распознанной речи)
from dotenv import load_dotenv  # загрузка информации из .env-файла
import speech_recognition  # распознавание пользовательской речи (Speech-To-Text)
import pyttsx3  # синтез речи (Text-To-Speech)
from pydub import AudioSegment
from pydub.playback import play
import json  # работа с json-файлами и json-строками
import wave  # создание и чтение аудиофайлов формата wav
import os  # работа с файловой системой
from fuzzywuzzy import fuzz  # Проверка схожести строк

# Чтение json файла
with open('data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

model = Model(r"vosk-model-small-ru-0.22")  # Загрузка модели


def record_and_recognize_audio(is_commands, *args: tuple):
    """
    Запись и распознавание аудио
    """
    with microphone:
        recognized_data = ""

        # запоминание шумов окружения для последующей очистки звука от них
        recognizer.adjust_for_ambient_noise(microphone, duration=0.5)
        try:
            # Понятный вывод в консоли
            if is_commands:
                print("Слушаю команду...")
            else:
                print('Жду команду активации...')
            audio = recognizer.listen(microphone)

            with open("microphone-results.wav", "wb") as wav:
                wav.write(audio.get_wav_data())

        except speech_recognition.WaitTimeoutError:
            pass

        try:
            wave_audio_file = wave.open("microphone-results.wav", "rb")
            print("Начинаю обработку...")
            offline_recognizer = KaldiRecognizer(model, wave_audio_file.getframerate())

            data = wave_audio_file.readframes(wave_audio_file.getnframes())
            if len(data) > 0:
                if offline_recognizer.AcceptWaveform(data):
                    recognized_data = offline_recognizer.Result()

                    # получение данных распознанного текста из JSON-строки (чтобы можно было выдать по ней ответ)
                    recognized_data = json.loads(recognized_data)
                    recognized_data = recognized_data["text"]
        except:
            pass

        return recognized_data


def play_voice_assistant_speech(text_to_speech):
    """
    Проигрывание речи ответов голосового ассистента (без сохранения аудио)
    :param text_to_speech: текст, который нужно преобразовать в речь
    """
    ttsEngine.say(str(text_to_speech))
    ttsEngine.runAndWait()


def play_greetings(*args: tuple):
    """
    Проигрывание звука принятия
    """
    song = AudioSegment.from_wav("new_message_notice.wav")
    play(song)


def execute_command_with_name(command_name: str, *args: list):
    """
    Выполнение заданной пользователем команды и аргументами
    :param command_name: название команды
    :param args: аргументы, которые будут переданы в метод
    :return:
    """
    for key in commands.keys():
        answers = ''  # Ответ бота
        accuracy_best = 0  # Лучшая точность
        for fragment in data:
            accuracy = fuzz.ratio(command_name, fragment['key'])
            if accuracy > accuracy_best:
                accuracy_best = accuracy
                answers = fragment['answers']
        print(colored(f'Key: {answers}\n'
                      f'Accuracy: {accuracy_best}', 'green'))
        if accuracy_best >= 65:  # Порог срабатывания команды
            print(colored(f'Ассистент: {answers}', 'blue'))
            play_voice_assistant_speech(answers)
        else:
            print(colored('Ассистент: я не распознала команду', 'blue'))
            play_voice_assistant_speech('я не распознала команду')


# быстрые команды бота
commands = {
    ("привет аня",): play_greetings,  # команда активации
}

if __name__ == "__main__":

    # инициализация инструментов распознавания и ввода речи
    recognizer = speech_recognition.Recognizer()
    microphone = speech_recognition.Microphone()

    # инициализация инструмента синтеза речи
    ttsEngine = pyttsx3.init()

    # загрузка информации из .env-файла (там лежит API-ключ для OpenWeatherMap)
    load_dotenv()

    while True:
        # старт записи речи с последующим выводом распознанной речи и удалением записанного в микрофон аудио
        voice_input = ''
        keyboard_pc = False
        if not (keyboard.is_pressed('alt')):
            voice_input = record_and_recognize_audio(False)
            os.remove("microphone-results.wav")
        else:
            keyboard_pc = True
        print(colored(f'Услышала: {voice_input}', "blue"))
        if voice_input != '' or keyboard_pc:
            for key in commands.keys():
                answer = ''  # Ответ
                accurasy_best = 0  # Точность лучшего ответа
                for activ_fraza in key:
                    accurasy = fuzz.ratio(voice_input, activ_fraza)
                    if accurasy > accurasy_best:
                        accurasy_best = accurasy
                if accurasy_best >= 75 or keyboard_pc:
                    print(colored('Услышала фразу активации', 'blue'))
                    keyboard_pc = False
                    commands[key]()
                    voice_input = record_and_recognize_audio(True)
                    # Пред обработка текста
                    numbers = {'ноль': '0', 'один': '1', 'два': '2', 'три': '3', 'четыре': '4', 'пять': '5',
                               'шесть': '6', 'семь': '7',
                               'восемь': '8', 'девять': '9'}
                    for key in numbers.keys():
                        voice_input = voice_input.replace(key, numbers[key])

                    print(colored(f'Обработала: {voice_input}', 'blue'))
                    execute_command_with_name(voice_input)  # Поиск по файлу
