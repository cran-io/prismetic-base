
import urllib2
import requests
import json
import glob
import random
import os
import fnmatch
import time
from uuid import getnode as get_mac



##Variables to post server
idTable={}
deviceIdTable={}
dataPath="/data"
filename=dataPath+"/Syncfile.sync"
deviceIdfilename=dataPath+"/Device_id.sync"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
deviceId = ''
#apiurl='http://prismetic.cran.io:8080/api/'
apiurl='http://prismetic.cran.io:8080/api/'
urlBase='http://prismetic.cran.io:8080/api/devices/'

def setTime():
    url = apiurl+'time'
    try:
        r = requests.get(url)
        data=r.json()['time']
        print data
        print ("La hora se cambio")
    except:
        print("Post error")
        print("Retrying request")
        time.sleep(2)
        setTime()
    os.system("sudo timedatectl set-time '" +data+ "'")
    

def loadDeviceId():
    mac = str(get_mac())
    global deviceId
    global deviceIdTable
    newlines=[]
    try:
        deviceId=deviceIdTable[mac]
    except:
        try:
            with open(deviceIdfilename) as f:
                print("lineread")
                lineread = f.readlines()
                print lineread
                print lineread[0].split(':')[1]
            print("ESCRBI LA CONCHA DE LA LORA")
            deviceIdTable[mac]=lineread[0].split(':')[1]
            print(deviceIdTable[mac])
            print("ESCRIBI")
            
        except :
            deviceId=str(request_DeviceId(mac))
            try:
                os.remove(deviceIdfilename)
            except:
                print("No hace falta borrarlo, el archivo no existe")
            print(deviceId)
            idfile=open(deviceIdfilename,'wb+')
            newlines.append(mac)
            newlines.append(":")
            newlines.append(deviceId)
            idfile.writelines(newlines)
            idfile.close()


def request_DeviceId(idname):
    url = urlBase
    jasonPost=json.dumps({"model":str(idname) ,"mac":str(idname), "active": True})
    print(jasonPost)
    try:
        r = requests.post(url, data=jasonPost,headers=headers)
        data=r.json()['_id']
        print data
    except:
        print("Post error")
        print("Retrying request")
        time.sleep(2)
        request_DeviceId(idname)
    return data


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
        b=(buffer[len(buffer)-1].index('.dat'))
        ids.append(buffer[len(buffer)-1][a:b])
    output = set()
    for x in ids:
        output.add(x)
    print(list(output))
    return(list(output))



def request_sensorid(idname):
    url = urlBase+deviceId+'/sensors/'
    print url
    jasonPost=json.dumps({"name":"Entrada principal" , "active": True})
    print(jasonPost)
    try:
        print("intentando request")
        r = requests.post(url, data=jasonPost,headers=headers)
        data=r.json()['_id']
        print ("new sensor id: "+data)
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
    b=(buffer[len(buffer)-1].index('.dat'))
    id=(buffer[len(buffer)-1][a:b])
    print("EL ID ES: "+id)
    return id

def refreshDict(uniqueIds):
    filestatus=0
    readlines=[]
    writelines=[]
    newlines=[]
    lineread=[]
    global idTable
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

    date=data.readline().split('\n')[0]
    name=data.readline().split('\n')[0]
    #data.readline().split('\n')[0]
    peoplein=data.readline().split('\n')[0]
    peopleout=data.readline().split('\n')[0]
    print("jasonify")
    try:
        tosend=json.dumps({"enter": peoplein,"exit":peopleout,"sentAt":date})
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

#setTime()
loadDeviceId()
while(1):
    time.sleep(1)
    postNewData()
