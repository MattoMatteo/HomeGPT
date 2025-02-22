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
RUN wget -qO- https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/google-chrome-keyring.gpg \
    && echo 'deb [signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main' | tee /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable=133.0.6943.126-1

# Install ChromeDriver
RUN google-chrome --version \
    CHROME_VERSION=$(google-chrome --version | awk '{print $3}') \
    echo "Chrome version: $CHROME_VERSION" \
    CHROMEDRIVER_VERSION="133.0.6943.126" \
    echo "Chromedriver version: $CHROMEDRIVER_VERSION" \
    wget -q "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip" -O chromedriver.zip \
    echo "Chromedriver zip downloaded" \
    ls -l chromedriver.zip \
    unzip -v chromedriver.zip \
    ls -l chromedriver \
    rm chromedriver.zip \
    chmod +x chromedriver \
    mv chromedriver /usr/local/bin/ \
    echo "Chromedriver installed"

# Install python requirements
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the accessory files into the directory which will be an accessible and editable volume
COPY config_files/config.yaml /app/config_files/config.yaml
COPY config_files/SrLanguages.yaml /app/config_files/SrLanguages.yaml

# Copy the source files to the root directory
COPY . /app

# Add the accessory files volume to python's path, so source files can import them
ENV PYTHONPATH=/app/config_files:$PYTHONPATH

# Creates the volume of accessory files
VOLUME /app/config_files

# Command to start the container and the main source which will remain in the loop
CMD ["python", "main.py"]