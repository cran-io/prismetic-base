import serial
import time
from datetime import datetime

ser = serial.Serial('/dev/ttyACM0',57600,timeout=1s)

while True:
        income = ser.readline()
        if '\n' in income:
                data = income.split('\n')
                values = data[0].split(',')
                id=int(values[0])
                peopleIn=int(values[1])
                peopleOut=int(values[2])
                data=[id,peopleIn,peopleOut]
                print 'New data:' + str(data)
                if (peopleIn>0) or (peopleOut>0):
                        file = open("/data/"+str(int(time.time()))+" - "+values[0]+".dat",'w')
                        file.write(str(datetime.now())+'\n')
                        for d in data:
                                file.write(str(d)+'\n')
                        file.close()

