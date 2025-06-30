from flask import Flask, request, send_from_directory, render_template_string, redirect, url_for
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import threading
import shutil
import time
import requests
import cv2

app = Flask(__name__)

UPLOAD_FOLDER = 'uploaded_images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8" />
    <title>Galerie d'images</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f0f0f0;
        }
        h1 {
            color: #333;
        }
        form {
            margin-bottom: 20px;
        }
        label {
            margin-right: 10px;
        }
        select, input[type=date], button {
            padding: 5px 10px;
            margin-right: 15px;
            font-size: 14px;
        }
        ul {
            list-style: none;
            padding: 0;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 15px;
        }
        li {
            background: white;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 0 8px rgba(0,0,0,0.1);
            text-align: center;
        }
        img {
            max-width: 100%;
            height: auto;
            border-radius: 5px;
        }
        strong {
            display: block;
            margin-top: 8px;
            font-size: 16px;
        }
        select.status-select {
            font-weight: bold;
            margin-top: 5px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <h1>Galerie d'images uploadées</h1>
    <form method="get">
        <label for="date">Date:</label>
        <input type="date" name="date" id="date" value="{{ date }}">

        <label for="hour_start">Début :</label>
        <select name="hour_start" id="hour_start">
            <option value="">--</option>
            {% for h in hours %}
                <option value="{{ h }}" {% if hour_start == h %}selected{% endif %}>{{ h }}</option>
            {% endfor %}
        </select>
        :
        <select name="minute_start" id="minute_start">
            <option value="">--</option>
            {% for m in minutes %}
                <option value="{{ m }}" {% if minute_start == m %}selected{% endif %}>{{ m }}</option>
            {% endfor %}
        </select>

        <label for="hour_end">Fin :</label>
        <select name="hour_end" id="hour_end">
            <option value="">--</option>
            {% for h in hours %}
                <option value="{{ h }}" {% if hour_end == h %}selected{% endif %}>{{ h }}</option>
            {% endfor %}
        </select>
        :
        <select name="minute_end" id="minute_end">
            <option value="">--</option>
            {% for m in minutes %}
                <option value="{{ m }}" {% if minute_end == m %}selected{% endif %}>{{ m }}</option>
            {% endfor %}
        </select>

        <label for="status">Statut:</label>
        <select name="status" id="status">
            <option value="" {% if status == "" %}selected{% endif %}>--Tous--</option>
            <option value="ok" {% if status == "ok" %}selected{% endif %}>✅ OK</option>
            <option value="notok" {% if status == "notok" %}selected{% endif %}>❌ Not OK</option>
        </select>

        <button type="submit">Filtrer</button>
        <button type="button" onclick="window.location='/'">Réinitialiser</button>
    </form>

    <ul>
    {% if images %}
        {% for image, label in images %}
        <li>
            <img src="/images/{{ image }}" alt="{{ image }}">
            <strong>{{ image }} — {{ label }}</strong>
            <form method="post" action="{{ url_for('change_status', filename=image) }}">
                <select name="new_status" class="status-select" onchange="this.form.submit()">
                    <option value="ok" {% if label == "✅ OK" %}selected{% endif %}>✅ OK</option>
                    <option value="notok" {% if label == "❌ Not OK" %}selected{% endif %}>❌ Not OK</option>
                </select>
            </form>
        </li>
        {% endfor %}
    {% else %}
        <p>Aucune image correspondant aux filtres.</p>
    {% endif %}
    </ul>
</body>
</html>
"""

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return 'No image uploaded', 400
    file = request.files['image']
    if file.filename == '':
        return 'No selected file', 400

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = timestamp + '_' + secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    if not is_well_framed(filepath):
        os.rename(filepath, os.path.join(app.config['UPLOAD_FOLDER'], 'CROSS_' + filename))
    else:
        os.rename(filepath, os.path.join(app.config['UPLOAD_FOLDER'], 'OK_' + filename))

    return 'Image received', 200

@app.route('/')
def gallery():
    date_filter = request.args.get('date')
    hour_start = request.args.get('hour_start')
    minute_start = request.args.get('minute_start')
    hour_end = request.args.get('hour_end')
    minute_end = request.args.get('minute_end')
    status_filter = request.args.get('status', '').lower()

    def to_minutes(h, m):
        return int(h) * 60 + int(m)

    start_min = end_min = None
    if hour_start and minute_start:
        start_min = to_minutes(hour_start, minute_start)
    if hour_end and minute_end:
        end_min = to_minutes(hour_end, minute_end)

    all_images = sorted(os.listdir(UPLOAD_FOLDER), reverse=True)
    filtered_images = []

    for image in all_images:
        try:
            clean_name = image
            if clean_name.startswith("OK_"):
                clean_name = clean_name[3:]
            elif clean_name.startswith("CROSS_"):
                clean_name = clean_name[6:]

            parts = clean_name.split('_')
            date_str = parts[0]
            time_str = parts[1]
            hour_str, minute_str, _ = time_str.split('-')

            if date_filter and date_filter != date_str:
                continue

            current_min = to_minutes(hour_str, minute_str)
            if start_min is not None and current_min < start_min:
                continue
            if end_min is not None and current_min > end_min:
                continue

            if status_filter == "ok" and not image.startswith("OK_"):
                continue
            if status_filter == "notok" and not image.startswith("CROSS_"):
                continue

            label = "✅ OK" if image.startswith("OK_") else "❌ Not OK"
            filtered_images.append((image, label))
        except Exception:
            continue

    hours = [f"{i:02}" for i in range(24)]
    minutes = [f"{i:02}" for i in range(60)]

    return render_template_string(
        HTML_TEMPLATE,
        images=filtered_images,
        date=date_filter or '',
        hour_start=hour_start or '',
        minute_start=minute_start or '',
        hour_end=hour_end or '',
        minute_end=minute_end or '',
        status=status_filter or '',
        hours=hours,
        minutes=minutes,
    )

@app.route('/images/<filename>')
def get_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/change_status/<filename>', methods=['POST'])
def change_status(filename):
    new_status = request.form.get('new_status')
    if new_status not in ['ok', 'notok']:
        return "Statut invalide", 400

    current_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(current_path):
        return "Fichier introuvable", 404

    if filename.startswith('OK_'):
        base_name = filename[3:]
    elif filename.startswith('CROSS_'):
        base_name = filename[6:]
    else:
        base_name = filename

    new_filename = ('OK_' if new_status == 'ok' else 'CROSS_') + base_name
    new_path = os.path.join(UPLOAD_FOLDER, new_filename)

    if os.path.exists(new_path):
        return "Nom de fichier déjà existant", 400

    os.rename(current_path, new_path)
    return redirect(request.referrer or url_for('gallery'))

def is_well_framed(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
    return laplacian_var > 100

def weekly_cleanup():
    while True:
        now = datetime.now()
        next_sunday = now + timedelta((6 - now.weekday()) % 7 + 1)
        next_reset = datetime.combine(next_sunday, datetime.min.time())
        wait_seconds = (next_reset - now).total_seconds()
        threading.Timer(wait_seconds, clear_upload_folder).start()
        break

def clear_upload_folder():
    shutil.rmtree(UPLOAD_FOLDER)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    weekly_cleanup()

if __name__ == '__main__':
    weekly_cleanup()
    app.run(host='0.0.0.0', port=5000)
