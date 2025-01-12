########################################################################################################################
#
#
#  	Project     	: 	Water Tank Level Reader and Booster Pressure Reader
#
#   File            :   measure.py
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
from datetime import datetime
import time, json, sys
import db
import mqtt
from apputils import * 

def calculate_type0(sensor_reading, config_params, logger):    
    
    sensor_raw_max      = config_params["sensor"]["sensor_raw_max"]
    water_height_max_cm = config_params["sensor"]["water_height_max_cm"]
    tank_height_cm      = config_params["sensor"]["tank_height_cm"]
    tank_capacity_l     = config_params["sensor"]["tank_capacity_l"]
    adjust_value        = config_params["sensor"]["adjust_value"]
    channel             = config_params["sensor"]["channel"]

        
    logger.debug("{time}, measure.calculate_type0 - Entering: ch:{channel}, val:{sensor_reading}".format(
        time            = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        channel         = config_params["sensor"]["channel"],
        sensor_reading  = sensor_reading,
    ))


    # Calculate water level
    if 0 <= sensor_reading <= sensor_raw_max:
        water_height_cm = ((sensor_reading / sensor_raw_max) * water_height_max_cm) - adjust_value
        
    else:   
        logger.error("{time}, measure.calculate_type0 - Reading must be between 0 and {sensor_raw_max}".format(
            time           = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            sensor_raw_max = sensor_raw_max,
        ))      
        water_height_cm = 0          
          
    # end if
    
    
    if water_height_cm < 0: 
        water_height_cm = 0
    

    # make pretty
    water_height_cm = round(water_height_cm, 2)
    percentage      = round((water_height_cm / tank_height_cm) * 100, 2)
    watervolume     = round(tank_capacity_l * percentage / 100, 2)
            

    logger.debug("{time}, measure.calculate_type0 - Exiting: ch:{channel}, {water_height_cm} cm, {percentage} %, {watervolume} L".format(
        time            = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        channel         = channel,
        water_height_cm = water_height_cm,
        percentage      = percentage,
        watervolume     = watervolume,
    ))

    
    return water_height_cm, percentage, watervolume

# end calculate_type0


# Measure boospressure
def boostpressure(sensor_reading, config_params, logger):
    
    max_pressure        = config_params["common"]["max_pressure"]             # BAR
    sensor_raw_max      = config_params["common"]["sensor_raw_max"]                # Max raw value to be read
    sensor_raw_min      = config_params["common"]["sensor_raw_min"]                # Min raw value when empty
    pos_value           = sensor_raw_max - sensor_raw_min
    channel             = config_params["sensor"]["channel"]

    
    logger.debug("{time}, measure.boostpressure - Entering: ch:{channel}, val:{sensor_reading}".format(
        time            = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        channel         = config_params["sensor"]["channel"],
        sensor_reading  = sensor_reading,
    ))

    if 0 <= sensor_reading <= sensor_raw_max:
        # Calcuate pressure           
        pressureBar  = round(max_pressure / pos_value * sensor_reading, 2)
        pressurePsi  = round((pressureBar * 14.5038), 2)      
        
    else:
        logger.error("{time}, measure.boostpressure - Reading must be between 0 and {sensor_raw_max}".format(
            time        = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            sensor_raw_max = sensor_raw_max,
        ))      
        pressureBar = 0
        pressurePsi = 0
         

    # end if
    
  
    logger.debug("{time}, measure.boostpressure - Exiting: ch:{channel}, {pressureBar} Bar, {pressurePsi} Psi".format(
        time        = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        channel     = channel,
        pressureBar = pressureBar,
        pressurePsi = pressurePsi,
    ))

    return pressureBar, pressurePsi

# end boostpressure



def chan_reader(chan, config_params):
    
    tag              = config_params["sensor"]["tag"]
    sleep_seconds    = config_params["sensor"]["sleep_seconds"]
    logfile          = config_params["sensor"]["logfile"]
    console_loglevel = config_params["sensor"]["console_loglevel"]  
    file_loglevel    = config_params["sensor"]["file_loglevel"]
    channel          = config_params["sensor"]["channel"]
    transducer_type  = config_params["sensor"]["transducer_type"]
    base_topic       = config_params["sensor"]["base_topic"]
    database         = config_params["sensor"]["database"]
    
    # Create new Channel Process specific logger's
    # chan_logger = basic_logger(logfile, loglevel)
    logger, fl, cl = advance_logger(logfile, console_loglevel, file_loglevel)
    
    logger.info("")
    logger.info('{time}, measure.chan_reader - Starting... Ch: {channel},'.format(
        time    = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        channel = channel
    ))
    
    logger.info("{time}, measure.chan_reader - Ch: {channel}, Tp: {transducer_type}, logfile: {logfile}, File Level: {fl}, Console Level: {cl}".format(
        time            = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        channel         = channel,
        transducer_type = transducer_type,
        logfile         = logfile,
        fl              = fl,
        cl              = cl
    ))
    logger.info("")


    if config_params["influxdb"]["enabled"] == 1:
        try:

            influx_client = db.connect(config_params, logger)
            
        except Exception as err:

            logger.critical('{time}, Something went wrong (InfluxDB Connection)) / Error... {err}'.format(
                time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                err  = err
            ))
            
            sys.exit(1)
                    
        # end try
    else:
        logger.debug('{time}, InfluxDB Disabled... '.format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        ))
        influx_client = None
    
    # end if
    
    
    # Initialize MQTT Broker Connection
    if config_params["mqtt"]["enabled"] == 1:
        try:

            mqtt_client = mqtt.connect(config_params, logger)
            
        except Exception as err:

            logger.critical('{time}, Something went wrong (MQTT Connection) / Error... {err}'.format(
                time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                err  = err
            ))

            logger.critical('{time}, MQTT Disconnect... '.format(
                time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            ))
            
            sys.exit(1)

        # end try
    else:
        logger.debug('{time}, MQTT Disabled... '.format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        ))
        mqtt_client = None
            
    # end if


    while True:
        
        tTimestamp  = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime(time.time()))       # timestamp for Influx, down to the second

        # Raw Measurements
        tValue      = round(chan.value, 6)
        tVoltage    = round(chan.voltage, 6)       


        if transducer_type == 0:
            
            tWaterLevel, tPercentage, tVolume = calculate_type0(tValue, config_params, logger)
            
            json_data = {
                "measurement" : database,           # select from "< >""
                "tags": {                           # where tank = "< >"
                    "tank": tag
                },
                "time" : tTimestamp,
                "fields": {
                    "water_level":      tWaterLevel,        # cm of water in tank
                    "fill_percentage":  tPercentage,        # based on distance and tank depth, percentage full
                    "water_volume":     tVolume,            # based on percentage and tank capacity
                    "voltage":          tVoltage,           # Actual Measured voltage
                    "value":            tValue,             # Actual Measured value
                }
            }
            
            logger.info('{time}, measure.chan_reader - ch: {ch}, tp: {tp}, Tag: {tag}, Level: {waterLevel} cm, Fill: {percentage}%, Volume: {volume} L, Voltage {voltage}, Value: {value}'.format(
                time            = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                ch              = channel,
                tp              = transducer_type,                
                tag             = tag,
                waterLevel      = tWaterLevel,
                percentage      = tPercentage,
                volume          = tVolume,
                voltage         = tVoltage,        
                value           = tValue             
            ))           
            
            
        # Bottom screw in, the json package send to mqtt and inserted into the database has a different structure.
        elif transducer_type == 1:
            
            tPressureBar, tPressurePsi = boostpressure(tValue, config_params, logger)                                # how many cm of water do we have                                           

            json_data = {
                "measurement" : database,           # select from "< >""
                "tags": {                           # where tank = "< >"
                    "pump": tag
                },
                "time" : tTimestamp,
                "fields": {
                    "pressureBAR":  tPressureBar,       # Boost Pressure in BAR
                    "pressurePsi":  tPressurePsi,       # Boost Pressure in Psi
                    "voltage":      tVoltage,           # Actual Measured voltage
                    "value":        tValue,             # Actual Measured value
                }
            }
            
            logger.info('{time}, measure.chan_reader - ch: {ch}, tp: {tp}, Tag: {tag}, Bar: {pressureBAR}, Psi: {pressurePsi}, Voltage: {voltage}, Value: {value}'.format(
                time            = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                ch              = channel,                
                tp              = transducer_type,
                tag             = tag,
                pressureBAR     = tPressureBar,         # BAR
                pressurePsi     = tPressurePsi,         # Psi / Pounds per Square Inch
                voltage         = tVoltage,             # voltage
                value           = tValue                # value
            ))  
        # end if
        
        
        # Insert InfluxDB
        if influx_client != None:
            
            influx_client.switch_database(database = database)
        
            ########################################################################
            # Insert into InfluxDB Database
            response = db.insert(influx_client, [json_data], logger)
    
        # end if


        # Publish MQTT
        if mqtt_client != None:
            
            ########################################################################
            # Publish MQTT
            mqtt.publish(mqtt_client, json.dumps(json_data), base_topic + "/json", logger)

        # end if    
        
        pp_json(json_data, logger)
        
        print("")            
        time.sleep(sleep_seconds)
        
    # end while True
# end chan_reader