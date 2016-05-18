from flask import Flask
import urllib2
import requests
import json
import glob
import random
import os
import fnmatch
from datetime import datetime

app = Flask(__name__)

##Variables to post server
idTable={}
dataPath="/data"
filename=dataPath+"/Syncfile.sync"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
deviceId= '5739d8a8f5dfba02145fadc0'
urlBase='http://192.168.1.56:8080/api/devices/'




def getfilelist():
    try:
        fileList=glob.glob(dataPath+"/*.dat")
        #print("File list readed")
    except:
        print("File list error")
    return fileList

def getFilesIds(fileList):
    #print("Getting ids from list")
    ids=[]
    for i in range(0, len(fileList)):
        buffer=fileList[i].split('/')
        a=(buffer[len(buffer)-1].index('-')+2)
        b=(buffer[len(buffer)-1].index('.dat')-1)
        ids.append(buffer[len(buffer)-1][a:b])
    output = set()
    for x in ids:
        output.add(x)
    print(list(output))
    return(list(output))



def request_sensorid(idname):
    url = urlBase+deviceId+'/sensors/'
    jasonPost=json.dumps({"name":idname , "active": True})
    print(jasonPost)
    try:
        r = requests.post(url, data=jasonPost,headers=headers)
        data=r.json()['_id']
        print data
    except:
        print("Post error")
        return -1
    return data

def checkIds(uniqueIds):
    try:
        for ids in uniqueIds:
            idTable[ids]
    except KeyError:
        print("La tabla no fue cargada")
    refreshDict(uniqueIds)    

def updateFile(newlines):
    try:
        os.remove(filename)
    except:
        print("No hace falta borrarlo, el archivo no existe")
    syncIds=open(filename,'wb+')
    syncIds.writelines(newlines)
    syncIds.close()
    print("El archivo fue creado con exito")

def getIdfromname(name):

    buffer=name.split('/')
    a=(buffer[len(buffer)-1].index('-')+2)
    b=(buffer[len(buffer)-1].index('.dat')-1)
    id=(buffer[len(buffer)-1][a:b])
    return id

def refreshDict(uniqueIds):
    filestatus=0
    readlines=[]
    writelines=[]
    newlines=[]
    lineread=[]
    #print("Unique ids: " +str(uniqueIds))
    try:
        with open(filename) as f:
            print("lineread")
            lineread = f.readlines()
            
        for line in lineread:
            readlines.append(line[0:line.index(':')])

        for sensorid in uniqueIds:
            if (sensorid in readlines):
                print("Esta identificado el sensor numero: " + sensorid)
            else:
                print("No esta identificado el sensor numero: " + sensorid)
                newServerId=request_sensorid(sensorid)
                newlines.append(str(sensorid) + ":" +str(newServerId)+"\n")
        f.close()
        
    except IOError:
        for sensorid in uniqueIds:
            newServerId=request_sensorid(sensorid)
            newlines.append(str(sensorid) + ":" +str(newServerId)+"\n")
    for nline in lineread:
            idTable[nline[0:nline.index(':')]]=nline[nline.index(':')+1:(nline.index('\n'))]
    for nline in newlines:
            idTable[nline[0:nline.index(':')]]=nline[nline.index(':')+1:(nline.index('\n'))]
    
    if not newlines:
        print("No new sensors")
    else:
        print("New sensor detected")
        updateFile(lineread+newlines)

def checkNewData():
    f=checkIds(getFilesIds(getfilelist()))

def jasonfi(data):
    name=data.readline().split('\n')[0]
    date=data.readline().split('\n')[0]
    data.readline().split('\n')[0]
    peoplein=data.readline().split('\n')[0]
    peopleout=data.readline().split('\n')[0]
    print("jasonify")
    try:
        tosend=json.dumps({"enter": peoplein,"exit":peopleout,"sentAt":"fecha"})
        print(tosend)
        return tosend
    except:
        print ("Error en el json")


def postNewData():
    checkNewData()
    newDataFiles=getfilelist();
    for datafile in newDataFiles:
        try:   
            data=open(str(datafile),'r')
            jsontosend=jasonfi(data)
            data.close()
            print("gettinidfrommname")
            print(getIdfromname(datafile))
            url = urlBase+deviceId+'/sensors/'+ idTable[getIdfromname(datafile)] +'/sensors_data'
            print("Arme la url")
            try:
                r = requests.post(url, data=jsontosend,headers=headers)
                print(r)
            except:
                print('Error')
            
            os.remove(str(datafile))
        except:
            print("Algun archivo tiene un error")
            return "Error"
    

@app.route('/')
def hello_world():
    output = 'Prismetic Base Online\n'
    for root, dirnames, filenames in os.walk('/data/logs'):
        for logfile in fnmatch.filter(filenames, '*.log'):
            output += '##############################\n'
            output += os.path.join(root, logfile) + '\n'
            output += '##############################\n'
            f = open(os.path.join(root, logfile), 'r')
            log = f.read()
            f.close()
            output += log + '\n'
	return output

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80)

while(1):
	time.sleep(1)
	postNewData()
