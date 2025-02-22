import time
import os

#Mic and speech_recognition
import speech_recognition as sr
import pyaudio

#Internal audio output
from gtts import gTTS, langs
import io
import pygame.mixer
import pygame._sdl2.audio as sdl2_audio


#chrome for estract by https://chatgpt.it response
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

#mqtt for comunication between software and broker to send response and if dont wanna use integrated mic
import paho.mqtt.client as mqtt
from paho.mqtt.enums import MQTTErrorCode

import yaml
#----------- MQQT --------------

mqtt_client = mqtt.Client()
mqtt_mode = False

def on_connect(client, userdata, flags, rc):
    client.subscribe(config["mqtt"]["mqtt_topic_subscription"])

def on_message(client, userdata, msg):
    global use_internal_audio_output
    message = str(msg.payload.decode())
    topic = str(msg.topic)
    write_log(f"Message received: {message} on topic {topic}")

    response = ask_to_chatgpt(message)

    publish_response(client,response)
    if use_internal_audio_output:
        start_text_to_speech(response)

def publish_response(client:mqtt.Client, response:str):
    client.publish(config["mqtt"]["mqtt_topic_publication"], response)

def init_mqtt_client()->bool:
    global mqtt_client
    global mqtt_mode
    mqtt_client.username_pw_set(config["mqtt"]["mqtt_username"],config["mqtt"]["mqtt_password"])
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    try:
        error_code = int(mqtt_client.connect(config["mqtt"]["mqtt_host"],config["mqtt"]["mqtt_port"],60))
    except Exception as error_code:
        write_log(f"Unable to connect to broker. Check hostname/ip and port. Error: {error_code}")
        return False
    
    mqtt_client.loop_start()
    return True

#------------- Mic & Recognizer ----------------

stop_flag = False
device_index = -1
use_internal_mic = False

def init_mic()->bool:
    global device_index
    global use_internal_mic

    if not config["recognition_language"] in SrLanguages["RecognitionLanguageCode"].values():
        write_log(f"No '{config['recognition_language']}' language found for recognition: 'en-gb' will be set by default.")
        config["recognition_language"] = "en-gb"

    #Check Mic device
    audio = pyaudio.PyAudio()
    devices_list = set()
    for i in range(audio.get_device_count()):
        device_info = audio.get_device_info_by_index(i)
        if device_info["maxOutputChannels"]>0:
            devices_list.add(device_info["name"])
        if device_info["name"] == config["mic_name"]:
            device_index = i
    audio.terminate()

    if device_index!=-1:
        write_log("Mic device found.")
        return True
    elif config["mic_name"] == "default":
        device_index = None
        return True
    else:
        write_log(f"No '{config['mic_name']}' mic device found. That is the devices list:")
        write_log(", ".join(devices_list).strip(", "))
        return False

def start_listen():
    global device_index
    microphone = sr.Microphone(device_index=device_index)   
    recognizer = sr.Recognizer()
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source=source)

    return recognizer.listen_in_background(source=microphone,callback=thread_listen)

def speech_to_text(recognizer:sr.Recognizer, audio:sr.AudioData)->str:
    try:
        text = recognizer.recognize_google(audio, language=config["recognition_language"])
        return f"You said: {text}"
    except sr.UnknownValueError:
        return "I didn't understand what you said."
    except sr.RequestError as e:
        return f"Service error: {e}"
        
def thread_listen(recognizer:sr.Recognizer, audio:sr.AudioData):
    global stop_flag
    global mqtt_mode
    global use_internal_audio_output

    write_log("Listening...\n")
    text = speech_to_text(recognizer=recognizer, audio=audio)
    response = ""
    write_log(text)
    if text != "I didn't understand what you said.":
        text = text[len("You said: "):]
        if text.lower().startswith(config["activation_words"]):
            response = ask_to_chatgpt(request=text)
            if mqtt_mode:
                MQTT_error_code = mqtt_client.publish(config["mqtt_topic_publication"],response)
                if MQTT_error_code.rc == MQTTErrorCode.MQTT_ERR_NO_CONN:
                    write_log("Unable to publish MQTT message to broker. Please check your username and password.")
            if use_internal_audio_output:
                start_text_to_speech(response)

#-------------- Audio Output -------------------

use_internal_audio_output = False

def init_internal_output_audio()->bool:

    #set device
    if config["out_device_name"] == None:
        return False
    pygame.mixer.init()
    devices = tuple(sdl2_audio.get_audio_device_names(False))
    if len(devices)==0:
        write_log("No output audio device found in your system.")
        return False
    if config["out_device_name"] == "default":
        config["out_device_name"] = None
    else:
        if not any(device == config["out_device_name"] for device in devices):
            write_log(f"No output audio device found with name: '{config['out_device_name']}'. Default will be set.")
            write_log("This is the list of output audio device available:")
            write_log(", ".join(devices).strip(", "))
            config["out_device_name"] = "default"
            config["out_device_name"] = None
    pygame.mixer.quit()
    
    #set language 
    if config["out_language"] == "default":
        config["out_language"] = "en"
        return True
    
    langs_dic = langs._main_langs()
    found = False
    for k,v in langs_dic.items():
        if k == config["out_language"] or v == config["out_language"]:
            config["out_language"] = k
            found = True
    if not found:
        write_log(f"No '{config['out_language']}' language found for the output audio device: 'en' will be set by default")
        config["out_language"] = "en"

    return True

def start_text_to_speech(text:str):
    tts = gTTS(text,lang=config["out_language"])
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    pygame.mixer.init(devicename=config["out_device_name"])
    pygame.mixer.music.load(audio_fp, "mp3")
    pygame.mixer.music.play()

def stop_text_to_speech():
    pygame.mixer.music.stop()

def audio_playing()->bool:
    return pygame.mixer.music.get_busy()

def wait_playback_end():
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

#--------------------- LLM ----------------------
def ask_to_chatgpt(request:str)->str:

    #Set options of chrome
    opzioni_chrome = Options()
    opzioni_chrome.add_argument("headless")
    prefs = {
    "download.default_directory": os.getcwd(),  # Modifica con il tuo percorso
    "download.prompt_for_download": False,  # Evita la richiesta di conferma del download
    "directory_upgrade": True,  # Permette il salvataggio automatico nella cartella impostata
    "safebrowsing.enabled": True  # Disabilita il controllo SafeBrowsing per evitare blocchi sui file scaricati
    }
    opzioni_chrome.add_experimental_option("prefs",prefs)
    driver = webdriver.Chrome(options=opzioni_chrome)
    #Start driver and act on site
    driver.get("https://chatgpt.it")
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[placeholder="Scrivi un messaggio"]'))).send_keys(request)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[class="wpaicg-chat-shortcode-send"]'))).click()
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//span[@class="wpaicg-chat-message"][@id]'))) #wait for message (max 20sec)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[class="wpaicg-chatbox-download-btn"]'))).click()
    #check if file is complete before quit driver
    timeout = 60
    end_time = time.time() + timeout
    downloaded = False
    while time.time() < end_time and downloaded==False:
        files = os.listdir(os.getcwd())
        if any(file == "chat.txt" for file in files):
            downloaded = True
        else:
            time.sleep(0.1)
    driver.quit()
    #estract the response from file.txt end erase it
    path_chat = "chat.txt"
    response = ""
    with open(path_chat,"r",encoding='utf-8') as f:
        lines = []
        lines = f.readlines()
        for i, line in enumerate(lines):
            if i != 0 and line.strip("\n").lower() != request.lower():
                response = response + line
    os.remove(path_chat)
    write_log(response)
    #return the response
    return response

#--------------------- System -------------------
config = {}
path_config_yaml = "config_files/config.yaml"
SrLanguages = {}
path_SrLanguages = "config_files/SrLanguages.yaml"

def init_system():
    global config
    global SrLanguages
    list_file = os.listdir(os.getcwd())
    if any("log.txt"==file for file in list_file):
        os.remove("log.txt")
    with open(path_config_yaml, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    with open(path_SrLanguages, "r", encoding="utf-8") as file:
        SrLanguages = yaml.safe_load(file)
def print_service_status():
    global use_internal_mic
    global mqtt_mode
    global use_internal_audio_output

    if use_internal_mic:
        write_log("Internal mic mode ON")
    else:
        write_log("Internal mic mode OFF")
    if use_internal_audio_output:
        write_log("Internal audio output mode ON")
    else:
        write_log("Internal audio output mode OFF")
    if mqtt_mode:
        write_log("MQTT mode ON")
    else:
        write_log("MQTT mode OFF")
def write_log(message:str):
    path = os.getcwd()+"/config_files/log.txt"
    if os.path.exists(path):
        mode = "a"
    else:
        mode = "w"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(path,"a") as f:
        f.write(f"\n{timestamp} {message}")    
    print(f"\n{timestamp} {message}")

#--------------------- Main ----------------------
def main():

    global stop_flag

    global use_internal_mic
    global mqtt_mode
    global use_internal_audio_output

    init_system()
    mqtt_mode = init_mqtt_client()
    use_internal_mic = init_mic()
    if use_internal_mic:
        stop_listening = start_listen()

    use_internal_audio_output = init_internal_output_audio()

    print_service_status()

    while mqtt_mode or use_internal_mic:
        time.sleep(0.1)

if __name__ == "__main__":
    main()