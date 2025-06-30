# Application: Dance motion detection (no movement, slow dance, fast dance).

import time
from lsm6dsox import LSM6DSOX
from machine import Pin, I2C

import os
print("Arquivos na raiz do dispositivo:", os.listdir())


INT_MODE = True         # Enable interrupts
INT_FLAG = False        # At start, no pending interrupts

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

while (True):
    if (INT_MODE):
        if (INT_FLAG):
            # Interrupt detected, read the MLC output and translate it to a human readable description
            INT_FLAG = False
            result = lsm.read_mlc_output()
            while (result is None):
                result = lsm.read_mlc_output()

            print("-", DANCE_LABELS[result[0]])
    else:
        result = lsm.read_mlc_output()
        if result is not None:
            print(DANCE_LABELS[result[0]])
    # adjust the polling interval as needed
    time.sleep_ms(500)
