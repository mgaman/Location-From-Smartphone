#!/usr/bin/python
import serial
import re
# For insight into NMEA conventions, go to
#   http://www.catb.org/gpsd/NMEA.html#_nmea_encoding_conventions
# RMC gives location, active or not, time and date
loc = '$GPRMC,092750.000,A,5321.6802,N,00630.3372,W,0.02,31.66,280511,,,A*43'
# When testing set final to False and process the string 'loc'
# FOr production set final to True and select the appropriate portname
#portname = '/dev/ttyS0'
portname = '/dev/rfcomm0'
final = True

def checksum(sentence):

    """ Remove any newlines """
    if re.search("\n$", sentence):
        sentence = sentence[:-1]

    nmeadata,cksum = re.split('\*', sentence)

    calc_cksum = 0
    for s in nmeadata:
        calc_cksum ^= ord(s)

    """ Return the checksum from
        sentence, and the calculated checksum
    """
    return '0x'+cksum,hex(calc_cksum)

def processDate(date):
        day = int(date)/10000
        month = (int(date) % 10000) / 100
        year = int(date) % 100
	print('sudo date +%%D -s  "%d/%d/%d"' % (month,day,year+2000))

def processTime(time):
	# drop partial secs
	ts = time.split('.')
	hour = int(ts[0])/10000
	minute = (int(ts[0]) % 10000) / 100
	second = int(ts[0]) % 100
	print('export TZ=GMT')
	print('sudo date +%%T -s  "%d:%d:%d"' % (hour,minute,second))

def processHemi(lat,long):
	# export hemispheres
	print ('export GPSNS="GPS.GPSLatitudeRef=%s"' % lat)
	print ('export GPSEW="GPS.GPSLongitudeRef=%s"' % long)

def processLatLong(lat,long):
	# process latitude
	latp = lat.split('.')
        latdeg = int(latp[0])/100
        latmin = int(latp[0])%100
        # decoding minutes depends on length of field
        # multiply secs by 100 then divide by 100 for better accuracy
        latsec = (float(latp[1])/10**len(latp[1]))*6000
        print ('export GPSLAT="GPS.GPSLatitude=%d/1,%d/1,%d/100"' % (latdeg,latmin,latsec))
        # process longitude
        longp = long.split('.')
        longdeg = int(longp[0])/100
        longmin = int(longp[0])%100
        # decoding minutes depends on length of field
        # multiply secs by 100 then divide by 100 for better accuracy
        longsec = (float(longp[1])/10**len(longp[1]))*6000
        print ('export GPSLONG="GPS.GPSLongitude=%d/1,%d/1,%d/100"' % (longdeg,longmin,longsec))

def ParseRMC(s):
        parts = s.split(',')
        if parts[2] == 'A':  # good fix
                processLatLong(parts[3],parts[5])
                processHemi(parts[4],parts[6])
		# do date before time as setting date zeroes time
		processDate(parts[9])
		processTime(parts[1])
                return True
        else:
                return False

if final:
	ser = serial.Serial(portname,9600, timeout=10)
done = False
while (not done):
	if final:
		loc = ser.readline();
	print ('#%s' % loc)
	# The first letter if a sentence is always $
	# The next 2 letters are called Talker ID and reflect the source of information e.g.
	# GP means the data comes from a GPS (American) source, GL from Glosnass (Russian)
	# As we dont care, just ignore and look at the 4th->6th characters(Sentence)  
        if len(loc) > 6 and loc[0] == '$' and loc[3:6] == 'RMC':
		# be pedantic and check the checksum
		cksum,calc_cksum = checksum(loc[1:])  # $ not part of checksum
		if int(cksum,16) == int(calc_cksum,16):
                	done = ParseRMC(loc)
		else:
			print "Checksums are %s and %s" % (cksum,calc_cksum)
print '#finished!'
