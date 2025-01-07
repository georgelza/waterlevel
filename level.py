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


    # Create new Main Process specific logger's
    main_logger = basic_logger(config_params["common"]["logfile"], config_params["common"]["loglevel"])
    
    main_logger.debug("{time}, level.main_initiator - Entered main_initiator: ".format(
        time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
    ))

    main_logger.info("")
    main_logger.info('{time}, level.main_initiator - Starting... '.format(
        time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
    ))
    
        
    if config_params["common"]["loglevel"] < 3:

        main_logger.info(' ')
        main_logger.info(' ####################################### ')
        main_logger.info(' #                                     # ')
        main_logger.info(' #          Water Tank Levels          # ')
        main_logger.info(' #         And Booster Pressure        # ')
        main_logger.info(' #                                     # ')
        main_logger.info(' #          by: George Leonard         # ')
        main_logger.info(' #          georgelza@gmail.com        # ')
        main_logger.info(' #                                     # ')
        main_logger.info(' #       {time}    # '.format(
            time=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        ))
        main_logger.info(' #                                     # ')
        main_logger.info(' ####################################### ')
        main_logger.info(' ')
        
        pp_json(config_params, main_logger)

    
    
    # Initialize InfluxDB Connection
    if config_params["influxdb"]["enabled"] == 1:
        try:

            influx_client = db.connect(config_params, main_logger)
            
        except Exception as err:

            main_logger.critical('{time}, Something went wrong (InfluxDB Connection)) / Error... {err}'.format(
                time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                err  = err
            ))
            
            os.exit(1)
                    
        # end try
    else:
        main_logger.debug('{time}, InfluxDB Disabled... '.format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        ))
        influx_client = None
    
    # end if
    
    
    # Initialize MQTT Broker Connection
    if config_params["mqtt"]["enabled"] == 1:
        try:

            mqtt_client = mqtt.connect(config_params, main_logger)
            
        except Exception as err:

            main_logger.critical('{time}, Something went wrong (MQTT Connection) / Error... {err}'.format(
                time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                err  = err
            ))

            main_logger.critical('{time}, MQTT Disconnect... '.format(
                time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            ))
            
            os.exit(1)

        # end try
    else:
        main_logger.debug('{time}, MQTT Disabled... '.format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        ))
        mqtt_client = None
            
    # end if
    
    
    # Initialize MCP3008
    try:
                
        mcp = adc.initialize(main_logger)
        
    except Exception as err:

        main_logger.critical('{time}, Something went wrong (ADC Configure) / Error... {err}'.format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            err  = err
        ))
        
        mqtt.close(mqtt_client, main_logger)
        os.exit(1)
        
    finally:
        main_logger.debug('{time}, ADC Enabled... '.format(
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
            chan             = adc.createChan(mcp, 0, main_logger)
            config["sensor"] = config_params[chanlbl]

            main_logger.debug("{time}, Adding {chanLabel} Process: ".format(
                time      = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                chanLabel = chanlbl 
            ))

            # Create a process for each site
            p = multiprocessing.Process(target=measure.chan_reader, name=chanlbl, args=(chan, config, mqtt_client, influx_client))
            p.start()
            processes.append(p)
    
        # end id
        
        if "1" in config["common"]["channels"]:
            
            chanlbl          = "chan1"
            chan             = adc.createChan(mcp, 1, main_logger)
            config["sensor"] = config_params[chanlbl]

            main_logger.debug("{time}, Adding {chanLabel} Process: ".format(
                time      = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                chanLabel = chanlbl 
            ))

            # Create a process for each site
            p = multiprocessing.Process(target=measure.chan_reader, name=chanlbl, args=(chan, config, mqtt_client, influx_client))
            p.start()
            processes.append(p)
    
        # end id

        if "2" in config["common"]["channels"]:
            
            chanlbl          = "chan2"
            chan             = adc.createChan(mcp, 2, main_logger)
            config["sensor"] = config_params[chanlbl]

            main_logger.debug("{time}, Adding {chanLabel} Process: ".format(
                time      = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                chanLabel = chanlbl 
            ))

            # Create a process for each site
            p = multiprocessing.Process(target=measure.chan_reader, name=chanlbl, args=(chan, config, mqtt_client, influx_client))
            p.start()
            processes.append(p)
    
        # end id
        
        if "3" in config["common"]["channels"]:
            
            chanlbl          = "chan3"
            chan             = adc.createChan(mcp, 3, main_logger)
            config["sensor"] = config_params[chanlbl]

            main_logger.debug("{time}, Adding {chanLabel} Process: ".format(
                time      = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                chanLabel = chanlbl 
            ))

            # Create a process for each site
            p = multiprocessing.Process(target=measure.chan_reader, name=chanlbl, args=(chan, config, mqtt_client, influx_client))
            p.start()
            processes.append(p)
    
        # end id

        if "4" in config["common"]["channels"]:
            
            chanlbl          = "chan4"
            chan             = adc.createChan(mcp, 4, main_logger)
            config["sensor"] = config_params[chanlbl]

            main_logger.debug("{time}, Adding {chanLabel} Process: ".format(
                time      = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                chanLabel = chanlbl 
            ))

            # Create a process for each site
            p = multiprocessing.Process(target=measure.chan_reader, name=chanlbl, args=(chan, config, mqtt_client, influx_client))
            p.start()
            processes.append(p)
    
        # end id
        
        if "5" in config["common"]["channels"]:
            
            chanlbl          = "chan5"
            chan             = adc.createChan(mcp, 5, main_logger)
            config["sensor"] = config_params[chanlbl]

            main_logger.debug("{time}, Adding {chanLabel} Process: ".format(
                time      = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                chanLabel = chanlbl 
            ))

            # Create a process for each site
            p = multiprocessing.Process(target=measure.chan_reader, name=chanlbl, args=(chan, config, mqtt_client, influx_client))
            p.start()
            processes.append(p)
    
        # end id
        
        if "6" in config["common"]["channels"]:
            
            chanlbl          = "chan6"
            chan             = adc.createChan(mcp, 6, main_logger)
            config["sensor"] = config_params[chanlbl]

            main_logger.debug("{time}, Adding {chanLabel} Process: ".format(
                time      = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                chanLabel = chanlbl 
            ))

            # Create a process for each site
            p = multiprocessing.Process(target=measure.chan_reader, name=chanlbl, args=(chan, config, mqtt_client, influx_client))
            p.start()
            processes.append(p)
    
        # end id
        
        if "7" in config["common"]["channels"]:
            
            chanlbl          = "chan7"
            chan             = adc.createChan(mcp, 7, main_logger)
            config["sensor"] = config_params[chanlbl]

            main_logger.debug("{time}, Adding {chanLabel} Process: ".format(
                time      = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                chanLabel = chanlbl 
            ))

            # Create a process for each site
            p = multiprocessing.Process(target=measure.chan_reader, name=chanlbl, args=(chan, config, mqtt_client, influx_client))
            p.start()
            processes.append(p)
    
        # end id
                        
        if config['common']['booster'] == "1":
            
            chanlbl = "booster"
            
            if config[chanlbl]["channel"] == 0:
                chan = adc.createChan(mcp, 0, main_logger)
                
            elif config[chanlbl]["channel"] == 1:
                chan = adc.createChan(mcp, 1, main_logger)
                
            elif config[chanlbl]["channel"] == 2:
                chan = adc.createChan(mcp, 2, main_logger)
                
            elif config[chanlbl]["channel"] == 3:
                chan = adc.createChan(mcp, 3, main_logger)
                
            elif config[chanlbl]["channel"] == 4:
                chan = adc.createChan(mcp, 4, main_logger)
                
            elif config[chanlbl]["channel"] == 5:
                chan = adc.createChan(mcp, 5, main_logger)
                
            elif config[chanlbl]["channel"] == 6:
                chan = adc.createChan(mcp, 6, main_logger)
                
            elif config[chanlbl]["channel"] == 7:
                chan = adc.createChan(mcp, 7, main_logger)
                
            # end if                 

            config["sensor"] = config_params["booster"]


            main_logger.debug("{time}, Adding {chanLabel} Process: ".format(
                time      = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                chanLabel = chanlbl 
            ))

            # Create a process for each site
            p = multiprocessing.Process(target=measure.chan_reader, name=chanlbl, args=(chan, config, mqtt_client, influx_client))
            p.start()          
            processes.append(p)
              
        # end if
        
        
        for p in processes:
            p.join()
            
        # end for

    
    except Exception as err:

        main_logger.critical('{time}, Something went wrong / Error... {err}'.format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
            err  = err
        ))
  
    except KeyboardInterrupt:
        # Reset by pressing CTRL + C

        main_logger.info('{time}, Reset by pressing CTRL + C...'.format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
        ))

    finally:

        main_logger.info("KeyboardInterrupt detected! Terminating all processes...")
        main_logger.info("")
        
        # Terminate all running processes if Ctrl+C is pressed
        for p in processes:
            p.terminate()
            p.join()

        main_logger.info("All processes terminated. Exiting gracefully...")
        
        main_logger.info('{time}, Closing MQTT Connection... '.format(
            time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        ))
        
        if mqtt_client != None:
            mqtt_client.disconnect(config_params, main_logger)
            
        main_logger.info('{time}, Goodbye... '.format(
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
