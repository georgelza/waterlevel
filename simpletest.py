


# https://github.com/adafruit/Adafruit_Python_MCP3008/blob/master/examples/simpletest.py
#
# Simple example of reading the MCP3008 analog input channels and printing
# them all out.
# Author: Tony DiCola
# License: Public Domain

from time import sleep          # Import sleep from time
import Adafruit_GPIO.SPI as SPI # Import Adafruit GPIO_SPI Module
import Adafruit_MCP3008         # Import Adafruit_MCP3008
import time

# We can either use Software SPI or Hardware SPI. For software SPI we will
# use regular GPIO pins. Hardware SPI uses the SPI pins on the Raspberry PI
# Set the following variable to either HW or SW for Hardware SPI and Software
# SPI respectivly.
SPI_TYPE = 'HW'
dly = .5         # Delay of 1000ms (1 second)

# Software SPI Configuration
CLK     = 18    # Set the Serial Clock pin
MISO    = 23    # Set the Master Input/Slave Output pin
MOSI    = 24    # Set the Master Output/Slave Input pin
CS      = 25    # Set the Slave Select

# Hardware SPI Configuration
HW_SPI_PORT = 0 # Set the SPI Port. Raspi has two.
HW_SPI_DEV  = 0 # Set the SPI Device

# Instantiate the mcp class from Adafruit_MCP3008 module and set it to 'mcp'. 
if (SPI_TYPE == 'HW'):
    # Use this for Hardware SPI
    mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(HW_SPI_PORT, HW_SPI_DEV))
    
elif (SPI_TYPE == 'SW'):
    # Use this for Software SPI
    mcp = Adafruit_MCP3008.MCP3008(clk = CLK, cs = CS, miso = MISO, mosi = MOSI)


print('Reading MCP3008 values, press Ctrl-C to quit...')
# Print nice channel column headers.
print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*range(8)))
print('-' * 57)
# Main program loop.
while True:
    # Read all the ADC channel values in a list.
    values = [0]*8
    for i in range(8):
        # The read_adc function will get the value of the specified channel (0-7).
        values[i] = mcp.read_adc(i)
    # Print the ADC values.
    print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*values))
    # Pause for half a second.
    time.sleep(0.5)
    