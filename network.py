"""
Module that manages the software connectivity.
Currently only the mqtt protocol is included.
"""
from socket import gaierror
from paho.mqtt import client as mqtt_client
from paho.mqtt.enums import MQTTErrorCode

from system import Configurations as Conf, ConfigKey, OutputPipelineManager as Pipeline
from log_manager import setup_logger

logger = setup_logger("NETWORK")

class NetworkManager():
    """
    Manage all software connectivity services.
    """
    mqtt_active = False
    mqtt_client = mqtt_client.Client()

    @classmethod
    def mqtt_connect_to_broker(cls,username:str, password:str, host:str, port:int)->bool:
        """
        Method that allows connection with a broker within your network.
        The parameters used to connect will be taken from the config.yaml file.
        If the broker parameters entered are incorrect, the initialization
        will not be performed and False will be returned. True otherwise.
        """
        cls.mqtt_client.username_pw_set(username, password)
        try:
            error_code = cls.mqtt_client.connect(host, port, 60)
            if error_code != MQTTErrorCode.MQTT_ERR_SUCCESS:
                return False
        except (ValueError, TypeError, gaierror, ConnectionRefusedError) as e:
            logger.error(f"Unable to connect to broker. Check hostname/ip and port. Error: {e}")
            cls.mqtt_active = False
            return False
        if cls.mqtt_client.loop_start() != MQTTErrorCode.MQTT_ERR_SUCCESS:
            logger.error(f"Unable to start mqtt loop. Error: {error_code}")
            return False
        if not cls.mqtt_publish_response(""):
            logger.error("Unable to connect to broker. Check hostname/ip and port.")
            return False
        logger.error(f"Connected to the mqtt broker: {host}:{port}")
        cls.mqtt_active = True
        return True

    @classmethod
    def mqtt_publish_response(cls, response:str)->bool:
        """
        Method to publish a mqtt message to the topic set in the configuration file.
        """
        error_code = cls.mqtt_client.publish(
            Conf.get_conf_data(ConfigKey.MQTT_TOPIC_PUBLICATION),
            response
        )
        try:
            error_code.wait_for_publish(1)
        except RuntimeError as e:
            logger.error(
                "Unable to publish MQTT message to broker. "
                f"Error code: {e}.")
            return False
        return True

@NetworkManager.mqtt_client.connect_callback()
def on_connect(client: mqtt_client.Client, _, __, ___):
    """
    Callback when broker accept our connection request.
    At this point we can subscribe to topic that was specified in config.yaml.
    """
    client.subscribe(Conf.get_conf_data(ConfigKey.MQTT_TOPIC_SUBSCRIPTION))

@NetworkManager.mqtt_client.message_callback()
def on_message(_, __, msg: mqtt_client.MQTTMessage):
    """
    Callback when an incoming message arrive from broker.
    """
    if msg.topic == Conf.get_conf_data(ConfigKey.MQTT_TOPIC_SUBSCRIPTION):
        message = str(msg.payload.decode())
        topic = str(msg.topic)
        logger.info(f"Message received: {message} on topic {topic}")
        Pipeline.run(message)

def callback_for_pipeline(message:str):
    """
    Callback function for publishing output to the network,
    based on user settings and network capabilities.
    """
    if NetworkManager.mqtt_active:
        return NetworkManager.mqtt_publish_response(message)
    return True
