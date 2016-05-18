import serial
import time
from datetime import datetime

ser = serial.Serial('/dev/ttyACM0',57600)

while True:
    data = ser.readline()
    print data
    values = data.split(',')
    if (int(values[1])>0) or (int(values[2])>0):
        file = open("/data/"+str(int(time.time()))+" - "+values[0]+".dat",'w')
        file.write(str(datetime.now()))
        for v in values:
            file.write(str(v)+'\n')
        file.close()
