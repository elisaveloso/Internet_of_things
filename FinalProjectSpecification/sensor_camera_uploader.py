import time
import datetime
import os
import requests
import RPi.GPIO as GPIO
from picamera2 import Picamera2
import logging

logging.basicConfig(
    filename='/tmp/sprom.log',              # Nome do arquivo de log
    level=logging.INFO,                # Nível de mensagens que serão salvas
    format='%(asctime)s - %(message)s' # Como cada linha será formatada (com data e hora)
)


# === CONFIGURAÇÃO DOS PINOS ===
TRIG = 23  # GPIO 23 - Pino físico 16
ECHO = 24  # GPIO 24 - Pino físico 18

# === CONFIGURAÇÃO DO SENSOR ===
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# === CONFIGURAÇÃO DA CÂMERA ===
camera = Picamera2()
camera.configure(camera.create_still_configuration())
camera.start()
time.sleep(2)

# === ENDEREÇO DO SERVIDOR ===
SERVER_URL = "http://192.168.67.117:5000/upload"  # Altere aqui

def medir_distancia():
    GPIO.output(TRIG, False)
    time.sleep(0.05)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distancia = pulse_duration * 17150
    return round(distancia, 2)

def tirar_foto_e_enviar():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"foto_{timestamp}.jpg"
    camera.capture_file(filename)
    logging.info(f"[📸] Foto tirada: {filename}")

    try:
        with open(filename, 'rb') as f:
            files = {'image': (filename, f)}
            response = requests.post(SERVER_URL, files=files, timeout=5)

        if response.status_code == 200:
            logging.info(f"[✅] Enviado com sucesso! Removendo {filename}")
            os.remove(filename)
        else:
            logging.info(f"[⚠️] Erro ao enviar: {response.status_code}")
    except Exception as e:
        logging.info(f"[❌] Falha ao enviar imagem: {e}")
        # remover mesmo assim ou guardar para enviar depois
        os.remove(filename)


try:
    print("Iniciando monitoramento de proximidade...")
    while True:
        dist = medir_distancia()
        logging.info(f"Distância: {dist} cm")

        if dist < 30:
            logging.info("[🎯] Objeto detectado! Tirando foto...")
            time.sleep(2)
	    tirar_foto_e_enviar()
            time.sleep(3)  # evita múltiplos envios por detecção

        time.sleep(0.5)

except KeyboardInterrupt:
    logging.info("Encerrando...")
    camera.stop()
    GPIO.cleanup()
