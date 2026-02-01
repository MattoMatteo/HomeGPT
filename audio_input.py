"""
Module that manages audio inputs and therefore microphones.
"""
import time
from collections import defaultdict

import pyaudio
import speech_recognition as sr

from system import Configurations as Conf, ConfigKey, SrLanguagesKey
from system import OutputPipelineManager as Pipeline
from log_manager import setup_logger

logger = setup_logger("AUDIO_INPUT")

#------------- Mic & Recognizer ----------------
class MicManager():
    """
    Class that finds and initializes the requested microphone
    and starts the passive listening thread.
    """
    def __init__(self, mic_name:str, recognition_language:str):
        #First: check whether it is possible to initialize a microphone.
        self.devices_list = self.get_mic_device_list()
        if len(self.devices_list) == 0:
            logger.warning("No mic devices found in system.")
            self.device_active = False
            return
        if mic_name is None:
            logger.warning("No microphone will be used: 'None' has been set in config.yaml.")
            self.device_active = False
            return
        logger.info(
            f"These are the available microphones:\n"
            f"{', '.join(d["name"] for d in self.devices_list).strip(', ')}"
        )
        self.device_active = True

        #Second: set mic index
        self.default_device_info = self.get_default_mic_device_info()

        self.device_index= self.get_device_index(mic_name)

        log_message = ""
        self.mic_name = ""
        if not self.device_index:
            logger.warning(f"No '{mic_name}' mic found.")
            mic_name = "default"

        if mic_name == "default": #Default set.
            self.mic_name = self.default_device_info["name"]
            log_message = "Default mic has ben set: '{self_mic_name}'"
            self.device_index = self.default_device_info["index"]
        else:   #Found
            self.mic_name = mic_name
            log_message = "'{old_mic_name}' mic device found.".capitalize()

        context = defaultdict(str, {
        "self_mic_name": self.mic_name,
        "old_mic_name": mic_name,
        })
        format_message = log_message.format_map(context)
        if format_message:
            logger.info(format_message[0].upper() + format_message[1:])

        self.set_recognition_language(recognition_language)
        self.start_listen(device_index = self.device_index)

    def set_recognition_language(self, recognition_languge:str):
        """
        Try to set given recognition language. If not found en-gb will be set by default.
        """
        if not Conf.find_st_languages_data(SrLanguagesKey.RECOGNITION_LANGUAGE_CODE,
                                       recognition_languge) or recognition_languge == "default":
            self.recognition_language = "en-gb"
            if not recognition_languge == "default":
                logger.warning(
                    f"Recognition language for {self.mic_name} mic "
                    f"not found ('{recognition_languge}'), 'en-gb' will be set by default."
                )
        else:
            self.recognition_language = recognition_languge
        logger.info(f"Recognition language for {self.mic_name} mic "
                  f"set to: {self.recognition_language}")

    def get_default_mic_device_info(self) -> dict:
        """
        Use pyaudio for get defautl device information.
        Return a dict that have these keys:
        {
            "name": str,
            "index": int,
            "maxInputChannels": int, 
            "maxOutputChannels": int,
            ....other
        }
        """
        audio = pyaudio.PyAudio()
        mic_info = audio.get_default_input_device_info()
        audio.terminate()
        return mic_info

    def is_device_active(self):
        """
        Returns true if the device could be initialized. 
        """
        return self.device_active

    def get_mic_device_list(self)->list[int]:
        """
        Return a list of device info (refer to get_default_mic_device_info()).
        """
        audio = pyaudio.PyAudio()
        devices_list = []
        for i in range(audio.get_device_count()):
            device_info = audio.get_device_info_by_index(i)
            if device_info["maxInputChannels"]>0:
                devices_list.append(device_info)
        audio.terminate()
        return devices_list

    def get_device_index(self, device_name:str) -> int | None:
        """
        Return index of given device_name in self.devices_list.
        Return None if not found.
        """
        device_index = None

        audio = pyaudio.PyAudio()
        for device_info in self.devices_list:
            if device_name == device_info["name"] and device_info["hostApi"]==0:
                device_index = device_info["index"]
                #hostapi = 0 NON SO PERCHE'
                #DA SISTEMARE IL FATTO DEGLI OMONIMI. PER ORA TENGO SOLO IL PRIMO RISULTATO
        audio.terminate()
        return device_index

    def start_listen(self, device_index:int):
        """
        Method that takes care of starting the microphone background listening thread
        and sets the callback function to fire when something has been heard.
        Returns a "stopper" function that, when called, stops the thread.
        """
        recognizer = sr.Recognizer()
        audio_source = sr.Microphone(device_index=device_index)
        with audio_source as s:
            recognizer.adjust_for_ambient_noise(source=s)

        stopper = recognizer.listen_in_background(source=audio_source,
                                                  callback=create_callback(self))
        time.sleep(0.1)
        return stopper

def create_callback(mic: MicManager):
    """
    Creates a callback function for `recognizer.listen_in_background` that passes an
    additional parameter to `speech_to_text`.
    Example:
        stopper = recognizer.listen_in_background(source, create_callback(param))
    """
    def callback(recognizer, audio):
        speech_to_text(recognizer, audio, mic)
    return callback

def speech_to_text(recognizer:sr.Recognizer, audio:sr.AudioData, mic: MicManager):
    """
    Callback of thread that listen in background a mic.
    The audio data will be processed through the speech to text function to give the answer 
    """
    logger.info("Listening...\n")
    log_message = ""
    response = ""
    try:
        response:str = recognizer.recognize_google(audio, language=mic.recognition_language)
        log_message = "You said: {response}"
    except sr.UnknownValueError:
        log_message = "I didn't understand what you said."
    except sr.RequestError as e:
        log_message = f"Service error: {e}"

    context = defaultdict(str, {
        "response": response,
    })
    format_message = log_message.format_map(context)
    if format_message:
        logger.info(format_message)

    if response != "":
        if response.lower().startswith(tuple(Conf.get_conf_data(ConfigKey.ACTIVATION_WORDS))):
            Pipeline.run(response)

mic_list: list[MicManager] = []
