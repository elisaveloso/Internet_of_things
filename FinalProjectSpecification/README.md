## 🏭 Real-world Simulation: Sugarcane Plant Scenario

This project simulates real-time operations in sugarcane processing plants using a Raspberry Pi and an ultrasonic proximity detection system.

### System Workflow

1. **Continuous Monitoring:**  
    The ultrasonic sensor continuously monitors the designated area.

2. **Object Detection:**  
    When an object is detected within 30 centimeters, the system is triggered.

3. **Image Capture:**  
    The Pi Camera captures **6 consecutive images** at **2 frames per second** over a **3-second period**.

### Purpose

This logic replicates the detection of a bucket or dumping action in an industrial environment, ensuring that key moments are accurately captured for further analysis.

---

**Key Features:**
- Real-time proximity detection
- Automated image capture
- Designed for industrial simulation scenarios
- Enables accurate event documentation

## 🚀 How to Run


### 🔹 Final Project – Smart Proximity Photo Capture (SPROM)

Located in the `FinalProject/` directory, this is a complete end-to-end IoT solution combining:

- 🖼️ Raspberry Pi Zero 2W with Pi Camera
- 📏 Ultrasonic sensor for object detection
- 📤 Automatic photo capture and upload to a web server
- 🌐 Flask-based server to display uploaded images
- 🔌 `systemd` integration for auto-execution at boot
- 📝 Full documentation available in `documentation.pdf`

#### 🏭 Real-world Simulation: Sugarcane Plant Scenario

To simulate real-time operation in sugarcane processing plants, the proximity detection system runs continuously on the Raspberry Pi. The ultrasonic sensor constantly monitors the area until it detects an object closer than **30 centimeters**.

When such an object is detected, it triggers the Pi Camera to capture **6 consecutive images** at **2 frames per second (fps)** over a **3-second period**.

This logic is designed to replicate how **a bucket or dumping action** would be detected in a real industrial environment, ensuring key moments are captured accurately for further analysis.

---

## ▶️ How to Run This Project (SPROM – Smart Proximity Photo Capture)

### 🧰 Requirements

- Raspberry Pi Zero 2W (or compatible)
- Raspberry Pi Camera (e.g. OV5647), properly connected
- HC-SR04 Ultrasonic Sensor
- MicroSD card with Raspberry Pi OS (Lite or Desktop)
- Laptop/PC on the same Wi-Fi network
- Basic jumper wires and 2 × 1kΩ resistors for voltage divider
- Internet for initial package installation

### 📦 1. Raspberry Pi Setup

1. Flash Raspberry Pi OS using [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Enable **SSH** and **Wi-Fi** (via `raspi-config` or `wpa_supplicant.conf`)
3. Boot the Pi and connect via SSH:

```bash
ssh pi@<raspberry-ip>
```

### 📷 2. Enable Camera and Update

```bash
sudo raspi-config
# Interface Options → Enable Camera
sudo apt update && sudo apt full-upgrade -y
sudo reboot
```

### 🔌 3. Hardware Wiring

| HC-SR04 Pin | Raspberry Pi Pin |
|-------------|------------------|
| VCC         | 5V (Pin 2)       |
| GND         | GND (Pin 6)      |
| TRIG        | GPIO23 (Pin 16)  |
| ECHO        | GPIO24 (Pin 18)* |

> ⚠️ Use a **voltage divider** with two 1kΩ resistors on the ECHO line to reduce 5V to 3.3V.

### ⚙️ 4. Install Dependencies on the Pi

```bash
sudo apt install python3-picamera2 python3-requests python3-flask libcamera-apps
```

### 📝 5. Configure the Sensor + Camera Script

1. Place `sensor_camera_uploader.py` in `/home/pi/`
2. Edit the script and set your **Flask server IP**:

```python
SERVER_URL = "http://<your-laptop-ip>:5000/upload"
```

### 🔁 6. Set the Script to Start Automatically (Optional)

Create a file:

```bash
sudo nano /etc/systemd/system/sprom.service
```

Paste:

```ini
[Unit]
Description=SPROM sensor-camera uploader
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/sensor_camera_uploader.py
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Then activate:

```bash
sudo systemctl daemon-reload
sudo systemctl enable sprom
sudo systemctl start sprom
```

### 🖥️ 7. Start the Flask Server (on your PC/laptop)

```bash
pip install flask
cd FinalProject
python app.py
```

Then open your browser:

```
http://localhost:5000/
```

Or from another device:

```
http://<your-laptop-ip>:5000/
```

### 📸 8. How It Works

- The ultrasonic sensor continuously measures distance.
- When an object is closer than 30 cm:
  - Waits 2 seconds
  - Captures 6 photos over 3 seconds (2 fps)
  - Sends each image to a Flask server
  - Server displays the images in a gallery
  - The Raspberry Pi deletes each image after sending it

---

## 👩‍💻 Author

**Elisa Veloso**  
GitHub: [@elisaveloso](https://github.com/elisaveloso)  
IoT Project – 2025

---

## 📜 License

This project is for educational purposes. You are free to explore and adapt it for learning.