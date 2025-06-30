# Application: Dance motion detection (no movement, slow dance, fast dance).

import time
from lsm6dsox import LSM6DSOX
from machine import Pin, I2C
import machine
import network
from umqtt.simple import MQTTClient

import os
print("Arquivos na raiz do dispositivo:", os.listdir())

# === CONSTANTS ===

# Configure the MQTT
mqtt_server = 'broker.hivemq.com'
client_id = 'bigles'
topic_pub = b'TomsHardware'
# topic_msg = b'Movement Detected'

INT_MODE = True         # Enable interrupts
INT_FLAG = False        # At start, no pending interrupts

# WiFi credentials
SSID = 'Santos'
PASSWORD = '12345678'

# === FUNCTIONS ===
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        print("Conectando ao WiFi...")
        time.sleep(1)
    time.sleep(3)
    print(wlan.isconnected())
    print("Conectado ao WiFi:", wlan.ifconfig())

def mqtt_connect():
    client = MQTTClient(client_id, mqtt_server, keepalive=3600)
    client.connect()
    print("Connected to %s MQTT Broker'%(mqtt_server)")
    return client

def reconnect():
    print('Failed to connect to the MQTT Broker. Reconnecting...')
    time.sleep(5)
    machine.reset()


# Define the interrupt handler function.
def imu_int_handler(pin):
    global INT_FLAG
    INT_FLAG = True

# === MAIN ===
# Configure the external interrupt (IMU).
if (INT_MODE == True):
    int_pin = Pin(24)
    int_pin.irq(handler=imu_int_handler, trigger=Pin.IRQ_RISING)

# Initialize an I2C object.
i2c = I2C(0, scl=Pin(13), sda=Pin(12))

# Pre-trained model configuration
# Selected data rate and scale must match the MLC data rate and scale configuration.
UCF_FILE = "lsm6dsox_vibration_monitoring.ucf"

# Map MLC output states to dance labels
DANCE_LABELS = {
    0: "dance|NO_DANCING",
    1: "dance|SLOW_DANCING",
    2: "dance|FAST_DANCING"
}
print(i2c)
# Initialize sensor with MLC
lsm = LSM6DSOX(i2c,
               gyro_odr=26,
               accel_odr=26,
               gyro_scale=2000,
               accel_scale=4,
               ucf=UCF_FILE)

print("\n--------------------------------")
print("- Dance Motion Detection Example -")
print("--------------------------------\n")
print("- MLC configured for dance states...\n")

# Connect to WiFi
connect_wifi()

# Connect to MQTT Broker
try:
    client = mqtt_connect()
except OSError as e:
    reconnect()

while (True):
    if (INT_MODE):
        if (INT_FLAG):
            # Interrupt detected, read the MLC output and translate it to a human readable description
            INT_FLAG = False
            result = lsm.read_mlc_output()
            while (result is None):
                result = lsm.read_mlc_output()
            label = DANCE_LABELS.get(result[0], "Unknown")
            print("-", label)
            client.publish(topic_pub, label)

            print("-", DANCE_LABELS[result[0]])
    else:
        result = lsm.read_mlc_output()
        if result is not None:
            label = DANCE_LABELS.get(result[0], "Unknown")
            print(DANCE_LABELS[result[0]])
            client.publish(topic_pub, label)
    # adjust the polling interval as needed
    time.sleep_ms(500)
