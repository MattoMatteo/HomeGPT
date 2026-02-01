"""
Initial module where basic components like inputs and outputs are initialized
and callback functions are loaded into the response pipeline
"""
import time

from system import Configurations as Conf, ConfigKey
from system import OutputPipelineManager as Pipeline
from log_manager import setup_logger
import network
import audio_input
import audio_output
import reply_manager

logger = setup_logger("MAIN")

def print_service_status():
    """
    Convenience function for printing which services have been activated.
    Like Mic, audio output and MQTT.
    """
    log_message = ""
    if any(mic.is_device_active() for mic in audio_input.mic_list):
        log_message = "Internal mic mode ON"
    else:
        log_message = "Internal mic mode OFF"
    logger.info(log_message)

    if any(device.is_device_active() for device in audio_output.audio_output_list):
        log_message = "Internal audio output mode ON"
    else:
        log_message = "Internal audio output mode OFF"
    logger.info(log_message)

    if network.NetworkManager.mqtt_active:
        log_message = "MQTT mode ON"
    else:
        log_message = "MQTT mode OFF"
    logger.info(log_message)

#--------------------- Main ----------------------
def main():
    """
    Starting function where the basic components will be initialized,
    based on the choices made in the configuration file.
    Mqtt, microphone, audio output.
    """
    network.NetworkManager.mqtt_connect_to_broker(
        username=Conf.get_conf_data(ConfigKey.MQTT_USERNAME),
        password=Conf.get_conf_data(ConfigKey.MQTT_PASSWORD),
        host=Conf.get_conf_data(ConfigKey.MQTT_HOST),
        port=Conf.get_conf_data(ConfigKey.MQTT_PORT)
    )

    #MIC_NAME and RECOGNITION_LANGUAGE will be a list to init more then one mic at time
    audio_input.mic_list.append(
        audio_input.MicManager(mic_name=Conf.get_conf_data(ConfigKey.MIC_NAME),
            recognition_language=Conf.get_conf_data(ConfigKey.RECOGNITION_LANGUAGE))
    )

    #OUT_DEVICE_NAME will be a list to init more then one mic at time
    audio_output.audio_output_list.append(
        audio_output.AudioOutputManager(Conf.get_conf_data(ConfigKey.OUT_DEVICE_NAME),
            speech_language=Conf.get_conf_data(ConfigKey.OUT_LANGUAGE))
    )

    Pipeline.register_elaboration_callback(reply_manager.callback_for_pipeline)
    Pipeline.register_output_callbacks("network", network.callback_for_pipeline)
    Pipeline.register_output_callbacks("audio_output", audio_output.callback_for_pipeline)

    print_service_status()
    any_mic_active = any(mic.is_device_active() for mic in audio_input.mic_list)
    while network.NetworkManager.mqtt_active or any_mic_active:
        time.sleep(0.1)

if __name__ == "__main__":
    main()
