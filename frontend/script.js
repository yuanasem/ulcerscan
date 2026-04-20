document.addEventListener('DOMContentLoaded', () => {
    // Navigasi Tab
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(btn.getAttribute('data-target')).classList.add('active');
        });
    });

    // Variabel Elemen
    const fileInput = document.getElementById('file-input');
    const dropZone = document.getElementById('drop-zone');
    const btnAnalyze = document.getElementById('btn-analyze');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const uploadPrompt = document.getElementById('upload-prompt');
    const resultCard = document.getElementById('result-card');
    const emptyState = document.getElementById('empty-state');

    let selectedFile = null;

    // Trigger Upload
    dropZone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', e => {
        if (e.target.files.length > 0) handleFile(e.target.files[0]);
    });

    // Drag & Drop
    dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragover'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', e => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
    });

    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('Harap masukkan file gambar (JPG/PNG)');
            return;
        }
        selectedFile = file;
        const reader = new FileReader();
        reader.onload = e => {
            imagePreview.src = e.target.result;
            uploadPrompt.style.display = 'none';
            previewContainer.style.display = 'block';
            btnAnalyze.removeAttribute('disabled');
            // Reset UI Hasil
            resultCard.style.display = 'none';
            emptyState.style.display = 'flex';
        };
        reader.readAsDataURL(file);
    }

    // Koneksi ke Backend Production
    btnAnalyze.addEventListener('click', async () => {
        if (!selectedFile) return;

        // UI Loading State
        const originalBtnText = btnAnalyze.innerHTML;
        btnAnalyze.innerHTML = '<i class="fa-solid fa-circle-notch spin"></i> Menganalisis...';
        btnAnalyze.disabled = true;

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            // Ganti URL sesuai endpoint backend production kamu
            const response = await fetch('/api/predict', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Gagal menghubungi server');

            const data = await response.json();

            // Mapping Data dari API ke UI Terbaru
            document.getElementById('res-type').textContent = data.class_name || 'Tidak Terdeteksi';
            document.getElementById('res-severity').textContent = data.severity || 'Normal';
            document.getElementById('res-confidence').textContent = `${(data.confidence * 100).toFixed(1)}% Akurat`;
            document.getElementById('res-recommendation').textContent = data.recommendation || 'Tetap jaga kebersihan mulut.';
            document.getElementById('res-date').textContent = new Date().toLocaleTimeString();

            // Tampilkan Hasil
            emptyState.style.display = 'none';
            resultCard.style.display = 'block';

        } catch (error) {
            console.error(error);
            alert('Terjadi kesalahan saat analisis: ' + error.message);
        } finally {
            btnAnalyze.innerHTML = originalBtnText;
            btnAnalyze.disabled = false;
        }
    });
});