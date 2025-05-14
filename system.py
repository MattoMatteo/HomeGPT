"""
Module that provides system objects and functions that can be used by other modules,
such as: configurations, a modified method for writing logs and, most importantly,
the pipeline class to generate the response that can be called from various input services.
"""
import os
import time
from typing import Any, Callable

from enum import Enum
import yaml

CONFIG_PATH = "./config_files/config.yaml"
SR_LANGUAGES_PATH = "config_files/SrLanguages.yaml"
LOG_PATH = "./config_files/log.txt"

def write_log(message:str):
    """
    Function for simultaneously writing a log to a file and to the terminal.
    """
    path = os.getcwd()+"/config_files/log.txt"
    if os.path.exists(path):
        mode = "a"
    else:
        mode = "w"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(path, mode, errors="ignore", encoding="utf-8") as f:
        f.write(f"\n{timestamp} {message}")
    print(f"\n{timestamp} {message}")

def clear_log() -> None:
    """
    Delete log file if it exists.
    """
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)

class SrLanguagesKey(Enum):
    """
    They represent the keys to access the corresponding attribute of SrLanguages.yaml.
    """
    RECOGNITION_LANGUAGE_CODE = "RecognitionLanguageCode"
    OUT_LANGUAGE_CODE = "OutLanguageCode"

class ConfigKey(Enum):
    """
    They represent the keys to access the corresponding attribute of config.yaml.
    """
    MIC_NAME = "mic_name"
    RECOGNITION_LANGUAGE = "recognition_language"
    ACTIVATION_WORDS = "activation_words"
    SYSTEM_PROMPT = "system_prompt"
    OUT_DEVICE_NAME = "out_device_name"
    OUT_LANGUAGE = "out_language"
    MQTT_HOST = "mqtt_host"
    MQTT_USERNAME = "mqtt_username"
    MQTT_PASSWORD = "mqtt_password"
    MQTT_PORT = "mqtt_port"
    MQTT_TOPIC_SUBSCRIPTION = "mqtt_topic_subscription"
    MQTT_TOPIC_PUBLICATION = "mqtt_topic_publication"

class Configurations():
    """
    Class that manages the import of configuration files
    and their use within the software
    """
    with open(CONFIG_PATH, "r", encoding="utf-8") as config_file:
        _data = yaml.safe_load(config_file)
    with open(SR_LANGUAGES_PATH, 'r', encoding="utf-8") as sr_file:
        _sr_data = yaml.safe_load(sr_file)

    @classmethod
    def get_conf_data(cls, key:ConfigKey) -> Any:
        """
        Method to get an attribute of conf.yaml file, using the corresponding Key enum.
        """
        return cls._data[key.value]

    @classmethod
    def get_sr_languages_data(cls, key:SrLanguagesKey) -> str:
        """
        Method to get an attribute of SrLanguages.yaml file, using the corresponding Key enum.
        """
        return cls._sr_data[key.value]

    @classmethod
    def find_st_languages_data(cls, key:SrLanguagesKey, value:str) -> bool:
        """
        Searches for the requested value and returns true or false if it is found or not.
        """
        return any(value in (k, v) for k, v in cls._sr_data[key.value].items())

class OutputPipelineManager():
    """
    Class that manages the output callback functions of
    the various services that can register their own
    function to be activated during the output pipeline.
    """
    @staticmethod
    def _noop_callback(_) -> Any:
        """Callback placeholder."""
        write_log("No elaboration callback has ben set.")

    _elaboration_callback = _noop_callback
    _output_callbacks = {}

    @classmethod
    def register_output_callbacks(cls, name: str, callback: Callable):
        """Register a out callback function under a unique name."""
        cls._output_callbacks[name] = callback

    @classmethod
    def register_elaboration_callback(cls, callback: Callable):
        """Register a elaboration of input callback function under a unique name."""
        cls._elaboration_callback = callback

    @classmethod
    def unregister_output_callbacks(cls, name: str):
        """Remove a previously registered callback."""
        cls._output_callbacks.pop(name, None)

    @classmethod
    def run(cls, input_data:str):
        """Run first elaboration callback all then all other registered 
        out callbacks, in order of registration."""

        output_data = cls._elaboration_callback(input_data)
        if not output_data:
            write_log("No elaboration callback set.")
            return
        for name, callback in cls._output_callbacks.items():
            if callable(callback):
                write_log(f"Output callback run: {name}")
                callback(output_data)

    @classmethod
    def has_callback(cls, name: str) -> bool:
        """Search for a callback by name"""
        return name in cls._output_callbacks
