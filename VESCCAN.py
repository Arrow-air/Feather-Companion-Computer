import can
import struct

class VESCCAN:
    def __init__(self):
        self.can0 = can.interface.Bus(channel='can0', bustype='socketcan')  # socketcan_native Bitrate implicit at 500K
        self.id = ''
        self.data = ''
        self.unit_id = ''
        self.command = ''
        self.message = ''
        self.idData = {}
        self.msgData = {}
        self.unitData = {'0': {}, '1': {}, '2': {}, '3': {}, '4': {}, '5': {}}

    def calculate_can_id(self, unit_id, command):
        # Ensure controller ID and command number are within valid range
        if unit_id < 0 or unit_id > 255:
            raise ValueError("Controller ID must be between 0 and 255.")
        if command < 0 or command > 255:
            raise ValueError("Command number must be between 0 and 255.")

        # Frame type for data frame is 0
        frame_type = 0

        # Calculate the CAN ID by shifting and combining the parts
        self.id = (frame_type << 26) | (command << 8) | unit_id

        return self.id

    def decode_can_id(self, id):
        if id < 0 or id > 0x1FFFFFFF:
            raise ValueError("CAN ID must be a 29-bit value between 0 and 0x1FFFFFFF.")

        # Extract components from the CAN ID
        self.unit_id = id & 0xFF
        self.command = (id >> 8) & 0xFF
        self.spare = (id >> 16) & 0x3FF
        self.frame_type = (id >> 26) & 0x7
        self.idData = {'controller_id': self.unit_id, 'command_number': self.command, 'spare': self.spare, 'frame_type': self.frame_type}

        return self.idData

    def read_frame(self):
        self.message = self.can0.recv()

        if self.message is None:
            return None

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

        if command == 11018:  # CAN_PACKET_BMS_TEMPS
            self.msgData['NoOfCells'] = data[1]
            self.msgData['auxVoltagesIndividual1'] = struct.unpack('>H', data[2:4])[0] * 0.01
            self.msgData['auxVoltagesIndividual2'] = struct.unpack('>H', data[4:6])[0] * 0.01
            self.msgData['auxVoltagesIndividual3'] = struct.unpack('>H', data[6:8])[0] * 0.01

        elif command == 9738:  # CAN_PACKET_BMS_V_TOT
            self.msgData['packVoltage'] = struct.unpack('>I', data[0:4])[0] * 0.001
            self.msgData['chargerVoltage'] = struct.unpack('>I', data[4:8])[0] * 0.001

        elif command == 9994:  # CAN_PACKET_BMS_I
            self.msgData['packCurrent1'] = struct.unpack('>i', data[0:4])[0] * 0.01  # signed integer
            self.msgData['packCurrent2'] = struct.unpack('>i', data[4:8])[0] * 0.01  # signed integer

        elif command == 10250:  # CAN_PACKET_BMS_AH_WH
            self.msgData['Ah_Counter'] = struct.unpack('>I', data[0:4])[0] * 0.001
            self.msgData['Wh_Counter'] = struct.unpack('>I', data[4:8])[0] * 0.001

        elif command == 10506:  # CAN_PACKET_BMS_V_CELL
            self.msgData['cellPoint'] = data[0]
            self.msgData['NoOfCells'] = data[1]
            self.msgData['cellVoltage10'] = struct.unpack('>H', data[2:4])[0] * 0.001
            self.msgData['cellVoltage11'] = struct.unpack('>H', data[4:6])[0] * 0.001
            self.msgData['cellVoltage12'] = struct.unpack('>H', data[6:8])[0] * 0.001

        elif command == 10762:  # CAN_PACKET_BMS_BAL
            self.msgData['NoOfCells'] = data[0]
            data2 = list(data[1:8])
            data2.append(0)
            self.msgData['bal_state'] = struct.unpack('<Q', bytes(data2))[0]

        elif command == 11530:  # CAN_PACKET_BMS_SOC_SOH_TEMP_STAT
            self.msgData['cellVoltageLow'] = struct.unpack('>H', data[0:2])[0] * 0.001
            self.msgData['cellVoltageHigh'] = struct.unpack('>H', data[2:4])[0] * 0.001
            self.msgData['SOC'] = data[4] * 0.392156862745098
            self.msgData['SOH'] = data[5] * 0.3922
            self.msgData['tBattHi'] = data[6]
            self.msgData['BitF'] = data[7]

        elif command == 11274:  # CAN_PACKET_BMS_HUM
            self.msgData['CAN_PACKET_BMS_TEMP0'] = struct.unpack('>H', data[0:2])[0] * 0.01
            self.msgData['CAN_PACKET_BMS_HUM_HUM'] = struct.unpack('>H', data[2:4])[0] * 0.01
            self.msgData['CAN_PACKET_BMS_HUM_TEMP1'] = struct.unpack('>H', data[4:6])[0] * 0.01

        else:
            self.msgData['raw_data'] = data

        return self.msgData

if __name__ == "__main__":
    vesc = VESCCAN()

    while True:
        vesc.unitData = {'0': {}, '1': {}, '2': {}, '3': {}, '4': {}, '5': {}}

        while len(vesc.unitData['5']) < 25:
            rawData = vesc.read_frame()

            if rawData['unit_id'] == 0:
                vesc.unitData['0'].update(rawData)
            elif rawData['unit_id'] == 1:
                vesc.unitData['1'].update(rawData)
            elif rawData['unit_id'] == 2:
                vesc.unitData['2'].update(rawData)
            elif rawData['unit_id'] == 3:
                vesc.unitData['3'].update(rawData)
            elif rawData['unit_id'] == 4:
                vesc.unitData['4'].update(rawData)
            elif rawData['unit_id'] == 5:
                vesc.unitData['5'].update(rawData)

        print(vesc.unitData)
        print("\n")
