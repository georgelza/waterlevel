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
__version__     = "0.0.1"
__copyright__   = "Copyright 2024, George Leonard"


#Libraries
import paho.mqtt.client as mqtt
import sys
import RPi.GPIO as GPIO
from datetime import datetime


############# Instantiate a connection to the MQTT Server ##################
def connect(config_params, main_logger):

    # Configure the Mqtt connection etc.
    broker      = config_params["mqtt"]["broker"]
    port        = config_params["mqtt"]["port"]
    clienttag   = config_params["mqtt"]["clienttag"]
    username    = config_params["mqtt"]["username"]
    password    = config_params["mqtt"]["password"]
    base_topic  = config_params['mqtt']['base_topic']

    main_logger.info("")
    main_logger.info("#####################################################################")
    main_logger.info("")
    
    main_logger.info('{time}, mqtt.connect - Creating connection to MQTT... '.format(
        time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
    ))

    main_logger.info('{time}, mqtt.connect - Broker     : {broker} '.format(
        time   = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        broker = broker
    ))

    main_logger.info('{time}, mqtt.connect - Port       : {port}'.format(
        time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        port = port
    ))

    main_logger.info('{time}, mqtt.connect - Client Tag : {clienttag} '.format(
        time      = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        clienttag = clienttag
    ))

    main_logger.info('{time}, mqtt.connect - Base Topic : {base_topic} '.format(
        time=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        base_topic = base_topic
    ))
        

    try:
        
        mqtt.Client.connected_flag      = False                     # this creates the flag in the class
        mqtt.Client.bad_connection_flag = False                     # this creates the flag in the class

        client = mqtt.Client(clienttag)                             # create client object client1.on_publish = on_publish #assign function to callback
                                                                    # client1.connect(broker,port) #establish connection client1.publish("house/bulb1","on")

        client.on_disconnect = on_disconnect                        # Bind callback functions
        client.username_pw_set(username, password)
        client.connect(broker, port)                                # connect


    except Exception as err:
        main_logger.critical("{time}, mqtt.connect - Connection to MQTT Failed... {broker}, Port: {port}, Err: {err}".format(
            time   = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            broker = broker,
            port   = port,
            err    = err
        ))

        main_logger.critical("")
        main_logger.critical("#####################################################################")
        main_logger.critical("")

        GPIO.cleanup()
        sys.exit(1)
    
    finally:
        
        main_logger.info("{time}, mqtt.connect - Connected to to MQTT Broker: {broker}, Port: {port}".format(
            time   = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            broker = broker,
            port   = port
        ))

        main_logger.info("")
        main_logger.info("#####################################################################")
        main_logger.info("")
        
    # end try
    
    return client

#end mqtt_connect


def on_disconnect(client, userdata, flags, rc=0):

    client.connected_flag = False
    
#end on_disconnect


def publish(client, json_data, topic, main_logger):

    try:

        ret = client.publish(topic, json_data, 0)           # QoS = 0

    except Exception as err:
        main_logger.critical('{time}, mqtt.publish - Publish Failed !!!: {err}'.format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            err  = err
        ))
    
    finally:
        main_logger.info("{time}, mqtt.publish - MQTT Publish returned: {ret}".format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            ret  = ret
        ))    
    
    # end try
#end publish


def close(client, main_logger):

    try:

        client.disconnect()
        
    except Exception as err:
        main_logger.critical('{time}, mqtt.close - Connection Close to MQTT Failed... {err}'.format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            err  = err
        ))

        sys.exit(-1)

    finally:    
        main_logger.info('{time},  mqtt.close - Connection to MQTT Closed... '.format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        ))
        
    # end try
#end close