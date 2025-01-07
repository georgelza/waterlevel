########################################################################################################################
#
#
#  	Project     	: 	Water Tank Level Reader and Booster Pressure Reader
#
#   File            :   adc.py
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
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from datetime import datetime


def initialize(main_logger):
    
    # create the spi bus
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

    # # create the cs (chip select)
    cs = digitalio.DigitalInOut(board.D5)

    # create the mcp object
    mcp = MCP.MCP3008(spi, cs)
    
    #mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(HW_SPI_PORT, HW_SPI_DEV)) 
    
    main_logger.debug("{time}, adc.initialize - ADC MCP3008 initialized: ".format(
        time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
    ))

    return mcp
            
# end initialize


def createChan(mcp, channel, main_logger):
    
    if channel == 0:
        c = AnalogIn(mcp, MCP.P0)
        
    elif channel == 1:
        c = AnalogIn(mcp, MCP.P1)
        
    elif channel == 2:
        c = AnalogIn(mcp, MCP.P2)
        
    elif channel == 3:
        c = AnalogIn(mcp, MCP.P3)
        
    elif channel == 4:
        c = AnalogIn(mcp, MCP.P4)
        
    elif channel == 5:
        c = AnalogIn(mcp, MCP.P5)
        
    elif channel == 6:
        c = AnalogIn(mcp, MCP.P6)
        
    elif channel == 7:
        c = AnalogIn(mcp, MCP.P7)
        
    main_logger.debug("{time}, adc.createChan - Channel {chan} initialized: ".format(
        time    = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        chan    = channel
    ))
    
    return c
        

# end createChan