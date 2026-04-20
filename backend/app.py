from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
import cv2
import os
import uuid
from datetime import datetime
import setuptools
import sys
sys.modules['distutils'] = setuptools._distutils

app = Flask(__name__)
CORS(app)  # Enable CORS untuk REST API

# ===== KONFIGURASI =====
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# ===== LOAD MODEL =====
model = tf.keras.models.load_model('best_model.h5')

CLASS_NAMES = [
    "HERPETIFORM ULCERATION",
    "Infectious Ulcer (TB & HMFD)",
    "MAJOR RAS",
    "MINOR RAS",
    "OSCC",
    "Traumatic Ulcer"
]

RECOMMENDATIONS = {
    "MINOR RAS": {
        "severity": "Ringan",
        "recommendations": [
            "Gunakan obat kumur antiseptik 2x sehari",
            "Oleskan gel triamcinolone acetonide pada area luka",
            "Hindari makanan pedas, asam, dan panas",
            "Konsumsi vitamin B12 dan zinc",
            "Biasanya sembuh dalam 7-14 hari"
        ],
        "need_doctor": False
    },
    "MAJOR RAS": {
        "severity": "Berat",
        "recommendations": [
            "Segera konsultasi ke dokter gigi/spesialis",
            "Diperlukan kortikosteroid topikal kuat",
            "Pantau apakah ada komplikasi infeksi",
            "Hindari trauma mekanis pada area luka",
            "Durasi penyembuhan 2-6 minggu"
        ],
        "need_doctor": True
    },
    "HERPETIFORM ULCERATION": {
        "severity": "Sedang",
        "recommendations": [
            "Gunakan obat antiviral sesuai resep dokter",
            "Kompres dingin untuk mengurangi nyeri",
            "Jaga kebersihan mulut dengan sikat gigi lembut",
            "Hindari kontak langsung untuk mencegah penularan",
            "Konsultasi jika lesi menyebar"
        ],
        "need_doctor": True
    },
    "Traumatic Ulcer": {
        "severity": "Ringan",
        "recommendations": [
            "Identifikasi dan hilangkan penyebab trauma",
            "Gunakan obat kumur chlorhexidine",
            "Oleskan gel pelindung mukosa",
            "Hindari menggigit atau menggesek area luka",
            "Biasanya sembuh dalam 5-10 hari"
        ],
        "need_doctor": False
    },
    "OSCC": {
        "severity": "Kritis",
        "recommendations": [
            "⚠️ SEGERA ke dokter spesialis onkologi mulut",
            "Diperlukan biopsi untuk konfirmasi diagnosis",
            "Jangan menunda penanganan medis",
            "Rekam semua gejala dan perubahan ukuran lesi",
            "Hindari merokok dan konsumsi alkohol"
        ],
        "need_doctor": True
    },
    "Infectious Ulcer (TB & HMFD)": {
        "severity": "Berat",
        "recommendations": [
            "Segera konsultasi dokter untuk tes infeksi",
            "Isolasi diri untuk mencegah penularan HMFD",
            "Minum obat antiviral/antibiotik sesuai resep",
            "Perbanyak minum air putih dan istirahat",
            "Monitor suhu tubuh secara berkala"
        ],
        "need_doctor": True
    }
}

# ===== PREPROCESSING GAMBAR =====
def preprocess_image(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, (224, 224))
    img = img / 255.0
    img = np.expand_dims(img, axis=0)
    return img

# ===== ENDPOINT: HEALTH CHECK =====
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok",
        "model_loaded": model is not None,
        "timestamp": datetime.now().isoformat()
    })

# ===== ENDPOINT: PREDIKSI =====
@app.route('/api/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({"error": "Tidak ada gambar yang diunggah"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "Nama file tidak valid"}), 400

    # Simpan file sementara
    filename = f"{uuid.uuid4()}.jpg"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        # Preprocessing & Prediksi
        img = preprocess_image(filepath)
        predictions = model.predict(img)
        predicted_class_idx = np.argmax(predictions[0])
        confidence = float(np.max(predictions[0])) * 100
        predicted_class = CLASS_NAMES[predicted_class_idx]

        # Ambil rekomendasi
        rec = RECOMMENDATIONS.get(predicted_class, {})

        # Format semua probabilitas
        all_probs = {
            CLASS_NAMES[i]: round(float(predictions[0][i]) * 100, 2)
            for i in range(len(CLASS_NAMES))
        }

        result = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "predicted_class": predicted_class,
            "confidence": round(confidence, 2),
            "severity": rec.get("severity", "Tidak Diketahui"),
            "recommendations": rec.get("recommendations", []),
            "need_doctor": rec.get("need_doctor", False),
            "all_probabilities": all_probs,
            "image_filename": filename
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Hapus file temp (opsional)
        # os.remove(filepath)
        pass

# ===== ENDPOINT: GET MODEL INFO =====
@app.route('/api/model-info', methods=['GET'])
def model_info():
    return jsonify({
        "classes": CLASS_NAMES,
        "input_shape": [224, 224, 3],
        "model_type": "CNN Sequential",
        "framework": "TensorFlow/Keras"
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)