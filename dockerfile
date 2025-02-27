FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    #compilation tools
    gcc \
    python3-dev \
    #libraries to compile pyaudio on linux
    portaudio19-dev \
    libglib2.0-0 \
    #libraries for headless chrome
    gnupg wget ca-certificates \
    curl unzip \
    libnss3 libx11-xcb1 libxcomposite1 libxcursor1 \
    libxdamage1 libxi6 libxtst6 libappindicator3-1 \
    libasound2 libatk1.0-0 libgtk-3-0 \
    xdg-utils fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Install google chrome
RUN wget -4 -qO- https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/google-chrome-keyring.gpg \
    && echo 'deb [signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main' | tee /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable

# Copy the source files to the root directory
COPY . /app

# Install python requirements
RUN pip install --no-cache-dir -r requirements.txt

# Add the accessory files volume to python's path, so source files can import them
ENV PYTHONPATH=/app/config_files:$PYTHONPATH

# Command to start the container and the main source which will remain in the loop
CMD ["python", "main.py"]