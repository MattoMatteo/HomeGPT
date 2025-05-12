import system, network, audio_input, audio_output, time

def print_service_status():
    log_message = ""
    if audio_input.micManager.isDeviceActive():
        log_message = "Internal mic mode ON"
    else:
        log_message = "Internal mic mode OFF"
    system.write_log(log_message)

    if audio_output.audioOutputManager.isDeviceActive():
        log_message = "Internal audio output mode ON"
    else:
        log_message = "Internal audio output mode OFF"
    system.write_log(log_message)

    if network.networkmanager.mqtt_active:
        log_message = "MQTT mode ON"
    else:
        log_message = "MQTT mode OFF"
    system.write_log(log_message)

#--------------------- Main ----------------------
def main():
    network.networkmanager.init_mqtt_client(username=system.conf.config["mqtt"]["mqtt_username"],
                                            password=system.conf.config["mqtt"]["mqtt_password"],
                                            host=system.conf.config["mqtt"]["mqtt_host"],
                                            port=system.conf.config["mqtt"]["mqtt_port"])

    micOn = audio_input.micManager.init()
    audioOutputOn = audio_output.audioOutputManager.init()
    if micOn:
        audio_input.micManager.set_recognitionLanguage(system.conf.config["recognition_language"])
        internalMic_StopListening = audio_input.micManager.init_mic(system.conf.config['mic_name'])

    if audioOutputOn: #At least 1 audio output was found in the system
        audio_output.audioOutputManager.set_speechLanguageCode(system.conf.config["out_language"])
        audio_output.audioOutputManager.init_OutDevice(system.conf.config["out_device_name"])
        
    print_service_status()

    while network.networkmanager.mqtt_active or audio_input.micManager.isDeviceActive():
        time.sleep(0.1)

if __name__ == "__main__":
    main()