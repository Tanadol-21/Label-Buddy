from flask import Flask, request, render_template
import os
import requests
from typhoon_ocr import ocr_document

app = Flask(__name__)
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# API keys
os.environ['TYPHOON_OCR_API_KEY'] = 'sk-SMrtW1JrLSLfYMHZhhD8Kk13A6ZuxnEuZN9RoenbaHbytiF6'
VAJA_API_KEY = 'bBPTrefkfhEYXr89NuWmaKX585b32al6'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['image']
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(image_path)

        # OCR
        text = ocr_document(image_path, task_type="default")

        # สังเคราะห์เสียง
        url = 'https://api.aiforthai.in.th/vaja9/synth_audiovisual'
        headers = {'Apikey': VAJA_API_KEY, 'Content-Type': 'application/json'}
        data = {'input_text': text, 'speaker': 1, 'phrase_break': 0, 'audiovisual': 0}
        response = requests.post(url, json=data, headers=headers)

        audio_file = None
        if response.status_code == 200:
            wav_url = response.json().get('wav_url')
            resp = requests.get(wav_url, headers={'Apikey': VAJA_API_KEY})
            if resp.status_code == 200:
                output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result.wav')
                with open(output_path, 'wb') as f:
                    f.write(resp.content)
                audio_file = 'result.wav'
            else:
                text += "\n\n[❌ ERROR ดาวน์โหลดเสียงล้มเหลว]"
        else:
            text += "\n\n[❌ ERROR แปลงเสียงล้มเหลว]"

        return render_template('index.html', markdown=text, image_file=file.filename, audio_file=audio_file)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
