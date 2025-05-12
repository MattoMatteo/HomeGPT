import system
import pyaudio
import io
from gtts import gTTS, langs
from collections import defaultdict
import pygame.mixer
import pygame._sdl2.audio as sdl2_audio

class AudioOutputManager():

    def init(self)->bool:
        self.deviceName = False
        try:
            pygame.mixer.init()
        except Exception as e:
            system.write_log("Can't initialize audio output. Pygame.mixer problem.")
            system.write_log(e)
            return False
        self.devices_list = tuple(sdl2_audio.get_audio_device_names(False))
        if len(self.devices_list) == 0:
            system.write_log("No out audio devices found in system.")
            return False
        system.write_log("This is the list of output audio device available:")
        system.write_log(", ".join(name for name in self.devices_list).strip(", "))

        self.speechLanguage = "en"

        return True

    def init_OutDevice(self, device_name:str):
        if device_name == None:     #No wanna use out device
            return None
        
        #Get device name(Pygame will use device name not index).
        self.defaultAudioDeviceInfo = self.get_defaultOutAudioDeviceInfo()
        for d_n in self.devices_list:
            if d_n ==  device_name:
                self.deviceName = device_name
                log_message = "'{old_device_name}' output device found.".capitalize()         
        
        if self.deviceName == False or device_name == "default":
            if self.deviceName == False:
                log_message = "No '{old_device_name}' output device found. Default audio output has ben set: '{new_device_name}"
            if device_name == "default":
                log_message = "Default audio output has ben set: '{new_device_name}'"
            self.deviceName = self.defaultAudioDeviceInfo["name"]
      
        context = defaultdict(str, {
        "new_device_name": self.deviceName,
        "old_device_name": device_name,
        })
        system.write_log(log_message.format_map(context)[0].upper()+log_message.format_map(context)[1:])
 
    def get_defaultOutAudioDeviceInfo(self):
        audio = pyaudio.PyAudio()
        default_out = audio.get_default_output_device_info()
        audio.terminate()
        return default_out

    def isDeviceActive(self):
        if not self.deviceName == False:
            return True
        return False
    
    def set_speechLanguageCode(self, language:str):
        if language == "default":
            return True
        
        langs_dic = langs._main_langs()
        for k,v in langs_dic.items():
            if k == language or v == language:
                self.speechLanguage = k
                return True
        system.write_log(f"No '{language}' language found for the output audio device: 'en' will be set by default")
        return False
    
    def start_text_to_speech(self, text:str):
        tts = gTTS(text=text, lang=self.speechLanguage)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        self.audio_reproduce(audio_fp)

    def audio_reproduce(self, audio:io.BytesIO)->bool:
        pygame.mixer.init(devicename=self.deviceName)
        pygame.mixer.music.load(audio, "mp3")
        pygame.mixer.music.play()
        return True
    
audioOutputManager = AudioOutputManager()

