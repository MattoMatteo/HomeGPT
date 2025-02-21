from SrLanguages import recognitionLanguageCode, outLanguageCode

#########################################################################################################
# The software, through the use of selenium, allows the automated use of the site: https://chatgpt.it/  #
# which offers the paid service of chatGPT for free.                                                    #
# Using selenium directly on https://chatgpt.com/ does not work (not even in the free form).            #
#########################################################################################################

#Input mic device
        #1. Set to NONE if you dont wanna use internal mic but just another device that comunicate with MQTT
        #2. "default" to automaticaly select a default mic input
        #3. The name of mic. If the mic will not found, the default will be used.
                #If no one device will be find, check the log for the names list of devices available

mic_name = None    
recognition_language = recognitionLanguageCode.ITALIAN_ITALY #It uses Google APIs. For simplicity I have added a code list for the various languages via enums in SrLanguages.py: InputLanguages.
activation_words = ("hey google","alexa") # a tuple of words that trigger speech recognition

#output internal device
        #Device Name:
        #1. Set to NONE if you dont wanna use internal audio output device but just another device that comunicate with MQTT
        #2. "default" to automaticaly select a default audio output device
        #3. The name of audio output device. If the audio output device will not found, the default will be used.
                #If no one device will be find, check the log for the names list of devices available
out_device_name = None

        #Language code:
        #1. It uses gtts (Google text to speech), so you can search your language code.
        #2. If an invalid code will be insert, "en" will be set by default. For simplicity I have added a code list for the various languages via enums in SrLanguages.py: OutputLanguages.
out_language = outLanguageCode.ITALIAN

#MQTT
        #set ip or hostname
mqtt_host = "" # example "192.168.1.1" 
mqtt_username = ""
matt_password = ""
mqtt_port = 1883 # 1883 commonly
        #topic listening FROM broker
mqtt_topic_subscription = "HomeGPT/listen" 
        #publication topic TO THE broker
mqtt_topic_publication = "HomeGPT/respond" 

