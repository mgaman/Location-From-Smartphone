# Location-From-Smartphone
A cheap and simple way to transfer location/time data from your phone to a Raspberry Pi.

For example you're out in the wild with your Raspberry Pi and camera module taking wonderful shots and you want accurate time and location data to be saved in the JPEG file. Sadly your Raspberry Pi has no GPS module or Real Time Clock, but your phone does!

This method transfers the info, via Bluetooth, from the phone to the Pi as standard NMEA sentences. A simple Python script parses the NMEA data and generates a short script.

This script has 2 functions:
1. Encodes the location data as a series of environment variables that can be used by other scripts
2. Initialises the RPi date to the current value.
3. Normally this only needs to be done once but needs repeating if changing location.
## Smartphone Side
I have an Android phone and use the app **ShareGPS** by Jillybunch. Doubtful there a many others on both Android and iOS. Please send me feedback with with ones that work for you.
## Raspberry Pi without built in Bluetooth
If your RPi does not have built-in bluetooth you'll have to connect a stand alone BT to Serial device such as an HC-06 slave module and connect it to the UART pins of the RPi. When the device is paired with the phone the data will be available from the /dev/ttyS0 device.
## Raspberry Pi with built-in Bluetooth.
Follow the procedure in https://pirobotblog.wordpress.com/2016/12/22/serial-bluetooth-communication/ to set up a daemon that listens for incomming Bluetooth serial data. When available the data becomes available on the /dev/rfcomm0 device.
## Sample Output
This is sample output from the Python script. I have formated the location data into the format described in the **raspistill** documentation.
```
#$GPRMC,092750.000,A,5321.6802,N,00630.3372,W,0.02,31.66,280511,,,A*43
export GPSLAT="GPS.GPSLatitude=53/1,21/1,4081/100"
export GPSLONG="GPS.GPSLongitude=6/1,30/1,2023/100"
export GPSNS="GPS.GPSLatitudeRef=N"
export GPSEW="GPS.GPSLongitudeRef=W"
sudo date +%D -s  "5/28/2011"
export TZ=GMT
sudo date +%T -s  "9:27:50"
```
Save the output in a file e.g. set.txt then **source set.txt** will execute the file, setup the environment variables and initialise the date/time.
## Using the environment valiables
The following script takes a **raspistill** picture and encodes the location data in the EXIF metadata
```
#!/bin/bash
ROT=90
QUAL=75
raspistill -v -rot $ROT -q $QUAL -x $GPSEW -x $GPSNS -x $GPSLAT -x $GPSLONG -o $$.jpg
```
## Methodology
1. To parse the NMEA sentences I could have used any of a number of libraries already published. However I chose to do it all in the script so you can see where the data is coming from.
2. The NMEA sentence RMC contains all the information we need, location, date and time. The first instance indicating reliable information is processed and the script exited.
3. The script is liberally commented and, I hope, complete and clear. Please contact me if not.
## Date initialisation
1. If your RPi is connected to the internet it probably has a task running that updates time setting, therefore executing the **date** command will have no effect.
2. Which method your RPi uses depends on the version of Linux you're using. I have Stretch raspbian which uses **systemd-timesync** therefore I have to stop it with **sudo systemctl stop systemd-timesyncd** before I can execute the **date** command.
3. If your system is using NTP then do **sudo /etc/init.d/ntp stop**.
4. Please let me know of other methods in use.
 
