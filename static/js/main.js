document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadForm = document.getElementById('upload-form');
    const fileList = document.getElementById('file-list');
    const convertBtn = document.getElementById('convert-btn');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');

    if (!dropZone) return;

    // Trigger de la boîte de sélection native
    dropZone.addEventListener('click', () => fileInput.click());

    // Drag over effect
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    ['dragleave', 'drop'].forEach(event => {
        dropZone.addEventListener(event, () => dropZone.classList.remove('drag-over'));
    });

    // Capture des fichiers déposés
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        if (e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
            updateFileList();
        }
    });

    // Changement d'état de l'input natif
    fileInput.addEventListener('change', updateFileList);

    function updateFileList() {
        const files = fileInput.files;
        if (files.length === 0) {
            fileList.style.display = 'none';
            convertBtn.disabled = true;
            return;
        }
        
        fileList.innerHTML = '<strong>Fichier(s) sélectionné(s) :</strong><br>';
        for (let i = 0; i < files.length; i++) {
            fileList.innerHTML += `• ${files[i].name} (${(files[i].size / 1024 / 1024).toFixed(2)} Mo)<br>`;
        }
        fileList.style.display = 'block';
        convertBtn.disabled = false;
    }

    // Gestion de la soumission asynchrone AJAX via Fetch API
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const files = fileInput.files;
        if (files.length === 0) return;

        const formData = new FormData();
        // Gestion des téléversements multiples (images ou fusions multiples)
        for (let i = 0; i < files.length; i++) {
            formData.append('file', files[i]);
        }

        convertBtn.disabled = true;
        progressContainer.style.display = 'block';
        progressBar.style.width = '20%';
        progressText.innerText = 'Téléversement et conversion en cours... Ne fermez pas la page.';

        const endpoint = uploadForm.getAttribute('action');

        try {
            // Utilisation de XHR pour tracker l'évolution du traitement (progress simulation)
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errText = await response.text();
                throw new Error(errText || 'Une erreur système est survenue lors du traitement.');
            }

            progressBar.style.width = '100%';
            progressText.innerText = 'Traitement réussi ! Téléchargement imminent.';

            // Capture de la réponse binaire en Blob
            const blob = await response.blob();
            
            // Extraction du nom de fichier depuis les en-têtes de réponse ou fallback
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = "document_converti";
            if (contentDisposition && contentDisposition.includes('filename=')) {
                filename = contentDisposition.split('filename=')[1].replaceAll('"', '');
            } else {
                // Tentative de déduction de l'extension
                if (endpoint.includes('to-word')) filename += ".docx";
                else if (endpoint.includes('to-jpg') || endpoint.includes('split')) filename += ".zip";
                else if (endpoint.includes('to-excel')) filename += ".xlsx";
                else filename += ".pdf";
            }

            // Technique de l'ancre virtuelle pour forcer la boîte de dialogue de téléchargement du navigateur
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            
            // Nettoyage de la mémoire du DOM
            window.URL.revokeObjectURL(url);
            a.remove();

            setTimeout(() => {
                progressContainer.style.display = 'none';
                convertBtn.disabled = false;
                uploadForm.reset();
                fileList.style.display = 'none';
            }, 3000);

        } catch (error) {
            console.error(error);
            progressBar.style.width = '0%';
            progressText.innerHTML = `<span style="color:#ff6b6b;">${error.message}</span>`;
            convertBtn.disabled = false;
        }
    });
});