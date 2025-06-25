from flask import Flask, request, send_file, jsonify
import requests
import io
import base64

app = Flask(__name__)

# ---------- CONFIG ----------
VAJA_API_URL = "https://speech-synthesis-api.nectec.or.th/tts"
VAJA_API_KEY = "bBPTrefkfhEYXr89NuWmaKX585b32al6"
VAJA_SPEAKER = "narumol"

TYPHOON_API_URL = "https://api.aiforthai.in.th/ocr"  # ตัวอย่างของ AI for Thai
TYPHOON_API_KEY = "sk-GpP1k660e16eel96QWGSBVNRbBs55uTB5dwZ4AmlFPmQPXS3"
# ----------------------------

@app.route('/')
def index():
    return jsonify({"status": "OCR + TTS Proxy Online"})

# ✅ OCR Endpoint: รับรูปแล้วส่งไป Typhoon OCR
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

    try:
        response = requests.post(TYPHOON_API_URL, json=payload, headers=headers)
        if response.status_code != 200:
            return jsonify({"error": f"OCR Error: {response.status_code}"}), 500
        ocr_text = response.json().get("original_lines", [])
        full_text = "\n".join(ocr_text)
        return jsonify({"text": full_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ TTS Endpoint: ส่งข้อความไป VAJA
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

    try:
        response = requests.post(VAJA_API_URL, json=payload, headers=headers)

        if response.status_code != 200:
            return jsonify({"error": f"VAJA Error: {response.status_code}"}), 500

        return send_file(io.BytesIO(response.content), mimetype="audio/wav")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
