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
__version__     = "0.0.1"
__copyright__   = "Copyright 2024, George Leonard"


#Libraries
from influxdb import InfluxDBClient 
from datetime import datetime
import sys


############# Instantiate a connection to the InfluxDB ##################
def connect(config_params, my_logger):

    host     = config_params['influxdb']['host']
    port     = config_params['influxdb']['port']
    
    my_logger.info("")
    my_logger.info("#####################################################################")
    my_logger.info("")

    my_logger.info('{time}, db.connect - Creating connection to InfluxDB... '.format(
        time    = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
    ))

    my_logger.info('{time}, db.connect - Host     : {host} '.format(
        time    = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        host    = config_params['influxdb']['host']
    ))

    my_logger.info('{time}, db.connect - Port     : {port}'.format(
        time    = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        port    = config_params['influxdb']['port']
    ))

    my_logger.info('{time}, db.connect - Database : {database} '.format(
        time     = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        database = config_params['influxdb']['dbname']
    ))

    try:

        client = InfluxDBClient(host = host, port = port)

    except Exception as err:
        my_logger.critical('{time}, db.connect - Connection to InfluxDB Failed... {err}'.format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            err  = err
        ))

        my_logger.critical("")
        my_logger.critical("#####################################################################")
        my_logger.critical("")

        sys.exit(-1)
        
    finally:
    
        my_logger.info('{time}, db.connect - Connection to InfluxDB Succeeded... '.format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        ))

        my_logger.info("")
        my_logger.info("#####################################################################")
        my_logger.info("")

    # end try
        
    return client
    
 
#end influx_connect


def insert(client, json_data, main_logger):

    try:

        response = client.write_points(points=json_data)

    except Exception as err:
        main_logger.error('{time}, db.insert - Write Failed !!!: {err}'.format(
            time   = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            err    = err
        ))
    
    finally:
    
        main_logger.info("{time}, db.insert - InfluxDB Write operation: {response}".format(
            time     = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            response = response,
        ))       

    # end try    
#end influx_insert