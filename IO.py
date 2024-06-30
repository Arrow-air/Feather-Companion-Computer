import time

try:
    import RPi.GPIO as GPIO
except:
    pass

class IO:

    def __init__(self,modeselect) -> None:
        
        self.modeselect = modeselect
        self.mode = {0:'GCS',1:'FUI'}

        #GPIO.setmode(GPIO.BOARD)
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        self.INpins = [11,13,15,16,18,22]
        self.OUTpins = [29,31,36,37,38,40]
        self.outputs = []
        self.PWMpins = [32,33]

        #GPIO.setup(self.INpins, GPIO.IN)
        #GPIO.setup(self.OUTpins, GPIO.OUT)

        #self.pwm1 = GPIO.PWM(self.PWMpins[0], 50)
        #self.pwm2 = GPIO.PWM(self.PWMpins[1], 50)
        #self.pwm1.start(0)
        #self.pwm2.start(0)

        self.packet = {"INPin":0,"INState":0,"OUTPin":0,"OUTState":0}

        print("IO Init")

    def readIO(self):

        for x in range(len(self.INpins)):

            self.packet["INPin"] += str(self.INpins[x]) + '|'
            self.packet["INState"] += str(GPIO.input(self.INpins[x]))
        
    def writeIO(self,p1,p2,p3,p4,p5,p6):

        self.outputs = [p1,p2,p3,p4,p5,p6]

        for x in range(len(self.OUTpins)):

            self.packet["OUTPin"] += str(self.OUTpins[x]) + '|'
            self.packet["OUTState"] += str(self.outputs[x])

            GPIO.output(self.OUTpins[x],self.outputs[x])

    def analogueReadIO(self):
        pass
    
    def pwmWriteIO(self,dc1,dc2):

        self.dc1 = dc1
        self.dc2 = dc2

        self.pwm1.ChangeDutyCycle(self.dc1)
        self.pwm2.ChangeDutyCycle(self.dc2)

        return self.packet

    def packetStruct(self):
        return self.packet
