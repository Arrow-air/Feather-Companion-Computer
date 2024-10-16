import time
import serial
import struct
import math
import json

class Veronte2:

    def __init__(self, Veronteport, Verontebitrate, modeselect):
        self.modeselect = modeselect
        self.mode = {0: 'GCS', 1: 'FUI'}

        self.Veronteport = Veronteport
        self.Verontebitrate = Verontebitrate

        # Serial connection to the telemetry source
        self.VeronteSerial = serial.Serial(self.Veronteport, self.Verontebitrate, timeout=1)

        self.Data = []
        self.packet = {}
        self.dataDictionary = {'altitude_AGL': 0, 'altitude_AGL_set': 0, 'altitude_ABS': 40, 'heading': 0, 
                               'compass': 0, 'attitude_pitch': 0, 'attitude_roll': 0, 'vertical_speed_KTS': 0,
                               'airspeed_KTS': 0, 'OAT': 0, 'latitude': '40d26a46q', 'longitude': '79d58a56q'}

        # Ordered list of keys for telemetry data
        self.datalist = ['altitude_AGL', 'altitude_AGL_set', 'altitude_ABS', 'heading', 'compass', 'attitude_pitch', 
                         'attitude_roll', 'vertical_speed_KTS', 'airspeed_KTS', 'OAT', 'latitude', 'longitude']

        print("Veronte Init")

    def packetStruct(self):
        """
        Reads and parses telemetry data from the serial stream.
        Populates self.packet according to the ordered keys in self.datalist.
        """
        time.sleep(0.1)
        try:
            self.data = self.readData()

            if self.data:  # Only process valid data
                telemetry_data = self.data[1]
                print(len(telemetry_data))
                if len(telemetry_data) == 12:
                    for i, key in enumerate(self.datalist):
                        self.packet[key] = telemetry_data[i].get(f"Variable{i}", 0)

                    # Convert angles from radians to degrees
                    #self.packet['attitude_pitch'] = math.degrees(self.packet['attitude_pitch'])
                    #self.packet['attitude_roll'] = math.degrees(self.packet['attitude_roll'])
                    #self.packet['heading'] = math.degrees(self.packet['heading'])
                    #self.packet['compass'] = math.degrees(self.packet['compass'])

                    # Convert latitude and longitude to DMS format
                    #self.packet['latitude'] = self.decimal_to_dms(self.packet['latitude'])
                    #self.packet['longitude'] = self.decimal_to_dms(self.packet['longitude'])

                    print(self.packet)
                    return [self.packet, self.data[0]]

            else:
                return [self.dataDictionary, self.data]

        except Exception as e:
            print(f"Error parsing telemetry packet: {e}")
            return [self.dataDictionary, self.data]

    def readData(self):
        """
        Reads and parses a telemetry packet from the serial stream.
        Includes a CRC check against 0x94B0.
        """
        try:
            packet = {}

            if self.VeronteSerial.in_waiting > 0:
                # Start reading the telemetry packet
                packet['start_byte'] = struct.unpack('B', self.VeronteSerial.read(1))[0]

                # Only process the packet if the start byte is 0xBA
                if packet['start_byte'] == 0xBA:
                    packet['uav_address'] = struct.unpack('<H', self.VeronteSerial.read(2))[0]
                    packet['command_bytes'] = struct.unpack('2B', self.VeronteSerial.read(2))
                    packet['fixed_byte_1'] = struct.unpack('B', self.VeronteSerial.read(1))[0]
                    packet['fixed_byte_2'] = struct.unpack('B', self.VeronteSerial.read(1))[0]
                    packet['length'] = struct.unpack('B', self.VeronteSerial.read(1))[0]
                    packet['crc'] = struct.unpack('B', self.VeronteSerial.read(1))[0]
                    #print(packet['command_bytes'])

                    # Now read the data segment (length - 8 bytes)
                    data_length = packet['length'] - 8
                    telemetry_data = []

                    # Read timestamp (FLOAT32, mixed-endian)
                    timestamp_bytes = self.VeronteSerial.read(4)
                    timestamp = self.unpack_mixed_endian_float(timestamp_bytes)

                    # Read hash value (UINT32, mixed-endian)
                    hash_value = struct.unpack('I', self.VeronteSerial.read(4))[0]
                    #print(hash_value)

                    # Read variables (XTYPE, float32)

                    for i in range((data_length // 4)):
                        variable_bytes = self.VeronteSerial.read(4)
                        print(variable_bytes)
                        
                        variable = self.unpack_mixed_endian_float(variable_bytes)
                        telemetry_data.append({f"Variable{i}": round(variable, 2)})

                    packet['data'] = telemetry_data

                    # Read the final CRC (2 bytes)
                    packet['end_crc'] = struct.unpack('<H', self.VeronteSerial.read(2))[0]

                    self.VeronteSerial.flush()

                    #print(hex(packet['end_crc']))

                    # Check if the CRC is valid (expected value: 0x94B0)
                    #if packet['end_crc'] != 0x94B0:
                    #    print(f"Invalid CRC: {hex(packet['end_crc'])}, expected 0x94B0")
                    #    return None  # Discard packet if CRC is invalid

                    # If CRC is valid, return the parsed telemetry data
                    return [packet, telemetry_data]

        except Exception as e:
            print(f"Error reading data: {e}")
            return [self.dataDictionary, self.telemetrydata]

    def unpack_mixed_endian_float(self, byte_data):
        """
        Unpacks a mixed-endian float32 value from 4 bytes.
        Assumes mixed-endian means swapping AABBCCDD to CCDDAABB.
        """
        mixed_endian_bytes = byte_data#byte_data[2:4] + byte_data[0:2]
        return struct.unpack('f', mixed_endian_bytes)[0]

    def decimal_to_dms(self, decimal_degree):
        """
        Convert a decimal degree value to degrees, minutes, and seconds (DMS) format.
        """
        # Determine if the value is latitude or longitude and set the direction accordingly
        decimal_degree = math.degrees(decimal_degree)
        if decimal_degree < 0:
            direction = 'S' if abs(decimal_degree) <= 90 else 'W'
        else:
            direction = 'N' if abs(decimal_degree) <= 90 else 'E'

        decimal_degree = abs(decimal_degree)
        degrees = int(decimal_degree)
        minutes = int((decimal_degree - degrees) * 60)
        seconds = (decimal_degree - degrees - minutes / 60) * 3600
        
        return f"{degrees}°{minutes}'{seconds:.2f}\" {direction}"

if __name__ == '__main__':
    VeronteComport = '/dev/ttyS0'  # Veronte Serial Port
    Serialbitrate = 115200

    veronte = Veronte2(VeronteComport, Serialbitrate, 1)
    while True:
        veronte.packetStruct()
