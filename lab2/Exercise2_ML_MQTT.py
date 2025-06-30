# Application: Dance motion detection (no movement, slow dance, fast dance).

import time
from lsm6dsox import LSM6DSOX
from machine import Pin, I2C
import network
from umqtt.simple import MQTTClient
import machine

import os
print("Arquivos na raiz do dispositivo:", os.listdir())

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("Santos","12345678")
time.sleep(5)
print(wlan.isconnected())


INT_MODE = True         # Enable interrupts
INT_FLAG = False        # At start, no pending interrupts

mqtt_server = 'broker.hivemq.com'
client_id = 'bigles'
topic_pub = b'TomsHardware'

def mqtt_connect():
    client = MQTTClient(client_id, mqtt_server, keepalive=3600)
    client.connect()
    print('Connected to %s MQTT Broker'%(mqtt_server))
    return client

def reconnect():
    print('Failed to connect to the MQTT Broker. Reconnecting...')
    time.sleep(5)
    machine.reset()

# Define the interrupt handler function.
def imu_int_handler(pin):
    global INT_FLAG
    INT_FLAG = True

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

# Connect to MQTT Broker
try:
    client = mqtt_connect()
except OSError as e:
    reconnect()

while (True):
    if (INT_MODE):
        if (INT_FLAG):
            print("LOOP 1++++++++++++++++\n\n")
            # Interrupt detected, read the MLC output and translate it to a human readable description
            INT_FLAG = False
            result = lsm.read_mlc_output()
            while (result is None):
                print("LOOP 2+++++++++++++++++++++++\n\n")
                result = lsm.read_mlc_output()
                time.sleep_ms(300)
                client.publish(topic_pub, "Waiting for MLC output...")
            # Publish the result to the MQTT topic
            client.publish(topic_pub, DANCE_LABELS[result[0]])
            print("-", DANCE_LABELS[result[0]])
    else:
        print("ELSE+++++++++++++\n\n")
        result = lsm.read_mlc_output()
        if result is not None:
            # Publish the result to the MQTT topic
            client.publish(topic_pub, DANCE_LABELS[result[0]])
            print(DANCE_LABELS[result[0]])
    time.sleep_ms(500)
