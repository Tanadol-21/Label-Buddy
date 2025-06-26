from flask import Flask, request, send_file, jsonify
import requests
import io
import base64
import os

app = Flask(__name__)

# กำหนด API Key จาก Environment Variables
VAJA_API_KEY = os.environ.get("VAJA_API_KEY")
TYPHOON_API_KEY = os.environ.get("TYPHOON_API_KEY")

VAJA_API_URL = "https://speech-synthesis-api.nectec.or.th/tts"
VAJA_SPEAKER = "narumol"
TYPHOON_API_URL = "https://api.aiforthai.in.th/ocr"  # ตัวอย่าง URL OCR

if not VAJA_API_KEY or not TYPHOON_API_KEY:
    raise Exception("API Keys for VAJA or Typhoon are missing!")

@app.route('/')
def home():
    return jsonify({"status": "Label Buddy Backend is running"})

@app.route('/ocr', methods=["POST"])
def ocr():
    if 'image' not in request.files:
        return jsonify({"error": "Missing image"}), 400

    image_file = request.files['image']
    image_bytes = image_file.read()
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')

    headers = {
        "Apikey": TYPHOON_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "file": encoded_image,
        "detectOrientation": True
    }

    response = requests.post(TYPHOON_API_URL, json=payload, headers=headers)

    if response.status_code != 200:
        return jsonify({"error": f"OCR API error: {response.status_code}"}), 500

    ocr_text = response.json().get("original_lines", [])
    full_text = "\n".join(ocr_text)
    return jsonify({"text": full_text})

@app.route('/tts')
def tts():
    text = request.args.get("text")
    if not text:
        return jsonify({"error": "Missing 'text' parameter"}), 400

    headers = {
        "Authorization": f"Bearer {VAJA_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "speaker": VAJA_SPEAKER,
        "format": "wav"
    }

    response = requests.post(VAJA_API_URL, json=payload, headers=headers)

    if response.status_code != 200:
        return jsonify({"error": f"VAJA API error: {response.status_code}"}), 500

    return send_file(io.BytesIO(response.content), mimetype="audio/wav")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
