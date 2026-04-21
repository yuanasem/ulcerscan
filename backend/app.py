from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import tensorflow as tf
import numpy as np
import cv2
import os
import uuid
from datetime import datetime

# Mengatasi masalah distutils di beberapa versi Python/setuptools
try:
    import setuptools
    import sys
    sys.modules['distutils'] = setuptools._distutils
except ImportError:
    pass

app = Flask(__name__)
# Enable CORS agar frontend (index.html) bisa memanggil backend di Railway
CORS(app) 

# ===== KONFIGURASI =====
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Maksimal 16MB

# ===== LOAD MODEL =====
# Pastikan file 'best_model.h5' berada di folder yang sama dengan app.py
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
        "recommendations": "Gunakan obat kumur antiseptik 2x sehari, oleskan gel triamcinolone acetonide, hindari makanan pedas, dan konsumsi vitamin B12/zinc.",
        "need_doctor": False
    },
    "MAJOR RAS": {
        "severity": "Berat",
        "recommendations": "⚠️ Segera konsultasi ke dokter gigi spesialis. Diperlukan kortikosteroid topikal kuat dan hindari trauma mekanis pada area luka.",
        "need_doctor": True
    },
    "HERPETIFORM ULCERATION": {
        "severity": "Sedang",
        "recommendations": "Gunakan obat antiviral sesuai resep, kompres dingin untuk mengurangi nyeri, dan jaga kebersihan mulut dengan sikat gigi lembut.",
        "need_doctor": True
    },
    "Traumatic Ulcer": {
        "severity": "Ringan",
        "recommendations": "Identifikasi penyebab trauma (seperti kawat gigi atau tergigit), gunakan obat kumur chlorhexidine, dan oleskan gel pelindung.",
        "need_doctor": False
    },
    "OSCC": {
        "severity": "Kritis",
        "recommendations": "⚠️ SEGERA ke dokter spesialis onkologi mulut. Jangan menunda penanganan medis dan hindari merokok/alkohol.",
        "need_doctor": True
    },
    "Infectious Ulcer (TB & HMFD)": {
        "severity": "Berat",
        "recommendations": "Konsultasi dokter untuk tes infeksi. Isolasi diri untuk mencegah penularan (HMFD), perbanyak istirahat, dan monitor suhu tubuh.",
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

# ===== RUTE UTAMA (HOME) =====
# Menambahkan rute ini agar tidak muncul pesan "Not Found" saat membuka URL utama
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# Rute ini wajib ada agar file style.css dan script.js di folder 'static' bisa terbaca
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

#Bagian upload foto
# Tambahkan ini di bawah rute serve_static yang sudah ada
@app.route('/photos/<path:path>')
def serve_photos(path):
    return send_from_directory('photos', path)

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

    # Simpan file sementara dengan nama unik
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

        # Ambil rekomendasi sesuai kelas hasil prediksi
        rec_data = RECOMMENDATIONS.get(predicted_class, {})

        # Response diformat agar SAMA PERSIS dengan variabel di script.js
        result = {
            "type": predicted_class,
            "confidence": round(confidence, 2),
            "severity": rec_data.get("severity", "Tidak Diketahui"),
            "recommendation": rec_data.get("recommendations", "Konsultasikan dengan dokter."),
            "timestamp": datetime.now().isoformat()
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Hapus file sementara setelah diproses agar memori server tidak penuh
        if os.path.exists(filepath):
            os.remove(filepath)

if __name__ == '__main__':
    # Gunakan environment port dari Railway atau default ke 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)