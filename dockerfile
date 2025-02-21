# Usa l'immagine di base di Python
FROM python:3.11-slim

# Imposta la directory di lavoro
WORKDIR /app

# Copia il file requirements.txt e installa le dipendenze
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia direttamente i file di configurazione nel container
COPY config.py /app/config.py
COPY SrLanguages.py /app/SrLanguages.py

# Copia il codice sorgente locale (main.py, etc.)
COPY . /app

# Aggiungi la directory di configurazione al PYTHONPATH
ENV PYTHONPATH=/app/config_files:$PYTHONPATH

# Imposta il volume per i file di configurazione (facoltativo)
VOLUME /app/config_files

# Comando di avvio del container (comandi da eseguire quando parte il container)
CMD ["python", "main.py"]