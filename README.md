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

## ⚙️ Configuration
Modify the `config.py` file to set up your preferences:

```python
# Input mic device
mic_name = None    # Set to "default" for auto-selection or specify device name
recognition_language = recognitionLanguageCode.ITALIAN_ITALY 
activation_words = ("hey google", "alexa")  # Trigger words for speech recognition

# Output audio device
out_device_name = None  # Set to "default" for auto-selection or specify device name
out_language = outLanguageCode.ITALIAN  # Language for TTS output

# MQTT Configuration
mqtt_host = ""  # Example: "192.168.1.1"
mqtt_username = ""
mqtt_password = ""
mqtt_port = 1883  # Default MQTT port

# MQTT Topics
mqtt_topic_subscription = "HomeGPT/listen"  # Topic for receiving input
mqtt_topic_publication = "HomeGPT/respond"  # Topic for sending output
```

For language codes, refer to the `SrLanguages.py` file which contains enums for different languages.

## 🤖 Future Improvements
- Use a chatgpt.com account and other LLMs and their APIs for those who wish.
- Ability to send customized MQTT messages for smart home management without consulting ChatGPT.
- Modifiers to set after the message.
- Chat mode (currently, you get a single reply without tracking the conversation history).
- **User-selectable APIs**: Allow users to switch between different speech recognition and text-to-speech APIs, including local models, for those who prefer not to rely on third-party services.

Feel free to contribute! 🎉
