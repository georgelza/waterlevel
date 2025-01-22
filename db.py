########################################################################################################################
#
#
#  	Project     	: 	Water Tank Level Reader and Booster Pressure Reader
#
#   File            :   db.py
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
from influxdb import InfluxDBClient 
from influxdb_client.client.exceptions import InfluxDBError

from datetime import datetime
import sys


############# Instantiate a connection to the InfluxDB ##################
def connect(config_params, logger):

    host     = config_params['influxdb']['host']
    port     = config_params['influxdb']['port']
    channel  = config_params['sensor']['channel']
    
    logger.debug("")
    logger.debug("#####################################################################")
    logger.debug("")

    logger.info('{time}, db.connect - {channel}, Creating connection to InfluxDB... '.format(
        time    = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        channel = channel,
    ))

    try:

        client = InfluxDBClient(host = host, port = port)

        logger.info('{time}, db.connect - Connection to InfluxDB Configured... Host: {host}, Port: {port}, Channel: {channel}'.format(
            time    = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            host        = host,
            port        = port,
            channel     = channel,
        ))

    except InfluxDBError as err:
        logger.critical('{time}, db.connect - InfluxDB Error... {err}'.format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            err  = err
        ))

        client = 0

    except Exception as err:
        logger.critical('{time}, db.connect - Connection to InfluxDB Failed... {err}'.format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            err  = err
        ))

        client = 0
            
    finally:
    
        logger.debug("")
        logger.debug("#####################################################################")
        logger.debug("")

        return client

    # end try
         
#end influx_connect


def insert(client, json_data, logger):

    try:

        response = client.write_points(points = json_data)
    
        logger.debug("{time}, db.insert - InfluxDB Insert Completed: {response}".format(
            time     = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            response = response
        ))   
        

    except InfluxDBError as err:
        logger.error('{time}, db.insert - InfluxDB Insert Failed !!!: {err}'.format(
            time   = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            err    = err
        ))
        
        response = 0
            
    except Exception as err:
        logger.error('{time}, db.insert - Unknown Exception !!!: {err}'.format(
            time   = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            err    = err
        ))        
        
        response = 0
    
    finally:
        return response

    # end try    
#end influx_insert