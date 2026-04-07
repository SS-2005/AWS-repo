import base64
import os
from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import tensorflow as tf
import tensorflow_hub as hub
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from PIL import Image
from tensorflow.keras.preprocessing import image

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / 'full-image-set-mobilenetv2-adam.h5'
LABELS_PATH = BASE_DIR / 'labels.csv'
IMG_SIZE = 224
REQUEST_TIMEOUT_SECONDS = 20
MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
CORS(app)

_model = None
_unique_breeds = None


def load_labels():
    global _unique_breeds
    if _unique_breeds is not None:
        return _unique_breeds
    if LABELS_PATH.exists():
        labels_df = pd.read_csv(LABELS_PATH)
        _unique_breeds = np.sort(labels_df.breed.unique())
    else:
        _unique_breeds = np.array([f'breed_{i}' for i in range(120)])
    return _unique_breeds


def load_model_once():
    global _model
    if _model is None:
        custom_objects = {'KerasLayer': hub.KerasLayer}
        _model = tf.keras.models.load_model(str(MODEL_PATH), custom_objects=custom_objects)
    return _model


def preprocess_image(img: Image.Image):
    img = img.resize((IMG_SIZE, IMG_SIZE))
    img_array = image.img_to_array(img)
    img_array = tf.expand_dims(img_array, axis=0)
    return img_array / 255.0


def predict_breed(img: Image.Image):
    model = load_model_once()
    labels = load_labels()

    processed_img = preprocess_image(img)
    predictions = model.predict(processed_img, verbose=0)

    predicted_idx = int(np.argmax(predictions[0]))
    confidence = float(np.max(predictions[0]))
    predicted_breed = str(labels[predicted_idx])

    top_5_indices = np.argsort(predictions[0])[-5:][::-1]
    top_predictions = [
        {
            'breed': str(labels[idx]),
            'confidence': round(float(predictions[0][idx] * 100), 2),
        }
        for idx in top_5_indices
    ]

    return predicted_breed, round(confidence * 100, 2), top_predictions


def image_to_base64(img: Image.Image):
    buffered = BytesIO()
    img.thumbnail((300, 300))
    img.save(buffered, format='JPEG')
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'model_file_present': MODEL_PATH.exists(),
        'labels_file_present': LABELS_PATH.exists(),
        'model_loaded': _model is not None,
    }), 200


@app.route('/warmup')
def warmup():
    try:
        load_labels()
        load_model_once()
        return jsonify({'status': 'warmed_up'}), 200
    except Exception as exc:
        return jsonify({'status': 'error', 'error': str(exc)}), 500


@app.route('/predict', methods=['POST'])
def predict():
    try:
        img = None

        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            img = Image.open(file.stream)
        elif request.form.get('url'):
            image_url = request.form['url'].strip()
            if not image_url.lower().startswith(('http://', 'https://')):
                return jsonify({'error': 'Image URL must start with http:// or https://'}), 400
            response = requests.get(image_url, timeout=REQUEST_TIMEOUT_SECONDS)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
        else:
            return jsonify({'error': 'No image provided'}), 400

        if img.mode != 'RGB':
            img = img.convert('RGB')

        breed, confidence, top_predictions = predict_breed(img)
        img_str = image_to_base64(img)

        return jsonify({
            'breed': breed,
            'confidence': confidence,
            'top_predictions': top_predictions,
            'image': img_str,
        })
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/random_dog')
def random_dog():
    try:
        response = requests.get('https://dog.ceo/api/breeds/image/random', timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        return jsonify({'url': response.json()['message']})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
