import time
import serial
import random
import ast

class Veronte:

    def __init__(self,Veronteport,Verontebitrate,modeselect):

        self.modeselect = modeselect
        self.mode = {0:'GCS',1:'FUI'}

        self.Veronteport = Veronteport
        self.Verontebitrate = Verontebitrate
        
        self.VeronteSerial =  serial.Serial(self.Veronteport,self.Verontebitrate,timeout = 1) # connect to the LoRa Modules 's serial port
        
        self.Data = ''
        self.packet = {}
        self.dataDictionary = {'altitude_AGL':0,'altitude_AGL_set':0,'altitude_ABS':0,'altitude_AGL':0,'heading':0,'compass':0,'attitude_pitch':0,'attitude_roll':0,'vertical_speed_KTS':0,
                               'airspeed_KTS':0,'OAT':0,'altitude_ABS':0}
        
        print("Veronte Init")
        
    def packetStruct(self):
        
        try:
                self.dataDictionary = self.readData()
                self.packet = {key : round(self.dataDictionary[key],2) for key in self.dataDictionary}
                print(self.packet)
        except:
                self.packet = {'altitude_AGL':round(random.uniform(0,100),2),'altitude_AGL_set':round(random.uniform(0,100),2),'altitude_ABS':round(random.uniform(0,100),2),'altitude_AGL':round(random.uniform(0,100),2),'heading':round(random.uniform(0,100),2),'compass':round(random.uniform(0,100),2),'attitude_pitch':round(random.uniform(0,100),2),'attitude_roll':round(random.uniform(0,100),2),'vertical_speed_KTS':round(random.uniform(0,100),2),
                       'airspeed_KTS':round(random.uniform(0,100),2),'OAT':round(random.uniform(0,100),2),"latitude":'40d26a46q','longitude':'79d58a56q',"flight_time":(str(random.randint(0,59))+':'+str(random.randint(0,59)))}
        
        #print(self.packet)
        return self.packet
        
    def readData(self):
            
        data = self.VeronteSerial.readline()
        
        data = data.decode("utf-8").replace('\r','')
        data = data.replace('\n','')
        
        if len(data) > 2:
                
                data = ast.literal_eval(data)
                self.data = data
        
                return self.data

if __name__ == "__main__":
    
    VeronteComport = '/dev/ttyS0' #Veronte Serial Port
    Serialbitrate = 115200

    veronte = Veronte(VeronteComport,Serialbitrate,'FUI')
    
    while True:
        
        veronte.packetStruct()
        
        print(veronte.packet)
        print("\n")
