import can
import struct
import time

class VESCCAN:
    def __init__(self):

        self.can0 = can.interface.Bus(channel='can0', bustype='socketcan', bitrate=500000)

        self.id = ''
        self.data = ''
        self.unit_id = ''
        self.command = ''
        self.message = None
        self.prev_message = None

        self.auxnum = 0
        self.cellnum = 0
        
        self.auxA = []
        self.auxB = []
        self.auxC = []
        
        self.cellsA = []
        self.cellsB = []
        self.cellsC = []
        
        self.idData = {}
        self.msgData = {}
        self.unitData = {'1':{},'2':{},'3':{},'4':{},'5':{},'6':{}}

    def calculate_can_id(self,unit_id, command):

        # Ensure controller ID and command number are within valid range
        if unit_id < 1 or unit_id > 255:
            raise ValueError("Controller ID must be between 1 and 255.")
        if command < 0 or command > 255:
            raise ValueError("Command number must be between 0 and 255.")
        
        # Frame type for data frame is 0
        frame_type = 0

        # Calculate the CAN ID by shifting and combining the parts
        self.id = ( frame_type << 26) | (unit_id << 8) | command 
        
        return self.id
    
    def decode_can_id(self,id):

        if id < 0 or id > 0x1FFFFFFF:
            raise ValueError("CAN ID must be a 29-bit value between 0 and 0x1FFFFFFF.")

        # Extract components from the CAN ID
        self.unit_id = id & 0xFF

        self.command = (id >> 8) & 0xFF

        self.spare = (id >> 16) & 0x3FF

        self.frame_type = (id >> 26) & 0x7

        self.idData = {'controller_id': self.unit_id,'command_number': self.command,'spare': self.spare,'frame_type': self.frame_type}

        return self.idData
    
    def read_frame(self):

        #print("Reading BMS")

        if self.message is None:
            self.message = self.can0.recv()
            self.prev_message = self.message

        elif self.message is not None:
            self.message = self.can0.recv(timeout=0.01)

            if self.message is None:
                self.message = self.prev_message
		
        self.id = self.message.arbitration_id

        if self.message.is_extended_id:
            self.decode_can_id(self.id)
        else:
            self.unit_id = self.id & 0xFF
            self.command = (self.id >> 5) & 0xFF

        self.data = self.message.data
        return self.parse_frame(self.command, self.data, self.unit_id)

    def parse_frame(self, command, data, unit_id):

        self.msgData = {'unit_id': unit_id}
        #print(command)
        #print(unit_id)
        
        #Note: Might Need to switch endianness in unpack function for real bms
        #Note: Scaling Factors might differ from those stipulated in the DBC packet structure file
        #Note: Command Differe from DBC files and should instead be found in the Ennoid Code
        #####: From DBC [9738, 9994, 10250, 10506, 10762, 11018, 11274, 11530]
        #####: From Code [38, 39, 40, 41, 42, 43, 44, 45]

        if (command == 38) and unit_id in range(10,17): # CAN_PACKET_BMS_V_TOT

            #print(command)
            #print(unit_id)
            self.msgData['packVoltage'] = struct.unpack('>I', data[0:4])[0] * 0.0000001
            self.msgData['chargerVoltage'] = struct.unpack('>I', data[4:8])[0] * 0.0000001

        elif (command == 39) and unit_id in range(10,17):# CAN_PACKET_BMS_I

            #print(command)
            #print(unit_id)
            self.msgData['packCurrent1'] = struct.unpack('<i', data[0:4])[0] * 0.000001
            self.msgData['packCurrent2'] = struct.unpack('<i', data[4:8])[0] * 0.000001

        elif (command == 40) and unit_id in range(10,17):# CAN_PACKET_BMS_AH_WH

            #print(command)
            #print(unit_id)
            self.msgData['Ah_Counter'] = struct.unpack('<I', data[0:4])[0] * 0.001
            self.msgData['Wh_Counter'] = struct.unpack('<I', data[4:8])[0] * 0.001

        elif (command == 41) and unit_id in range(10,17):# CAN_PACKET_BMS_V_CELL

            #print(command)
            #print(unit_id)

            '''
            self.msgData['cellPoint'] = data[0]
            self.msgData['NoOfCellsA'] = data[1]
            self.msgData['cellVoltage10'] = struct.unpack('<H', data[2:4])[0] * 0.001
            self.msgData['cellVoltage11'] = struct.unpack('<H', data[4:6])[0] * 0.001
            self.msgData['cellVoltage12'] = struct.unpack('<H', data[6:8])[0] * 0.001
            '''
            
            if 'cellVoltage10' not in self.msgData:
                self.msgData['cellVoltage10'] = []
            if 'cellVoltages11' not in self.msgData:
                self.msgData['cellVoltage11'] = []
            if 'cellVoltages12' not in self.msgData:
                self.msgData['cellVoltage12'] = []

            self.msgData['cellPoint'] = data[0]
            self.msgData['NoOfCellsA'] = data[1]
            
            self.cellsA.append(struct.unpack('>H', data[2:4])[0] * 0.001)
            self.cellsB.append(struct.unpack('>H', data[4:6])[0] * 0.001)
            self.cellsC.append(struct.unpack('>H', data[6:8])[0] * 0.001)
            
            self.cellnum += 1
            
            if self.cellnum > 7:

                self.msgData['cellVoltage10'] = self.cellsA
                self.msgData['cellVoltage11'] = self.cellsB
                self.msgData['cellVoltage12'] = self.cellsC
            
                self.cellsA = []
                self.cellsB = []
                self.cellsC = []
                
                self.cellnum = 0

        elif (command == 42) and unit_id in range(10,17):# CAN_PACKET_BMS_BAL

            #print(command)
            #print(unit_id)

            self.msgData['NoOfCellsB'] = data[0] #struct.unpack('<B', data[0:1])[0]
            data2 = list(data[1:8])
            data2.append(0)
            self.msgData['bal_state'] = struct.unpack('<Q', bytes(data2))[0] #struct.unpack('<Q', data2)[0] >> 1
        
        elif (command == 43) and unit_id in range(10,17):# CAN_PACKET_BMS_TEMPS

            #print(command)
            #print(unit_id)

            '''
            self.msgData['NoOfCellsC'] = data[1]
            self.msgData['auxVoltagesIndividual1'] = struct.unpack('<H', data[2:4])[0] * 0.01
            self.msgData['auxVoltagesIndividual2'] = struct.unpack('<H', data[4:6])[0] * 0.01
            self.msgData['auxVoltagesIndividual3'] = struct.unpack('<H', data[6:8])[0] * 0.01
            '''
            
            if 'auxVoltagesIndividual1' not in self.msgData:
                self.msgData['auxVoltagesIndividual1'] = []
            if 'auxVoltagesIndividual2' not in self.msgData:
                self.msgData['auxVoltagesIndividual2'] = []
            if 'auxVoltagesIndividual3' not in self.msgData:
                self.msgData['auxVoltagesIndividual3'] = []

            self.msgData['NoOfCellsC'] = data[1]
            
            self.auxA.append(struct.unpack('>H', data[2:4])[0] * 0.01)
            self.auxB.append(struct.unpack('>H', data[4:6])[0] * 0.01)
            #self.auxC.append(struct.unpack('>H', data[6:8])[0] * 0.01)
            
            self.auxnum += 1
            
            if self.auxnum > 7:

                self.msgData['auxVoltagesIndividual1'] = self.auxA
                self.msgData['auxVoltagesIndividual2'] = self.auxB 
                self.msgData['auxVoltagesIndividual3'] = self.auxC 
            
                self.auxA = []
                self.auxB = []
                self.auxC = []
                
                self.auxnum = 0

        elif (command == 44) and unit_id in range(10,17):# CAN_PACKET_BMS_HUM

            #print(command)
            #print(unit_id)

            self.msgData['CAN_PACKET_BMS_TEMP0'] = struct.unpack('>H', data[0:2])[0] * 0.01
            self.msgData['CAN_PACKET_BMS_HUM_HUM'] = struct.unpack('>H', data[2:4])[0] * 0.01
            self.msgData['CAN_PACKET_BMS_HUM_TEMP1'] = struct.unpack('>H', data[4:6])[0] * 0.001

        elif (command == 45) and unit_id in range(10,17):# CAN_PACKET_BMS_SOC_SOH_TEMP_STAT

            #print(command)
            #print(unit_id)

            self.msgData['cellVoltageLow'] = struct.unpack('>H', data[0:2])[0] * 0.001
            self.msgData['cellVoltageHigh'] = struct.unpack('>H', data[2:4])[0] * 0.001
            self.msgData['SOC'] = data[4] * 0.392156862745098
            self.msgData['SOH'] = data[5] * 0.3922
            self.msgData['tBattHi'] = data[6]
            self.msgData['BitF'] = data[7]

        else:
            #print(unit_id)
            #print(command)
            self.msgData['raw_data'] = data
            
        #print(self.msgData)
        self.prev_message = self.message
        return self.msgData
        
if __name__ == "__main__":
    
    vesc = VESCCAN()
    
    while True:
        
        vesc.unitData = {'1':{},'2':{},'3':{},'4':{},'5':{},'6':{}}
        
        while len(vesc.unitData['6']) <= 28:
        
            rawData = vesc.read_frame()
            
            #print(rawData)
            #print("\n")

            if rawData['unit_id'] == 11:
                vesc.unitData['1'] |= rawData
            elif rawData['unit_id'] == 12:
                vesc.unitData['2'] |= rawData
            elif rawData['unit_id'] == 13:
                vesc.unitData['3'] |= rawData
            elif rawData['unit_id'] == 14:
                vesc.unitData['4'] |= rawData
            elif rawData['unit_id'] == 15:
                vesc.unitData['5'] |= rawData
            elif rawData['unit_id'] == 16:
                vesc.unitData['6'] |= rawData

            #print(vesc.unitData)
            #print("\n")
            #print(len(vesc.unitData['6']))

        print(vesc.unitData)
        print("\n")

