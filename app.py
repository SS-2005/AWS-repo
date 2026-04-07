import os
from io import BytesIO
from pathlib import Path
import base64

import numpy as np
import pandas as pd
import requests
import tensorflow as tf
import tensorflow_hub as hub
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from PIL import Image, UnidentifiedImageError
from tensorflow.keras.preprocessing import image

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "full-image-set-mobilenetv2-adam.h5"
LABELS_PATH = BASE_DIR / "labels.csv"
REQUEST_TIMEOUT = 15
IMG_SIZE = 224

app = Flask(__name__)
CORS(app)

# Load model with custom objects for TensorFlow Hub layer
try:
    custom_objects = {"KerasLayer": hub.KerasLayer}
    model = tf.keras.models.load_model(MODEL_PATH, custom_objects=custom_objects)
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Load labels
try:
    labels_df = pd.read_csv(LABELS_PATH)
    unique_breeds = np.sort(labels_df.breed.unique())
    print("Labels loaded successfully")
except Exception as e:
    unique_breeds = np.array([f"breed_{i}" for i in range(120)])
    print(f"Warning: labels.csv not found or invalid. Using placeholder breed names. Details: {e}")


def preprocess_image(img: Image.Image):
    """Preprocess image for model prediction."""
    img = img.resize((IMG_SIZE, IMG_SIZE))
    img_array = image.img_to_array(img)
    img_array = tf.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0
    return img_array


def predict_breed(img: Image.Image):
    """Predict dog breed from image."""
    if model is None:
        raise RuntimeError("Model not loaded")

    processed_img = preprocess_image(img)
    predictions = model.predict(processed_img, verbose=0)

    predicted_idx = int(np.argmax(predictions[0]))
    confidence = float(np.max(predictions[0]))
    predicted_breed = unique_breeds[predicted_idx]

    top_5_indices = np.argsort(predictions[0])[-5:][::-1]
    top_predictions = [
        {
            "breed": str(unique_breeds[idx]),
            "confidence": round(float(predictions[0][idx] * 100), 2),
        }
        for idx in top_5_indices
    ]

    return str(predicted_breed), round(confidence * 100, 2), top_predictions


def open_image_from_request():
    if "file" in request.files and request.files["file"].filename:
        file = request.files["file"]
        return Image.open(file.stream)

    image_url = request.form.get("url", "").strip()
    if image_url:
        response = requests.get(image_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")
        if "image" not in content_type.lower():
            raise ValueError("Provided URL does not point to an image")
        return Image.open(BytesIO(response.content))

    raise ValueError("No image provided")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "model_loaded": model is not None,
            "labels_loaded": len(unique_breeds) > 0,
        }
    )


@app.route("/predict", methods=["POST"])
def predict():
    try:
        img = open_image_from_request()

        if img.mode != "RGB":
            img = img.convert("RGB")

        breed, confidence, top_predictions = predict_breed(img)

        buffered = BytesIO()
        preview = img.copy()
        preview.thumbnail((300, 300))
        preview.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return jsonify(
            {
                "breed": breed,
                "confidence": confidence,
                "top_predictions": top_predictions,
                "image": img_str,
            }
        )

    except (UnidentifiedImageError, ValueError) as e:
        return jsonify({"error": str(e)}), 400
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch image: {e}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/random_dog")
def random_dog():
    try:
        response = requests.get(
            "https://dog.ceo/api/breeds/image/random", timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        image_url = response.json()["message"]
        return jsonify({"url": image_url})
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch random dog image: {e}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
