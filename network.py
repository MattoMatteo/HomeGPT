#mqtt for comunication between software and broker to send response and if dont wanna use integrated mic
import paho.mqtt.client as mqtt
import system, reply_manager, audio_output

class NetworkManager():
    def __init__(self):
        self.mqtt_active = False

    def init_mqtt_client(self,username:str, password:str, host:str, port:int)->bool:
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.username_pw_set(username,password)
        self.mqtt_client.on_connect = on_connect
        self.mqtt_client.on_message = on_message
        try:
            error_code = int(self.mqtt_client.connect(host, port, 60))
        except Exception as error_code:
            system.write_log(f"Unable to connect to broker. Check hostname/ip and port. Error: {error_code}")
            self.mqtt_active = False
            return False
        
        self.mqtt_client.loop_start()
        self.mqtt_active = True
        return True
        
    def mqtt_publish_response(self,response:str)->bool:
        MQTT_error_code = self.mqtt_client.publish(system.conf.config["mqtt"]["mqtt_topic_publication"], response)
        if MQTT_error_code.rc == mqtt.MQTTErrorCode.MQTT_ERR_NO_CONN:
                system.write_log("Unable to publish MQTT message to broker. Please check your username and password.")
                return False
        return True

networkmanager = NetworkManager()

def on_connect(client, userdata, flags, rc):
    client.subscribe(system.conf.config["mqtt"]["mqtt_topic_subscription"])

def on_message(client, userdata, msg):
    if msg.topic == system.conf.config["mqtt"]["mqtt_topic_subscription"]:
        message = str(msg.payload.decode())
        topic = str(msg.topic)
        system.write_log(f"Message received: {message} on topic {topic}")

        response = reply_manager.freeGPT.ask_to_chatgpt_noAPI(message)

        networkmanager.mqtt_publish_response(client,response)
        if audio_output.audioOutputManager.isDeviceActive():
            audio_output.audioOutputManager.start_text_to_speech(response)
