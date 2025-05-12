FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    #compilation tools
    gcc \
    python3-dev \
    #libraries to compile pyaudio on linux
    portaudio19-dev \
    libglib2.0-0 \
    libmodplug1

# Copy the source files to the root directory
COPY . /app

# Install python requirements
RUN pip install --no-cache-dir -r requirements.txt

# Add the accessory files volume to python's path, so source files can import them
ENV PYTHONPATH=/app/config_files:$PYTHONPATH

# Command to start the container and the main source which will remain in the loop
CMD ["python", "main.py"]