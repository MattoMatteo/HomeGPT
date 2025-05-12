import time
import speech_recognition as sr
import pyaudio

import system

from collections import defaultdict
import yaml

#------------- Mic & Recognizer ----------------
path_SrLanguages = "config_files/SrLanguages.yaml"

class MicManager():

    def init(self)->bool:
        self.devices_list = self.get_micDeviceList()
        self.defaultDeviceInfo = self.get_defaultMicDeviceInfo()
        if len(self.devices_list) == 0:
            system.write_log("No mic devices found in system.")
            return False
        system.write_log("These are the available microphones:")
        system.write_log(", ".join(d["name"] for d in self.devices_list).strip(", "))

        self.recognitionLanguage = "en-gb" #Standard
        return True

    def init_mic(self, micName:str):
        if micName == None:
            return None
        #1. Get index
        self.deviceIndex= self.get_deviceIndex(micName)

        #2. Logs
        log_message = ""
        new_mic_name = ""
        if self.deviceIndex == False: #Not found
            log_message = "No '{old_mic_name}' mic found."
            self.deviceIndex = None

        if self.deviceIndex == None: #Default set.
            new_mic_name = self.defaultDeviceInfo["name"]
            log_message = "Default mic has ben set: '{new_mic_name}'"
            self.deviceIndex = self.defaultDeviceInfo["index"]
        else:   #Found
            new_mic_name = micName
            log_message = "'{old_mic_name}' mic device found.".capitalize()

        context = defaultdict(str, {
        "new_mic_name": new_mic_name,
        "old_mic_name": micName,
        })
        system.write_log(log_message.format_map(context)[0].upper()+log_message.format_map(context)[1:])
        return self.start_listen(device_index = self.deviceIndex)

    def set_recognitionLanguage(self, recognition_languge:str)->str:
        with open(path_SrLanguages, "r", encoding="utf-8") as file:
            SrLanguages:dict = yaml.safe_load(file)["RecognitionLanguageCode"]

        if not recognition_languge in SrLanguages.values():
            system.write_log(f"No '{recognition_languge}' language found for recognition: 'en-gb' will be set by default.")
            self.recognitionLanguage = "en-gb"
        self.recognitionLanguage = recognition_languge
        return self.recognitionLanguage

    def get_defaultMicDeviceInfo(self):
        audio = pyaudio.PyAudio()
        mic_info = audio.get_default_input_device_info()
        audio.terminate()
        return mic_info

    def isDeviceActive(self):
        if not self.deviceIndex == False:
            return True
        return False

    def get_micDeviceList(self)->list[int]:
        audio = pyaudio.PyAudio()
        devices_list = []
        for i in range(audio.get_device_count()):
            device_info = audio.get_device_info_by_index(i)
            if device_info["maxInputChannels"]>0:
                devices_list.append(device_info)
        audio.terminate()
        return devices_list

    def get_deviceIndex(self, deviceName:str):
        device_index = False

        audio = pyaudio.PyAudio()
        for device_info in self.devices_list:
            if deviceName == device_info["name"] and device_info["hostApi"]==0:     #hostapi = 0 NON SO PERCHE'
                device_index = device_info["index"]
                #DA SISTEMARE IL FATTO DEGLI OMONIMI. PER ORA TENGO SOLO IL PRIMO RISULTATO
            
        if deviceName == "default":
            if audio.get_device_count()>0:
                device_index = None                
            
        audio.terminate()
        return device_index

    def start_listen(self, device_index:int):
        recognizer = sr.Recognizer()
        audio_source = sr.Microphone(device_index=device_index)
        with audio_source as s:
            recognizer.adjust_for_ambient_noise(source=s)

        stopper = recognizer.listen_in_background(source=audio_source,callback=speech_to_text)
        time.sleep(0.1)
        return stopper
    
micManager = MicManager()

#Thread functions

def speech_to_text(recognizer:sr.Recognizer, audio:sr.AudioData):
    """
    Callback of thread that listen in background a mic.
    The audio data will be processed through the speech to text function to give the answer 
    """
    system.write_log("Listening...\n")
    log_message = ""
    response = ""
    try:
        response:str = recognizer.recognize_google(audio, language=micManager.recognitionLanguage)
        log_message = "You said: {response}"
    except sr.UnknownValueError:
        log_message = "I didn't understand what you said."
    except sr.RequestError as e:
        log_message = f"Service error: {e}"

    context = defaultdict(str, {
        "response": response,
    })
    system.write_log(log_message.format_map(context))

    if response != "":
        if response.lower().startswith(tuple(system.conf.config["activation_words"])):
            system.develops_and_response(response)