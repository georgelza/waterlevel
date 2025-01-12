########################################################################################################################
#
#
#  	Project     	: 	Water Tank Level Reader and Booster Pressure Reader
#
#   File            :   level.py
#
#	By              :   George Leonard ( georgelza@gmail.com )
#
#   Created     	:   28 Dec 2024
#
#   Notes       	:   https://github.com/adafruit/Adafruit_CircuitPython_MCP3xxx/#mcp3004-single-ended
#                   :   https://learn.adafruit.com/raspberry-pi-analog-to-digital-converters/mcp3008
#
#                   :   https://www.youtube.com/watch?v=eQaBFLbYMNY
#
#                   :   influxdb
#                   :   CREATE DATABASE watertak_levels
#                   :   CREATE USER waterlevel WITH PASSWORD 'password' WITH ALL PRIVILEGES
#
#                   :   cp waterlevels_and_pressure.service /lib/systemd/system
#
#                   :    sudo systemctl enable waterlevels_and_pressure.service
#                   :    sudo systemctl start waterlevels_and_pressure.service
#                   :    sudo systemctl status waterlevels_and_pressure.service
#
#                   :    sudo systemctl daemon-reload
#
#######################################################################################################################
__author__      = "George Leonard"
__email__       = "georgelza@gmail.com"
__version__     = "0.0.1"
__copyright__   = "Copyright 2024, George Leonard"


#Libraries
import copy
import sys, os
import multiprocessing
import measure
import adc
import db
import mqtt
from apputils import * 


########################################################################################################################
#
#   Ok Lets start things
#
########################################################################################################################


def main_initiator(config_params):

    logfile            = config_params["common"]["logfile"]
    console_loglevel   = config_params["common"]["console_loglevel"]
    file_loglevel      = config_params["common"]["file_loglevel"]

    # Create new Main Process specific logger's
    # main_logger = basic_logger(logfile, loglevel)
    logger, fl, cl = advance_logger(logfile, console_loglevel, file_loglevel)
    
    logger.info("")
    logger.info('{time}, level.main_initiator - Starting... '.format(
        time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
    ))
    
    logger.info("{time}, measure.main_initiator - logfile: {logfile}, File Level: {fl}, Console Level: {cl}".format(
        time        = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        logfile     = logfile,
        fl          = fl,
        cl          = cl
    ))
    
  
    if console_loglevel < 3:

        logger.info(' ')
        logger.info(' ####################################### ')
        logger.info(' #                                     # ')
        logger.info(' #          Water Tank Levels          # ')
        logger.info(' #         & Booster Pressure          # ')
        logger.info(' #                                     # ')
        logger.info(' #          by: George Leonard         # ')
        logger.info(' #          georgelza@gmail.com        # ')
        logger.info(' #                                     # ')
        logger.info(' #       {time}    # '.format(
            time=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        ))
        logger.info(' #                                     # ')
        logger.info(' ####################################### ')
        logger.info(' ')
        
        pp_json(config_params, logger)
   
    
    # Initialize MCP3008
    try:
                
        mcp = adc.initialize(logger)
        
    except Exception as err:

        logger.critical('{time}, Something went wrong (ADC Configure) / Error... {err}'.format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            err  = err
        ))
        
        sys.exit(1)
        
    finally:
        logger.debug('{time}, ADC Enabled... '.format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        ))
        
    # end try
    
      
    ## Assemble multiprocess sets...
    try:     

        processes   = []
        config      = []

        config = {
            "common":   copy.deepcopy(config_params["common"]),
            "influxdb": copy.deepcopy(config_params["influxdb"]),
            "mqtt":     copy.deepcopy(config_params["mqtt"]),
        }
        
        
        if "0" in config["common"]["channels"]:
            
            chanlbl          = "chan0"
            chan0            = adc.createChan(mcp, 0, logger)
            config["sensor"] = config_params[chanlbl]

            logger.debug("{time}, Adding {chanLabel} Process: ".format(
                time      = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                chanLabel = chanlbl 
            ))

            # Create a process for each site
            p = multiprocessing.Process(target=measure.chan_reader, name=chanlbl, args=(chan0, config))
            processes.append(p)
            p.start()
    
        # end id
        
        if "1" in config["common"]["channels"]:
            
            chanlbl          = "chan1"
            chan1            = adc.createChan(mcp, 1, logger)
            config["sensor"] = config_params[chanlbl]

            logger.debug("{time}, Adding {chanLabel} Process: ".format(
                time      = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                chanLabel = chanlbl 
            ))

            # Create a process for each site
            p = multiprocessing.Process(target=measure.chan_reader, name=chanlbl, args=(chan1, config))
            p.start()
            processes.append(p)
    
        # end id

        if "2" in config["common"]["channels"]:
            
            chanlbl          = "chan2"
            chan2            = adc.createChan(mcp, 2, logger)
            config["sensor"] = config_params[chanlbl]

            logger.debug("{time}, Adding {chanLabel} Process: ".format(
                time      = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                chanLabel = chanlbl 
            ))

            # Create a process for each site
            p = multiprocessing.Process(target=measure.chan_reader, name=chanlbl, args=(chan2, config))
            p.start()
            processes.append(p)
    
        # end id
        
        if "3" in config["common"]["channels"]:
            
            chanlbl          = "chan3"
            chan3            = adc.createChan(mcp, 3, logger)
            config["sensor"] = config_params[chanlbl]

            logger.debug("{time}, Adding {chanLabel} Process: ".format(
                time      = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                chanLabel = chanlbl 
            ))

            # Create a process for each site
            p = multiprocessing.Process(target=measure.chan_reader, name=chanlbl, args=(chan3, config))
            p.start()
            processes.append(p)
    
        # end id

        if "4" in config["common"]["channels"]:
            
            chanlbl          = "chan4"
            chan4            = adc.createChan(mcp, 4, logger)
            config["sensor"] = config_params[chanlbl]

            logger.debug("{time}, Adding {chanLabel} Process: ".format(
                time      = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                chanLabel = chanlbl 
            ))

            # Create a process for each site
            p = multiprocessing.Process(target=measure.chan_reader, name=chanlbl, args=(chan4, config))
            p.start()
            processes.append(p)
    
        # end id
        
        if "5" in config["common"]["channels"]:
            
            chanlbl          = "chan5"
            chan5            = adc.createChan(mcp, 5, logger)
            config["sensor"] = config_params[chanlbl]

            logger.debug("{time}, Adding {chanLabel} Process: ".format(
                time      = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                chanLabel = chanlbl 
            ))

            # Create a process for each site
            p = multiprocessing.Process(target=measure.chan_reader, name=chanlbl, args=(chan5, config))
            p.start()
            processes.append(p)
    
        # end id
        
        if "6" in config["common"]["channels"]:
            
            chanlbl          = "chan6"
            chan6            = adc.createChan(mcp, 6, logger)
            config["sensor"] = config_params[chanlbl]

            logger.debug("{time}, Adding {chanLabel} Process: ".format(
                time      = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                chanLabel = chanlbl 
            ))

            # Create a process for each site
            p = multiprocessing.Process(target=measure.chan_reader, name=chanlbl, args=(chan6, config))
            p.start()
            processes.append(p)
    
        # end id
        
        if "7" in config["common"]["channels"]:
            
            chanlbl          = "chan7"
            chan7            = adc.createChan(mcp, 7, logger)
            config["sensor"] = config_params[chanlbl]

            logger.debug("{time}, Adding {chanLabel} Process: ".format(
                time      = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                chanLabel = chanlbl 
            ))

            # Create a process for each site
            p = multiprocessing.Process(target=measure.chan_reader, name=chanlbl, args=(chan7, config))
            p.start()
            processes.append(p)
    
        # end id
                        
        if config['common']['booster'] == "1":
            
            chanlbl = "booster"
            
            if config[chanlbl]["channel"] == 0:
                chanbooster = adc.createChan(mcp, 0, logger)
                
            elif config[chanlbl]["channel"] == 1:
                chanbooster = adc.createChan(mcp, 1, logger)
                
            elif config[chanlbl]["channel"] == 2:
                chanbooster = adc.createChan(mcp, 2, logger)
                
            elif config[chanlbl]["channel"] == 3:
                chanbooster = adc.createChan(mcp, 3, logger)
                
            elif config[chanlbl]["channel"] == 4:
                chanbooster = adc.createChan(mcp, 4, logger)
                
            elif config[chanlbl]["channel"] == 5:
                chanbooster = adc.createChan(mcp, 5, logger)
                
            elif config[chanlbl]["channel"] == 6:
                chanbooster = adc.createChan(mcp, 6, logger)
                
            elif config[chanlbl]["channel"] == 7:
                chanbooster = adc.createChan(mcp, 7, logger)
                
            # end if                 

            config["sensor"] = config_params["booster"]


            logger.debug("{time}, Adding {chanLabel} Process: ".format(
                time      = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                chanLabel = chanlbl 
            ))

            # Create a process for each site
            p = multiprocessing.Process(target=measure.chan_reader, name=chanlbl, args=(chanbooster, config))
            p.start()          
            processes.append(p)
              
        # end if
        
        
        for p in processes:
            p.join()
            
        # end for

    
    except Exception as err:

        logger.critical('{time}, Something went wrong / Error... {err}'.format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            err  = err
        ))
  
    except KeyboardInterrupt:
        # Reset by pressing CTRL + C

        logger.info('{time}, Reset by pressing CTRL + C...'.format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
        ))

    finally:

        logger.info("KeyboardInterrupt detected! Terminating all processes...")
        logger.info("")
        
        # Terminate all running processes if Ctrl+C is pressed
        for p in processes:
            p.terminate()
            p.join()

        logger.info("All processes terminated. Exiting gracefully...")
        
        logger.info('{time}, Closing MQTT Connection... '.format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        ))
        
            
        logger.info('{time}, Goodbye... '.format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        ))

        sys.stdout.flush()
        sys.exit(-1)

    # end try
#end main_initiator


if __name__ == '__main__':

    configfile      = os.getenv('CONFIGFILE')
    config_params   = get_config_params(configfile)

    main_initiator(config_params)                      

#end if
