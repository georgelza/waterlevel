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
__version__     = "1.0.1"
__copyright__   = "Copyright 2025, George Leonard"


#Libraries
from datetime import datetime
import time, json, sys, statistics
import db
import mqtt
from apputils import * 

def calculate_type0(sensor_reading, config_params, logger):    
    
    sensor_raw_max      = config_params["sensor"]["sensor_raw_max"]
    water_height_max_cm = config_params["sensor"]["water_height_max_cm"]
    tank_height_cm      = config_params["sensor"]["tank_height_cm"]
    tank_capacity_l     = config_params["sensor"]["tank_capacity_l"]
    neg_adjust_value    = config_params["sensor"]["neg_adjust_value"]
    pos_adjust_value    = config_params["sensor"]["pos_adjust_value"]
    channel             = config_params["sensor"]["channel"]

        
    logger.debug("{time}, measure.calculate_type0 - Entering: ch:{channel}, val:{sensor_reading}".format(
        time            = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        channel         = config_params["sensor"]["channel"],
        sensor_reading  = sensor_reading,
    ))


    # Calculate water level -> This is our primary value
    if 0 <= sensor_reading <= sensor_raw_max:
        water_height_cm = ((sensor_reading / sensor_raw_max) * water_height_max_cm) - neg_adjust_value + pos_adjust_value
        
    else:   
        logger.error("{time}, measure.calculate_type0 - Reading must be between 0 and {sensor_raw_max}".format(
            time           = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            sensor_raw_max = sensor_raw_max,
        ))      
        water_height_cm = 0          
          
    # end if
        
    if water_height_cm < 0: 
        water_height_cm = 0

    # end if

    # make pretty
    water_height_cm = round(water_height_cm, 0 )
    percentage      = round((water_height_cm / tank_height_cm) * 100, 0)
    watervolume     = round(tank_capacity_l * ((water_height_cm / tank_height_cm) * 100) / 100, 0)

    # original, watervolume     = round(tank_capacity_l * percentage / 100, 0)
            

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
    
    max_pressure        = config_params["common"]["max_pressure"]                   # BAR
    sensor_raw_max      = config_params["common"]["sensor_raw_max"]                 # Max raw value to be read
    sensor_raw_min      = config_params["common"]["sensor_raw_min"]                 # Min raw value when empty
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


def median_readings(chan, config_params, logger):

    samples                 = config_params["sensor"]["samples"]
    max_samples             = config_params["sensor"]["max_samples"]
    samples_sleep_seconds   = config_params["sensor"]["sample_sleep_seconds"]

    logger.debug("{time}, measure.median_readings - Entering: ".format(
        time=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
    ))

    tValueAr   = []
    tVoltageAr = []
    i          = 0            # current valie reading
    maxLoop    = 0            # max loops to tru
    tBreak     = False        # did we exit because we hit maxLoop
    while i < samples:
        
        chanValue      = chan.value
        channelVoltage = chan.voltage
        
        if chanValue > 0 and channelVoltage > 0:
            tValueAr.append(chanValue)
            tVoltageAr.append(channelVoltage)
            i = i + 1
            
            logger.debug("{time}, measure.median_readings {maxLoop} {i} - Value: {chanValue}, Voltage: {channelVoltage}".format(
                time  = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                maxLoop        = maxLoop,
                i              = i,
                chanValue      = chanValue,
                channelVoltage = channelVoltage,
            ))
            
        maxLoop = maxLoop + 1
        time.sleep(samples_sleep_seconds)
        if maxLoop == max_samples:
            tBreak = True
            break

        # end if
    # end while

    tValue   = statistics.median(tValueAr)
    tVoltage = statistics.median(tVoltageAr)

    logger.debug("{time}, measure.median_readings - Exiting - Max Samples: {tBreak}, Value: {tValue}, Voltage: {tVoltage}".format(
        time     = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        tBreak   = tBreak,
        tValue   = tValue,
        tVoltage = tVoltage,
    ))

    return round(tValue, 6), round(tVoltage, 6)

#end median_readings


def chan_reader(chan, config_params):
    
    tag                 = config_params["sensor"]["tag"]
    sleep_seconds       = config_params["sensor"]["sleep_seconds"]
    logfile             = config_params["sensor"]["logfile"]
    console_loglevel    = config_params["sensor"]["console_loglevel"]  
    file_loglevel       = config_params["sensor"]["file_loglevel"]
    channel             = config_params["sensor"]["channel"]
    transducer_type     = config_params["sensor"]["transducer_type"]
    base_topic          = config_params["sensor"]["base_topic"]
    database            = config_params["sensor"]["database"]
    influxdb_enabled    = config_params["sensor"]["influxdb_enabled"]
    influxdb_attempts   = config_params["influxdb"]["attempts"]
    influxdb_backoff    = config_params["influxdb"]["backoff"]            
    mqtt_enabled        = config_params["sensor"]["mqtt_enabled"]
    mqtt_attempts       = config_params["mqtt"]["attempts"]
    mqtt_backoff        = config_params["mqtt"]["backoff"]            

    # Create new Channel Process specific logger's
    logger, fl, cl = advance_logger(logfile, console_loglevel, file_loglevel)
    
    print(" {time}, measure.chan_reader - Logger enabled for channel {channel}, Logfile: {logfile}, Console: {console_loglevel}, File: {file_loglevel}".format(
        time                = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        channel             = channel,
        logfile             = logfile,
        console_loglevel    = console_loglevel,
        file_loglevel       = file_loglevel,
    ))

    logger.debug("")
    logger.debug('{time}, measure.chan_reader - Initializing Ch: {channel},'.format(
        time    = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        channel = channel
    ))
    
    logger.debug("{time}, measure.chan_reader - Ch: {channel}, Tp: {transducer_type}, logfile: {logfile}, File Level: {fl}, Console Level: {cl}".format(
        time            = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        channel         = channel,
        transducer_type = transducer_type,
        logfile         = logfile,
        fl              = fl,
        cl              = cl
    ))
    logger.debug("")


    if influxdb_enabled == 1:

        influx_client = db.connect(config_params, logger)
        
        if influx_client == 0:
            sys.exit(-1)

        # end if
    else:
        logger.debug('{time}, measure.chan_reader - InfluxDB Not Enabled... '.format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        ))
    
    # end if
    
    
    # Initialize MQTT Broker Connection
    if mqtt_enabled == 1:

        mqtt_client = mqtt.connect(config_params, logger)
        
        if mqtt_client == 0:
            sys.exit(-1)

        # end if
    else:
        logger.debug('{time}, measure.chan_reader - MQTT Not Enabled... '.format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        ))
            
    # end if


    while True:
        
        logger.debug('{time}, measure.chan_reader - Starting Loop Ch: {channel},'.format(
            time    = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            channel = channel
        ))
        
        
        tTimestamp      = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime(time.time()))       # timestamp for Influx, down to the second
        influxdb_result = 0
        mqtt_result     = 0
            
        tValue, tVoltage = median_readings(chan, config_params, logger)
        
        if tValue > 0 and tVoltage > 0:
            if transducer_type == 0:
                
                tWaterLevel, tPercentage, tVolume = calculate_type0(tValue, config_params, logger)
                
                json_data = {
                    "measurement" : database,                   # select from "< >""
                    "tags": {                                   # where tank = "< >"
                        "tank": tag
                    },
                    "time" : tTimestamp,
                    "fields": {
                        "water_level":      tWaterLevel,        # cm of water in tank
                        "fill_percentage":  tPercentage,        # based on distance and tank depth, percentage full
                        "water_volume":     tVolume,            # based on percentage and tank capacity
                        "value":            int(tValue),        # Actual Measured value    => int
                        "voltage":          tVoltage,           # Actual Measured voltage  => float
                    }
                }
                       
                
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
                        "value":        int(tValue),        # Actual Measured value
                        "voltage":      tVoltage,           # Actual Measured voltage
                    }
                }
                
            # end if
             
                       
            # Insert InfluxDB
            if influxdb_enabled == 1:
                
                influx_client.switch_database(database = database)
            
                influxdb_result = db.insert(influx_client, [json_data], logger)
                
                logger.info('{time}, measure.chan_reader - influxdb_result {influxdb_result} !!!: '.format(
                    time            = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                    influxdb_result = influxdb_result,
                ))      
                       
                if influxdb_result == 0:
                    insertAttempt = 1
                    
                    time.sleep(insertAttempt * influxdb_backoff)  # Cause some back off if we having problems,
                    
                    while insertAttempt < influxdb_attempts and influxdb_result == 0:
                        
                        influx_client = db.connect(config_params, logger)
                        
                        logger.debug('{time}, measure.chan_reader - Reconnecting to InfluxDB .Channel: {channel}'.format(
                            time            = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                            ch              = channel,
                        ))
                        
                        influx_client.switch_database(database = database)
            
                        influxdb_result = db.insert(influx_client, [json_data], logger)
                        
                        insertAttempt += 1

                    # and while
                    
                    if influxdb_result == 0:
                        logger.debug('{time}, measure.chan_reader - InfluxDB Insert Failed after {insertAttempt} attempts!!!: '.format(
                            time            = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                            insertAttempt   = insertAttempt,
                        ))
                        
                        sys.exit(-1)
                        
                    # end if
                #end if        
            # end if

            # Publish MQTT
            if mqtt_enabled == 1:
                
                mqtt_result = mqtt.publish(mqtt_client, json.dumps(json_data), base_topic + "/json", logger)
                
                logger.info('{time}, measure.chan_reader - mqtt_result {mqtt_result} !!!: '.format(
                    time            = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                    mqtt_result   = mqtt_result,
                ))
                
                if mqtt_result == 0:
                    publishAttempt = 1
                    
                    time.sleep(publishAttempt * mqtt_backoff)  # Cause some back off if we having problems,
                    
                    while publishAttempt < mqtt_attempts and mqtt_result == 0:
                        mqtt_client = mqtt.connect(config_params, logger)

                        logger.debug('{time}, measure.chan_reader - Reconnecting to MQTT .Channel: {channel}'.format(
                            time            = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                            ch              = channel,
                        ))
                                    
                        mqtt_result = mqtt.publish(mqtt_client, json.dumps(json_data), base_topic + "/json", logger)
                        
                        publishAttempt += 1

                    # end while
                    if mqtt_result == 0:
                        logger.debug('{time}, measure.chan_reader - MQTT Publish Failed after {publishAttempt} attempts!!!: '.format(
                            time            = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                            publishAttempt  = publishAttempt,
                        ))
                        
                        sys.exit(-1)
                        
                    # end if
                # end if
            # end if    
            
            
            if transducer_type == 0:
                
                logger.info('{time}, measure.chan_reader - ch: {ch}, tp: {tp}, Tag: {tag}, Level: {waterLevel} cm, Fill: {percentage}%, Volume: {volume} L, Voltage {voltage}, Value: {value}, {influxdb_enabled}, {influxdb_result}, {mqtt_enabled}, {mqtt_result}'.format(
                    time             = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                    ch               = channel,
                    tp               = transducer_type,                
                    tag              = tag,
                    waterLevel       = tWaterLevel,
                    percentage       = tPercentage,
                    volume           = tVolume,
                    value            = int(tValue),             
                    voltage          = tVoltage,
                    influxdb_enabled = influxdb_enabled,
                    influxdb_result  = influxdb_result,
                    mqtt_enabled     = mqtt_enabled,
                    mqtt_result      = mqtt_result,
                ))           
                
                
            # Bottom screw in, the json package send to mqtt and inserted into the database has a different structure.
            elif transducer_type == 1:
                                
                logger.info('{time}, measure.chan_reader - ch: {ch}, tp: {tp}, Tag: {tag}, Bar: {pressureBAR}, Psi: {pressurePsi}, Voltage: {voltage}, Value: {value}, {influxdb_enabled}, {influxdb_result}, {mqtt_enabled}, {mqtt_result}'.format(
                    time             = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                    ch               = channel,                
                    tp               = transducer_type,
                    tag              = tag,
                    pressureBAR      = tPressureBar,         # BAR
                    pressurePsi      = tPressurePsi,         # Psi / Pounds per Square Inch
                    value            = int(tValue),          # value  
                    voltage          = tVoltage,              # voltage
                    influxdb_enabled = influxdb_enabled,
                    influxdb_result  = influxdb_result,
                    mqtt_enabled     = mqtt_enabled,
                    mqtt_result      = mqtt_result,
                ))  
            # end if
            
            pp_json(json_data, logger)

            logger.debug('{time}, measure.chan_reader - Completed Loop Ch: {channel},'.format(
                time    = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                channel = channel
            ))
                        
            logger.debug('')         
            logger.debug('')         

            time.sleep(sleep_seconds)

        # end if tValue > 0 and tVoltage > 0
    # end while True
# end chan_reader