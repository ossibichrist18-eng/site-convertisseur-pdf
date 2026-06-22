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
        
        // AJOUT DU BOUTON DE SUPPRESSION
        fileList.innerHTML += `
            <div style="margin-top: 10px; text-align: left;">
                <button type="button" id="clear-files-btn" style="background: none; border: none; color: #ff6b6b; text-decoration: underline; cursor: pointer; font-size: 13px; font-weight: bold; padding: 0;">
                    ✕ Supprimer le fichier sélectionné
                </button>
            </div>
        `;
        
        fileList.style.display = 'block';
        convertBtn.disabled = false;

        // EVENEMENT POUR VIDER LE SÉLECTEUR ET REINITIALISER
        document.getElementById('clear-files-btn').addEventListener('click', () => {
            fileInput.value = ""; // Vide la mémoire des fichiers sélectionnés
            updateFileList();    // Réactualise la boîte de dépôt (masquera le bouton)
        });
    }

    // Gestion de la soumission asynchrone AJAX via Fetch API
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // ==========================================
        // FORCE L'OUVERTURE DE VOTRE SMARTLINK ADSTERRA DANS UN NOUVEL ONGLET A CHAQUE CLIC
        window.open("https://www.effectivecpmnetwork.com/hbb8u1yif?key=09095d5d7fdb7ed03ec20d2fad1196bd", "_blank");
        // ==========================================

        const files = fileInput.files;
        if (files.length === 0) return;

        // "new FormData(uploadForm)" capture automatiquement tous les champs du formulaire 
        const formData = new FormData(uploadForm);

        // Affiche le bandeau global d'alerte s'il est configuré dans base.html
        const banner = document.getElementById('global-conversion-banner');
        if (banner) banner.style.display = 'flex';

        convertBtn.disabled = true;
        progressContainer.style.display = 'block';
        progressBar.style.width = '20%';
        progressText.innerText = 'Téléversement et conversion en cours... Ne fermez pas la page.';

        // Animation progressive de la barre de progression (elle avance d'elle-même au lieu de se bloquer)
        let currentProgress = 20;
        const progressInterval = setInterval(() => {
            if (currentProgress < 90) {
                currentProgress += (90 - currentProgress) * 0.05; // Ralentit à l'approche de 90%
                progressBar.style.width = `${currentProgress}%`;
            }
        }, 400);

        const endpoint = uploadForm.getAttribute('action');

        try {
            // Utilisation de Fetch pour envoyer la requête
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errText = await response.text();
                throw new Error(errText || 'Une erreur système est survenue lors du traitement.');
            }

            // Arrête le timer d'animation et remplit la barre à 100%
            clearInterval(progressInterval);
            progressBar.style.width = '100%';
            progressText.innerText = 'Traitement réussi ! Téléchargement imminent.';

            // Masque le bandeau de conversion
            if (banner) banner.style.display = 'none';

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
            // Arrête l'animation et masque le bandeau en cas d'erreur
            clearInterval(progressInterval);
            if (banner) banner.style.display = 'none';

            progressBar.style.width = '0%';
            progressText.innerHTML = `<span style="color:#ff6b6b;">${error.message}</span>`;
            convertBtn.disabled = false;
        }
    });
});