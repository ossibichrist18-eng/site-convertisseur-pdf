FROM python:3.11-slim

# Installation des dépendances système (LibreOffice + Poppler pour pdf2image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-impress \
    poppler-utils \
    curl \
    && apt-get clean \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du reste du projet
COPY . .

# Port exposé par défaut
EXPOSE 8000

# Commande de démarrage avec Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "120", "app:app"]