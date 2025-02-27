# MQTT Voice Assistant

## 📌 Overview
MQTT Voice Assistant is an intelligent voice control system that integrates MQTT communication with ChatGPT. It allows users to interact via voice input (microphone) or MQTT messages, and receive responses via speakers or MQTT output.

The system captures voice input, converts it into text via Google's speech recognition API, and sends it to ChatGPT via a third-party site (chatgpt.it).
The response is then played via internal speakers or sent via MQTT for smart home integration.

## 🚀 Features
- 🎙️ **Speech recognition**: Converts spoken words into text via Google's API.
- 🔗 **MQTT integration**: Sends and receives messages to/from MQTT topics.
- 💬 **ChatGPT Interaction**: Uses Selenium to retrieve responses from chatgpt.it.
- 🔊 **Flexible Output**: Plays responses through internal speakers or devices connected via MQTT.
- 🏡 **Smart Home Ready**: Easily integrates into home automation solutions.

## ⚠️ Known Issues
Using Selenium to query and extract data slows down the overall process (compared to using the APIs directly, which are paid for based on the number of tokens). This, combined with a small delay in transmitting and receiving MQTT signals, results in an average wait time of about 10 seconds, with rare cases reaching up to 15 seconds.

## 🔧 Installation via Docker and Docker Compose
Make sure to have Docker and Docker Compose installed on your system.
Building the Image Locally
To build and run the project using Docker, you can build the image directly from the provided Dockerfile. This approach does not require a pre-built image:

1. Create a folder:
```bash
mkdir HomeGPT
cd HomeGPT
```
2. Clone the repository:
```bash
git clone https://github.com/your-user/mqtt-voice-assistant.git
cd mqtt-voice-assistant
```
3. Modify the configuration file (`/config_files/config.yaml`) and docker-compose.yml:
```yaml
#Input mic device
        #1. Set to null if you dont wanna use internal mic but just another device that comunicate with MQTT
        #2. "default" to automaticaly select a default mic input
        #3. The name of mic. If the mic will not found, the default will be used.
                #If no one device will be find, check the log for the names list of devices available
mic_name: None    

recognition_language: "it-it" #It uses Google APIs. For simplicity I have added a code list for the various languages in SrLanguages.ywaml: RecognitionLanguageCode.

activation_words: # a list of words that trigger speech recognition
  - "hey google"
  - "alexa"   

#output internal device
        #Device Name:
        #1. Set to null if you dont wanna use internal audio output device but just another device that comunicate with MQTT
        #2. "default" to automaticaly select a default audio output device
        #3. The name of audio output device. If the audio output device will not found, the default will be used.
                #If no one device will be find, check the log for the names list of devices available
out_device_name: null

        #Language code:
        #1. It uses gtts (Google text to speech), so you can search your language code.
        #2. If an invalid code will be insert, "en" will be set by default. For simplicity I have added a code list for the various languages in SrLanguages.yaml: OutLanguageCode.
out_language: "it"

mqtt:    
  mqtt_host: "" #set ip or hostname: example "192.168.1.1" 
  mqtt_username: ""
  matt_password: ""
  mqtt_port: 1883
  mqtt_topic_subscription: "HomeGPT/listen" #topic listening FROM broker
  mqtt_topic_publication: "HomeGPT/respond" #publication topic TO THE broker
```
For language codes, refer to the `SrLanguages.yaml` file which contains list of different languages.

Modify the docker-compose.yml file to suit your system. Here is an example configuration:
```yml
version: '3.8'

services:
  homegpt:
    build: ./ 
    image: "homegpt_image"
    restart: unless-stopped
    container_name: homegpt
    volumes:
      - ./config_files:/app/config_files  # Mounts configuration files for persistence
    devices:
      - "/dev/snd:/dev/snd"  
      - "/dev/ttyUSB0:/dev/ttyUSB0"  # Check available devices with 'ls /dev/ttyUSB*'
```
The host's ALSA sound device (/dev/snd) is mapped inside the container. Ensure your system uses ALSA; otherwise, adjust accordingly
The actual device path may vary depending on your system and connected hardware
Note: You can place the docker-compose.yml file wherever you want, as long as it references the correct paths (e.g., ./config_files for the configuration files). The docker-compose command will pick it up as long as you are in the directory where the file is located.

4. Build the Docker image:
```bash
docker-compose build 
```
5. Start the container:
```bash
docker-compose up -d
```
This will build the image from the provided Dockerfile and start the container.

## 🤖 Future Improvements
- Use a chatgpt.com account and other LLMs and their APIs for those who wish.
- Ability to send customized MQTT messages for smart home management without consulting ChatGPT.
- Modifiers to set after the message.
- Chat mode (currently, you get a single reply without tracking the conversation history).
- **User-selectable APIs**: Allow users to switch between different speech recognition and text-to-speech APIs, including local models, for those who prefer not to rely on third-party services.

Feel free to contribute! 🎉
