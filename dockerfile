# Usa l'immagine di base di Python
FROM python:3.11-slim

# Imposta la directory di lavoro
WORKDIR /app

# Installa strumenti di compilazione
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    portaudio19-dev \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copia il file requirements.txt e installa le dipendenze
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia direttamente i file di configurazione nel container
COPY config_files/config.yaml /app/config_files/config.yaml
COPY config_files/SrLanguages.yaml /app/config_files/SrLanguages.yaml

# Copia il codice sorgente locale (main.py, etc.)
COPY . /app

# Aggiungi la directory di configurazione al PYTHONPATH
ENV PYTHONPATH=/app/config_files:$PYTHONPATH

# Imposta il volume per i file di configurazione (facoltativo)
VOLUME /app/config_files

# Comando di avvio del container (comandi da eseguire quando parte il container)
CMD ["python", "main.py"]