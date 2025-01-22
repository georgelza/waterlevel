########################################################################################################################
#
#
#  	Project     	: 	Water Tank Level Reader and Booster Pressure Reader
#
#   File            :   mqtt.py
#
#	By              :   George Leonard ( georgelza@gmail.com )
#
#   Created     	:   28 Dec 2024
#
#   Notes       	:
#
#######################################################################################################################
__author__      = "George Leonard"
__email__       = "georgelza@gmail.com"
__version__     = "1.0.1"
__copyright__   = "Copyright 2025, George Leonard"


#Libraries
import paho.mqtt.client as mqtt
import sys
import RPi.GPIO as GPIO
from datetime import datetime

mqtt_codes = [
    "Connection accepted",			
    "Connection refused: Level of MQTT protocol not supported by server",			
    "Connection refused: Client identifier not allowed by server.",		
    "Connection refused: Network connection successful but MQTT service is unavailable.",				
    "Connection refused: Data in username or password is malformed.",
    "Connection refused: Client not authorized to connect."
]

############# Instantiate a connection to the MQTT Server ##################
def connect(config_params, logger):

    # Configure the Mqtt connection etc.
    broker      = config_params["mqtt"]["broker"]
    port        = config_params["mqtt"]["port"]
    username    = config_params["mqtt"]["username"]
    password    = config_params["mqtt"]["password"]
    clienttag   = config_params["sensor"]["mqtt_clienttag"]

    logger.info("")
    logger.info("#####################################################################")
    logger.info("")
    
    logger.info('{time}, mqtt.connect - ch: {clienttag} Creating connection to MQTT... '.format(
        time        = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        clienttag   = clienttag,
    ))
        
    try:
        
        mqtt.Client.connected_flag      = False                     # this creates the flag in the class
        mqtt.Client.bad_connection_flag = False                     # this creates the flag in the class

        client = mqtt.Client(clienttag)                             # create client object client1.on_publish = on_publish #assign function to callback
                                                                    # client1.connect(broker,port) #establish connection client1.publish("house/bulb1","on")

        client.on_disconnect = on_disconnect                        # Bind callback functions
        client.username_pw_set(username, password)
        client.connect(broker, port)                                # connect

        logger.info("{time}, mqtt.connect - Connection to MQTT Configured... Broker: {broker}, Port: {port}, Client: {clienttag}".format(
            time        = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            broker      = broker,
            port        = port,
            clienttag   = clienttag,
        ))
    
    except Exception as err:
        logger.critical("{time}, mqtt.connect - Connection to MQTT Failed... {broker}, Port: {port}, Err: {err}".format(
            time   = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            broker = broker,
            port   = port,
            err    = err
        ))

        GPIO.cleanup()
        
        client = 0
        
    finally:

        logger.debug("")
        logger.debug("#####################################################################")
        logger.debug("")

        return client
        
    # end try
    

#end mqtt_connect


def on_disconnect(client, userdata, flags, rc=0):

    client.connected_flag = False
    
#end on_disconnect


def publish(client, json_data, base_topic, logger):

    try:

        ret = client.publish(base_topic, json_data, 0)           # QoS = 0

        logger.debug("{time}, mqtt.publish - MQTT Publish Completed: {ret}".format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            ret  = ret,
        ))  
        
        return ret
    
    except Exception as err:
        logger.critical('{time}, mqtt.publish - MQTT Publish Failed !!!: {err}'.format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            err  = err
        ))
    
        # Return 0
        return 0
        
    # end try
#end publish


def close(client, logger):

    try:

        client.disconnect()
        
        logger.debug('{time},  mqtt.close - Connection to MQTT Closed... '.format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        ))
        
    except Exception as err:
        logger.critical('{time}, mqtt.close - Connection Close to MQTT Failed... {err}'.format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            err  = err
        ))

        sys.exit(-1)
        
    # end try
#end close