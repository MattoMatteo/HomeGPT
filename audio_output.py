"""
Module that handles audio outputs.
Mainly composed of a class that takes care of:
- initializing the correct output
- transforming the response text into audio
- and playing it.
"""
import io
from collections import defaultdict

import pyaudio
from pygame import mixer as pygame_mixer, error as pygame_error # pylint: disable=no-name-in-module
import pygame._sdl2.audio as _sdl2_audio
from gtts import gTTS, lang

from system import write_log

class AudioOutputManager():
    """
    Class that takes care of initializing the correct output
    and transforming the response text into audio and playing it.
    """
    def __init__(self, device_name:str, speech_language:str):

        #First let's check the conditions to initialize the device
        if device_name is None:
            self._device_active = False
            return

        try:
            pygame_mixer.init()
        except pygame_error as e:
            write_log("Can't initialize audio output. Pygame mixer problem.")
            write_log(e)
            self._device_active = False
            return

        self.devices_list = tuple(_sdl2_audio.get_audio_device_names(False)) # pylint: disable=c-extension-no-member
        if len(self.devices_list) == 0:
            write_log("No out audio devices found in system.")
            self._device_active = False
            return

        write_log("This is the list of output audio device available:")
        write_log(", ".join(name for name in self.devices_list).strip(", "))

        #Get device name(Pygame will use device name not index).
        self.default_audio_device_info = self.get_default_out_audio_device_info()
        log_message = ""

        self.device_name = False
        for d_n in self.devices_list:
            if d_n ==  device_name:
                self.device_name = device_name
                log_message = "'{old_device_name}' output device found.".capitalize()

        if self.device_name is False:
            if device_name == "default":
                log_message = "Default audio output has ben set: '{new_device_name}'"
            else:
                log_message = ("No '{old_device_name}' output device found."
                "Default audio output has ben set: '{new_device_name}")
            self.device_name = self.default_audio_device_info["name"]

        context = defaultdict(str, {
        "new_device_name": self.device_name,
        "old_device_name": device_name,
        })
        write_log(
            log_message.format_map(context)[0].upper() +
            log_message.format_map(context)[1:]
        )
        self._device_active = True
        self.set_speech_language_code(speech_language)

    def get_default_out_audio_device_info(self):
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
        default_out = audio.get_default_output_device_info()
        audio.terminate()
        return default_out

    def is_device_active(self) -> bool:
        """
        Returns true if the device could be initialized. 
        """
        return self._device_active

    def set_speech_language_code(self, language:str):
        """
        Try to set given speech language. If not found en will be set by default.
        """
        langs_dic = lang.tts_langs()
        for k,v in langs_dic.items():
            if language in (k, v):
                self.speech_language = k
                write_log(f"{self.device_name} speech language set to {self.speech_language}")
                return

        self.speech_language = "en"
        if language == "default":
            write_log(f"{self.device_name} speech language set to 'en'")
        else:
            write_log(
                f"No '{language}' language found for {self.device_name} device, "
                "'en' will be set by default"
            )

    def audio_reproduce(self, audio:io.BytesIO)->bool:
        """
        Function that plays an audio file (mp3 text to speech)
        in the audio output initialized by the class.
        """
        pygame_mixer.init(devicename=self.device_name)
        pygame_mixer.music.load(audio, "mp3")
        pygame_mixer.music.play()
        return True

def text_to_speech(text:str, speech_language:str) -> io.BytesIO:
    """
    Method that converts the text (received in response) into an mp3
    thanks to Google's text-to-speech library.
    """
    tts = gTTS(text=text, lang=speech_language)
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    return audio_fp

def callback_for_pipeline(message:str):
    """
    Callback function for publishing output to the output audio devices,
    based on user settings and active devices.
    """
    audio_dict = {}
    for device in audio_output_list:
        if device.is_device_active():
            if device.speech_language not in audio_dict:
                audio_dict[device.speech_language] = text_to_speech(
                                                    message, device.speech_language)

    for device in audio_output_list:
        if device.is_device_active():
            device.audio_reproduce(audio_dict[device.speech_language])

audio_output_list: list[AudioOutputManager] = []
