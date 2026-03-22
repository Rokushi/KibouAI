import subprocess
import time
import requests
import os
import atexit
import pygame
import io

class DioTTS:
    """Класс для работы с TTS сервисом"""
    def __init__(self):
        self.process = None
        self.start_server()
        atexit.register(self.stop_server)

    def start_server(self):
        """Запускает сервер в фоне"""
        server_dir = os.path.dirname(os.path.abspath(__file__))
        #print(f"[DEBUG] server_dir = {server_dir}")
        python_path = os.path.join(server_dir, "venv_tts", "Scripts", "python.exe")
        #print(f"[DEBUG] python_path = {python_path}")
        #print(f"[DEBUG] exists? {os.path.exists(python_path)}")
        server_path = os.path.join(server_dir, "server.py")
        #print(f"[DEBUG] server_path = {server_path}")
        #print(f"[DEBUG] exists? {os.path.exists(server_path)}")

        #os.system("for /f \"tokens=5\" %a in ('netstat -ano ^| findstr :8000') do taskkill /F /PID %a 2>nul")

        self.process = subprocess.Popen(
            [python_path, server_path],
            cwd=server_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW,
            text=True
        )

        time.sleep(10)

        if self.process.poll() is not None:
            stdout, stderr = self.process.communicate()
            print(f"[DioTTS] Сервер упал сразу! Код возврата: {self.process.returncode}")
            print("=== STDOUT ===")
            print(stdout)
            print("=== STDERR ===")
            print(stderr)
            raise RuntimeError(f"Сервер не запустился: {stderr}")

        print("[DioTTS] Сервер запущен, проверяем health...")

        for attempt in range(30):
            try:
                timeout = 5 if attempt < 5 else 2
                response = requests.get("http://127.0.0.1:8000/health", timeout=timeout)
                if response.status_code == 200:
                    print("==TTS SERVICE IS READY==")
                    return

            except requests.exceptions.ConnectionError:
                print(f"[DioTTS] Попытка {attempt+1}: сервер ещё не отвечает")
            except Exception as e:
                print(f"[DioTTS] Попытка {attempt+1}: ошибка {e}")
            time.sleep(1)

        # for _ in range(30):
        #     try:
        #         requests.get("http://127.0.0.1:8000/health", timeout=1)
        #         print("==TTS сервис готов==")
        #         return
        #     except Exception as e:
        #         print(f"[DioTTS] Ошибка: {e}")
        #         time.sleep(1)
        #
        # raise RuntimeError("TTS сервис не запустился")

    def stop_server(self):
        """Останавливает сервер"""
        if self.process:
            self.process.kill()
            #os.system("for /f \"tokens=5\" %a in ('netstat -ano ^| findstr :8000') do taskkill /F /PID %a 2>nul")

    def say(self, text: str, save_path: str = "output.wav"):
        """Генерирует речь"""

        response = requests.post(
            "http://127.0.0.1:8000/tts",
            json={"text": text},
            timeout=30
        )

        # Сохраняем как есть, чтобы посмотреть
        with open("raw_response.bin", "wb") as f:
            f.write(response.content)

        try:
            with open("temp.wav", "wb") as f:
                f.write(response.content)

            pygame.mixer.init(frequency=24000, size=-16, channels=1)
            sound = pygame.mixer.Sound("temp.wav")
            sound.play()

            print("[DEBUG] Начал говорить")
            while pygame.mixer.get_busy():
                pygame.time.Clock().tick(10)
            print("[DEBUG] Закончил говорить")
        except Exception as e:
            print({e})

        with open(save_path, "wb") as f:
            f.write(response.content)