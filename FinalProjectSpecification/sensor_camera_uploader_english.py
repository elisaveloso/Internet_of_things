import time
import datetime
import os
import requests
import RPi.GPIO as GPIO
from picamera2 import Picamera2
import logging

# === LOG CONFIGURATION ===
logging.basicConfig(
    filename='/tmp/sprom.log',              # Log file name
    level=logging.INFO,                     # Message level to be saved
    format='%(asctime)s - %(message)s'      # Format of each line (with date/time)
)

# === GPIO PINS CONFIGURATION ===
TRIG = 23  # GPIO 23 - Physical pin 16
ECHO = 24  # GPIO 24 - Physical pin 18

# === SENSOR CONFIGURATION ===
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# === CAMERA CONFIGURATION ===
camera = Picamera2()
camera.configure(camera.create_still_configuration())
camera.start()
time.sleep(2)

# === SERVER ADDRESS ===
SERVER_URL = "http://192.168.67.117:5000/upload"  # Change this

def measure_distance():
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
    distance = pulse_duration * 17150
    return round(distance, 2)

def take_photo_and_send():
    for i in range (6): # Take photos at 2fps during 3 seconds (with time.sleep(0.5))
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"photo_{timestamp}_p1.jpg"
        camera.capture_file(filename)
        logging.info(f"[📸] Photo taken: {filename}")

        try:
            with open(filename, 'rb') as f:
                files = {'image': (filename, f)}
                response = requests.post(SERVER_URL, files=files, timeout=5)

            if response.status_code == 200:
                logging.info(f"[✅] Successfully sent! Removing {filename}")
                os.remove(filename)
            else:
                logging.info(f"[⚠️] Error sending: {response.status_code}")
        except Exception as e:
            logging.info(f"[❌] Failed to send image: {e}")
            # still remove or store to retry later
            os.remove(filename)
        time.sleep(0.5)

try:
    print("Starting proximity monitoring...")
    while True:
        dist = measure_distance()
        logging.info(f"Distance: {dist} cm")

        if dist < 30:
            logging.info("[🎯] Object detected! Taking photo...")
            time.sleep(2)
            take_photo_and_send()
            time.sleep(3)  # avoid multiple triggers

        time.sleep(0.5)

except KeyboardInterrupt:
    logging.info("Shutting down...")
    camera.stop()
    GPIO.cleanup()
