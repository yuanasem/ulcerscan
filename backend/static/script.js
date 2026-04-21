document.addEventListener('DOMContentLoaded', () => {
    // Navigasi Tab
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Hapus kelas active dari semua tombol dan semua konten
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Tambahkan kelas active ke tombol yang diklik
            btn.classList.add('active');
            
            // Ambil target ID dari data-target (misal: tab-edukasi)
            const targetId = btn.getAttribute('data-target');
            const targetContent = document.getElementById(targetId);
            
            // Tampilkan konten yang sesuai
            if (targetContent) {
                targetContent.classList.add('active');
            }
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

    // Koneksi ke Backend Production (update URL sesuai dengan deployment)
btnAnalyze.addEventListener('click', async () => {
    const formData = new FormData();
    const file = selectedFile; // Pastikan file yang dipilih sudah disimpan di variabel selectedFile
    
    // PERUBAHAN 1: Pakai 'image' sesuai request.files['image'] di Python
    formData.append('image', file); 

    btnAnalyze.innerHTML = '<i class="fa-solid fa-spinner spin"></i> Menganalisis...';
    btnAnalyze.setAttribute('disabled', 'true');

    try {
        // PERUBAHAN 2: Sesuaikan path URL dengan /api/predict
        const response = await fetch('https://ulcerscan-production.up.railway.app/api/predict', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Gagal menganalisis');
        }

        const data = await response.json();

        // Update UI dengan hasil dari server
        document.getElementById('res-type').innerText = data.type;
        document.getElementById('res-severity').innerText = data.severity;
        document.getElementById('res-recommendation').innerText = data.recommendation;
        // Tambahkan ini di bawah update res-recommendation
        if (data.confidence) {
            document.getElementById('res-confidence').innerText = data.confidence + '% Akurat';
}
        
        emptyState.style.display = 'none';
        resultCard.style.display = 'flex';

    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        btnAnalyze.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Analisis Sariawan';
        btnAnalyze.removeAttribute('disabled');
    }
});});