import os, time
import yaml

import network, audio_output, reply_manager

path_config_yaml = "./config_files/config.yaml"

class configurations():
    def __init__(self, path_config_yaml:str):
        if os.path.exists("./config_files/log.txt"):
            os.remove("./config_files/log.txt")

        with open(path_config_yaml, "r", encoding="utf-8") as file:
            self.config:dict = yaml.safe_load(file)

conf = configurations(path_config_yaml)

def write_log(message:str):
    path = os.getcwd()+"/config_files/log.txt"
    if os.path.exists(path):
        mode = "a"
    else:
        mode = "w"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(path, mode, errors="ignore") as f:
        f.write(f"\n{timestamp} {message}")    
    print(f"\n{timestamp} {message}")

def develops_and_response(message:str):
    response = reply_manager.freeGPT.ask_to_chatgpt_noAPI(message)

    if network.networkmanager.mqtt_active:
        network.networkmanager.mqtt_publish_response(response)

    if audio_output.audioOutputManager.isDeviceActive():
        audio_output.audioOutputManager.start_text_to_speech(response)
