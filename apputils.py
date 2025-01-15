########################################################################################################################
#
#
#  	Project     	: 	Water Tank Level Reader
#
#   File            :   apputils.py
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
import configparser
import logging, json
from datetime import datetime

def get_config_params(configfile, descriptor=""):
    """ Get/Read config file contents """

    parser = configparser.ConfigParser()
    parser.read(configfile)

    params = {}
    for section_name in parser.sections():
        items = {}
        for itemname, itemvalue in parser.items(section_name):
            items[itemname] = itemvalue

        # end for
        params[section_name] = items
    # end for


    params['common']['console_loglevel']    = int(params['common']['console_loglevel'])
    params['common']['file_loglevel']       = int(params['common']['file_loglevel'])
    params['common']['logfile']             = params['common']['logfile'].lower()
    params["common"]["channels"]            = params["common"]["channels"].split(",")

    # transducer_type
    #   Water Level   Thread fit Transducer_type  0.5 Bar = 0     water level/volume json package
    #   Booster       Thread fit Transducer_type  10 Bar  = 1     booster json package
    #   Ken           Drop in Transducer_type     0.5 Bar = 2     water level/volume json package

    # params['common']['booster']
    #   0 - Disabled
    #   1 - Enabled
    
    if params['common']['booster'] == "1":
        chan = "booster"
        params[chan]["channel"]                 = int(params[chan]['channel'])
        params[chan]["transducer_type"]         = int(params[chan]["transducer_type"])
        params[chan]["sleep_seconds"]           = int(params[chan]["sleep_seconds"])
        params[chan]['max_pressure']            = int(params[chan]['max_pressure'])
        params[chan]["sensor_raw_value"]        = int(params[chan]["sensor_raw_max"])
        params[chan]["sensor_raw_value"]        = int(params[chan]["sensor_raw_value"])
        # params[chan]["database"]                = params[chan]["database"]
        # params[chan]["tag"]                     = params[chan]["tag"]
        # params[chan]["base_topic"]              = params[chan]["base_topic"]        
        params[chan]['logfile']                 = params[chan]['logfile'].lower()
        params[chan]['console_loglevel']        = int(params[chan]['console_loglevel'])
        params[chan]['file_loglevel']           = int(params[chan]['file_loglevel'])
        params[chan]['adjust_value']            = int(params[chan]['adjust_value'])
        params[chan]['samples']                 = int(params[chan]['samples'])
        params[chan]['max_samples']             = int(params[chan]['max_samples'])
        params[chan]['sample_sleep_seconds']    = int(params[chan]['sample_sleep_seconds'])
        params[chan]['mqtt_enabled']            = int(params[chan]['mqtt_enabled'])
        params[chan]['influxdb_enabled']        = int(params[chan]['influxdb_enabled'])

    for x in range(8):        
        if str(x) in params["common"]["channels"]:
            chan = "chan" + str(x)
            params[chan]["channel"]                 = int(params[chan]["channel"])
            params[chan]["transducer_type"]         = int(params[chan]["transducer_type"])
            params[chan]["tank_height_cm"]          = int(params[chan]["tank_height_cm"])
            params[chan]["tank_capacity_l"]         = int(params[chan]["tank_capacity_l"])
            params[chan]["sleep_seconds"]           = int(params[chan]["sleep_seconds"])
            params[chan]["sensor_raw_max"]          = int(params[chan]["sensor_raw_max"])
            params[chan]["water_height_max_cm"]     = int(params[chan]["water_height_max_cm"])
            # params[chan]["database"]                = params[chan]["database"]
            # params[chan]["tag"]                     = params[chan]["tag"]
            # params[chan]["base_topic"]              = params[chan]["base_topic"]
            params[chan]['logfile']                 = params[chan]['logfile'].lower()
            params[chan]['console_loglevel']        = int(params[chan]['console_loglevel'])
            params[chan]['file_loglevel']           = int(params[chan]['file_loglevel'])
            params[chan]['adjust_value']            = int(params[chan]['adjust_value'])
            params[chan]['samples']                 = int(params[chan]['samples'])
            params[chan]['max_samples']             = int(params[chan]['max_samples'])
            params[chan]['sample_sleep_seconds']    = int(params[chan]['sample_sleep_seconds'])
            params[chan]['mqtt_enabled']            = int(params[chan]['mqtt_enabled'])
            params[chan]['influxdb_enabled']        = int(params[chan]['influxdb_enabled'])
            
    params['influxdb']['port']              = int(params['influxdb']['port'])    
    params["mqtt"]["port"]                  = int(params["mqtt"]["port"])   
    
    return params

# end def 


"""
Common Generic Logger setup, used by master loop for console and common file.
"""
def advance_logger(filename, console_level = 1, file_level = 1):


    my_logger = logging.getLogger(__name__)
    my_logger.setLevel(logging.INFO)

    # Create a formatter
    #cf = logging.Formatter('%(asctime)s - %(levelname)s - %(processName)s - %(message)s')
    cf = logging.Formatter('%(levelname)s - %(processName)s - %(message)s')
    ch = logging.StreamHandler()
    
    # Set file log level 
    if console_level == 0:
        ch.setLevel(logging.DEBUG)
        cl = "debug"

    elif console_level == 1:
        ch.setLevel(logging.INFO)
        cl = "info"
        
    elif console_level == 2:
        ch.setLevel(logging.WARNING)
        cl = "warning"
        
    elif console_level == 3:
        ch.setLevel(logging.ERROR)
        cl = "error"
      
    elif console_level == 4:
        ch.setLevel(logging.CRITICAL)
        cl = "critical"
        
    else:
        ch.setLevel(logging.INFO)  # Default log level if undefined
        cl = "info"

    # Create a formatter
    #ff = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ff = logging.Formatter('%(levelname)s - %(message)s')
    fh = logging.FileHandler(filename)

    # Set file log level 
    if file_level == 0:
        fh.setLevel(logging.DEBUG)
        fl = "debug"
        
    elif file_level == 1:
        fh.setLevel(logging.INFO)
        fl = "info"
        
    elif file_level == 2:
        fh.setLevel(logging.WARNING)
        fl = "warning"
        
    elif file_level == 3:
        fh.setLevel(logging.ERROR)
        fl = "error"
        
    elif file_level == 4:
        fh.setLevel(logging.CRITICAL)
        fl = "critical"
        
    else:
        fh.setLevel(logging.INFO)  # Default log level if undefined
        fl = "info"


    ch.setFormatter(cf)
    my_logger.addHandler(ch)
    
    fh.setFormatter(ff)
    my_logger.addHandler(fh)
    
    return my_logger, cl, fl

# end advance_logger



# Console print
def pp_json(json_thing, logger, sort=True, indents=4):
    
    #print(json.dumps(json_thing, sort_keys=sort, indent=indents))

    if type(json_thing) is str:
        logger.debug(json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))

    else:
        logger.debug(json.dumps(json_thing, sort_keys=sort, indent=indents))

    return None

# end pp_json



def basic_logger(filename, loglevel):

    basic_formatter = '%(asctime)s - %(levelname)s - %(processName)s - %(message)s'

    my_logger = logging.basicConfig(filename=filename, 
        filemode = 'w', 
        encoding = 'utf-8',
        level    = logging.INFO,
        format   = basic_formatter)

    # create logger
    my_logger = logging.getLogger(__name__)
        
    # create console handler and set level to debug
    my_logger_shandler = logging.StreamHandler()
    my_logger.addHandler(my_logger_shandler)

    if loglevel == 0:
        my_logger.setLevel(logging.DEBUG)
        my_logger.info('DEBUG LEVEL Activated')

    elif loglevel == 1:
        my_logger.setLevel(logging.INFO)
        my_logger.info('INFO LEVEL Activated')
        
    elif loglevel == 2:
        my_logger.setLevel(logging.WARNING)
        my_logger.info('WARNING LEVEL Activated')

    elif loglevel == 3:
        my_logger.setLevel(logging.ERROR)
        my_logger.info('ERROR LEVEL Activated')

    elif loglevel == 4:
        my_logger.setLevel(logging.CRITICAL)
        my_logger.info('CRITICAL LEVEL Activated')

    #end if
    
    return my_logger

# end b_logger