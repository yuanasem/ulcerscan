document.addEventListener('DOMContentLoaded', () => {
    // === Tab navigation ===
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

    // === Upload image logic ===
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadPrompt = document.getElementById('upload-prompt');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const btnAnalyze = document.getElementById('btn-analyze');
    const emptyState = document.getElementById('empty-state');
    const resultCard = document.getElementById('result-card');

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragover'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', e => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) handleFileSelection(e.dataTransfer.files[0]);
    });

    fileInput.addEventListener('change', e => {
        if (e.target.files.length > 0) handleFileSelection(e.target.files[0]);
    });

    function handleFileSelection(file) {
        if (!file.type.match('image.*')) { alert('Mohon unggah file gambar'); return; }

        const reader = new FileReader();
        reader.onload = e => {
            imagePreview.src = e.target.result;
            uploadPrompt.style.display = 'none';
            previewContainer.style.display = 'block';
            btnAnalyze.removeAttribute('disabled');
            
            // Reset state hasil
            emptyState.style.display = 'flex';
            resultCard.style.display = 'none';
        };
        reader.readAsDataURL(file);
    }

    // === INTEGRASI MACHINE LEARNING (Fetch API ke Flask) ===
    btnAnalyze.addEventListener('click', async () => {
        const file = fileInput.files[0];
        if (!file) return;

        // 1. Ubah tampilan tombol jadi loading
        const originalHtml = btnAnalyze.innerHTML;
        btnAnalyze.innerHTML = '<i class="fa-solid fa-spinner spin"></i> Menganalisis Gambar...';
        btnAnalyze.setAttribute('disabled', 'true');

        // Sembunyikan hasil lama
        emptyState.style.display = 'none';
        resultCard.style.display = 'none';

        // 2. Siapkan data gambar untuk dikirim
        const formData = new FormData();
        formData.append('image', file);

        try {
            // 3. Tembak ke endpoint /api/predict di Flask
            const response = await fetch('http://127.0.0.1:5000/api/predict', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const data = await response.json();

            // 4. Masukkan data balasan dari Flask ke dalam HTML
            document.getElementById('res-type').innerText = data.predicted_class;
            document.getElementById('res-severity').innerText = data.severity;
            
            // Mengubah array rekomendasi menjadi list HTML
            let rekomendasiHtml = '<ul style="margin:0; padding-left:20px;">';
            data.recommendations.forEach(item => {
                rekomendasiHtml += `<li>${item}</li>`;
            });
            rekomendasiHtml += '</ul>';
            
            // Tambahkan peringatan jika butuh ke dokter
            if (data.need_doctor) {
                rekomendasiHtml += '<p style="color: #dc2626; font-weight: bold; margin-top: 10px;"><i class="fa-solid fa-triangle-exclamation"></i> Segera jadwalkan kunjungan ke dokter.</p>';
            }
            
            document.getElementById('res-recommendation').innerHTML = rekomendasiHtml;
            
            // Update Akurasi
            document.querySelector('.badge-success').innerText = `${data.confidence}% Akurat`;

            // Tampilkan kartu hasil
            resultCard.style.display = 'flex';

        } catch (error) {
            console.error("Error:", error);
            alert("Gagal menyambung ke server AI. Pastikan file app.py sudah di-run di terminal!");
            emptyState.style.display = 'flex'; // Munculkan kembali empty state jika gagal
        } finally {
            // 5. Kembalikan tombol ke kondisi semula
            btnAnalyze.innerHTML = originalHtml;
            btnAnalyze.removeAttribute('disabled');
        }
    });
});