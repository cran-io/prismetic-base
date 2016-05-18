import serial
import time
from datetime import datetime

ser = serial.Serial('/dev/ttyACM0',57600)

while True:
        data = ser.readline()
        print data
        values = data.split(',')
        id=int(values[0])
        peopleIn=int(values[1])
        buffer=values[2]
        buffer2=buffer.split('\r')
        peopleOut=int(buffer2[0])
        data=[id,peopleIn,peopleOut]
        if (peopleIn>0) or (peopleOut>0):
                file = open("/data/"+str(int(time.time()))+" - "+values[0]+".dat",'w')
                file.write(str(datetime.now()))
                for d in data:
                        file.write(str(d))
                file.close()

