import time
import serial
import struct
import json

class Veronte2:

    def __init__(self, Veronteport, Verontebitrate, modeselect):

        self.modeselect = modeselect
        self.mode = {0: 'GCS', 1: 'FUI'}

        self.Veronteport = Veronteport
        self.Verontebitrate = Verontebitrate

        # Serial connection to the telemetry source
        self.VeronteSerial = serial.Serial(self.Veronteport, self.Verontebitrate, timeout=1)

        self.Data = ''
        self.packet = {}
        self.dataDictionary = {
            'altitude_AGL': 0, 'altitude_AGL_set': 0, 'altitude_ABS': 0, 
            'heading': 0, 'compass': 0, 'attitude_pitch': 0, 'attitude_roll': 0, 
            'vertical_speed_KTS': 0, 'airspeed_KTS': 0, 'OAT': 0
        }

        print("Veronte Init")

    def packetStruct(self):
        """
        Reads and parses telemetry data from the serial stream.
        """
        try:
            self.dataDictionary = self.readData()
            self.packet = {key: round(self.dataDictionary[0][key], 2) for key in self.dataDictionary[0]}
            
            print([self.packet, self.dataDictionary[1]])

            return [self.packet, self.dataDictionary[1]] 
        except Exception as e:
            print(f"Error parsing telemetry packet: {e}")
            return {}

    def readData(self):
        time.sleep(0.05)
        """
        Reads and parses a telemetry packet from the serial stream.
        """
        try:
            packet = {}

            # Check if there's data available in the serial buffer
            if self.VeronteSerial.in_waiting > 0:
                # Start reading the telemetry packet

                #print(self.VeronteSerial.read())

                packet['start_byte'] = struct.unpack('B', self.VeronteSerial.read(1))[0]
                packet['uav_address'] = struct.unpack('<H', self.VeronteSerial.read(2))[0]
                packet['command_bytes'] = struct.unpack('2B', self.VeronteSerial.read(2))
                packet['fixed_byte_1'] = struct.unpack('B', self.VeronteSerial.read(1))[0]
                packet['fixed_byte_2'] = struct.unpack('B', self.VeronteSerial.read(1))[0]
                packet['length'] = struct.unpack('B', self.VeronteSerial.read(1))[0]
                packet['crc'] = struct.unpack('B', self.VeronteSerial.read(1))[0]

                # Now read the data segment (length - 2 bytes)
                data_length = packet['length'] - 2
                print(data_length)
                telemetry_data = []

                # Read timestamp (FLOAT32)
                timestamp = struct.unpack('f', self.VeronteSerial.read(4))[0]
                telemetry_data.append({"Timestamp": timestamp})

                # Read hash value (UINT32)
                hash_value = struct.unpack('I', self.VeronteSerial.read(4))[0]
                telemetry_data.append({"Hash": hash_value})

                # Read variables (XTYPE, assuming float32 for example)
                for _ in range(data_length // 4):  # Adjust as per actual format
                    variable = struct.unpack('f', self.VeronteSerial.read(4))[0]
                    telemetry_data.append({f"Variable{_}": variable})

                packet['data'] = telemetry_data

                # Read the final CRC (2 bytes)
                packet['end_crc'] = struct.unpack('<H', self.VeronteSerial.read(2))[0]

                # Return the parsed telemetry data
                return telemetry_data

        except Exception as e:
            print(f"Error reading data: {e}")
            return {}

    def getTelemetryAsJSON(self):
        """
        Returns the parsed telemetry packet as a JSON string.
        """
        packet = self.packetStruct()
        return json.dumps(packet[0], indent=4)

if __name__ == '__main__':

    VeronteComport = '/dev/ttyS0' #Veronte Serial Port
    Serialbitrate = 115200

    veronte = Veronte2(VeronteComport, Serialbitrate, 1)

    while True:
        print(veronte.readData())
        #print(veronte.getTelemetryAsJSON())
