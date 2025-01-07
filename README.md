# Watertank level and Booster Pump Pressure

This is a small project that measures / calculates water level based on value returned by a transducer.
additionally it also measures the booster line pressure after our DAB water booster increased the water pressure in line into the house.

We define 3 transducer_types, although we only actually have 2...

1. basic water level transducer_type located at the bottom of a tank, screwed into the outbound piping = 0  (0 - 5bar)
2. basic water level transducer_type located at the bottom of a tank, hung from the top = 1 (0 - 5 bar)
3. basic transducer measuring water line pressure, screwed into the outboung pipine after pump = 2 (0 - 10 bar)

The values are messured via pressure transducers => List Ali Express links

My tanks are 4750L tanks that stand 2.5M heigh as such I'm using a 0-0.5 Bar sensor, 5V input and 3.3 V output sensor for water level/volume.

For Water volume, you can use either of the below sensors, a bottom screw in or a drop in sensor/transducer.

1. To measure the water volume in a tank use level.py

As the Raspberry Pi platform (Raspberry Pi 3B -> 5B and raspberry Pi Zero W and Zero 2 W) does not handle Analog signals a ADC MCP3008 chip was used, connected via SPI interface.

To configure what channel to read, where to publish on MQTT broker and where to save the data into our timeseries database using influxdb, all configured via the *_config.cfg file.

To make the service auto start when Pi is rebooted copy the *.service file to /lib/systemd/system folder and follow the steps at the top of level.py

See below links.

See images folder for diagrams how to wire things up...

As this is the only app that will be running on the pi... I install the python libraries as root... using the following command.


## Deploying...

mkdir -p /app/waterlevels
copy files to /app/waterlevels
cd /app/waterlevels
pip3 install -r requirements --break-system-packages


## Example 1

https://randomnerdtutorials.com/raspberry-pi-analog-inputs-python-mcp3008/#:~:text=The%20MCP3008%20chip%20is%20a,to%20connect%20to%20analog%20devices.


## Example 2

https://github.com/adafruit/Adafruit_CircuitPython_MCP3xxx/

Reading Potentiometer 

### enable spi 

To be able to talk to the MCP3008 we need to enable SPI protocol on the the Raspberry Pi.
Execute the following steps.

raspi-config
interfaces
spi

### allow non root to access spi 

https://forums.raspberrypi.com/viewtopic.php?t=336314


# Misc Notes

## Raspberry Schematics and mechanical drawings.

https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#schematics-and-mechanical-drawings


## Measuring Resolution

MCP3008 = 1024 bits (10bit)

Tank Depth 2.4m => 240cm

240/1024=0.24cm resolution per reading

## MCP3008 (10bit)

VDD => 2.5 -> 5.5v

https://randomnerdtutorials.com/raspberry-pi-analog-inputs-python-mcp3008/#:~:text=The%20MCP3008%20chip%20is%20a,to%20connect%20to%20analog%20devices.

https://components101.com/ics/mcp3008-adc-pinout-equivalent-datasheet

https://www.adafruit.com/product/856


### ADS1015 (12bit)/ADS1115 (16bit) with ESP8266/ESP32 and Raspberry Pi Pico

https://www.youtube.com/watch?v=VQ2S1Jvpmio


### ADS1115 (16bit)

https://www.youtube.com/watch?v=oda_jsSYqR4


### Other examples

https://github.com/leon-anavi/rpi-examples/tree/master/MCP3002/python

