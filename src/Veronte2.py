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

        self.Data = []
        self.packet = {}
        self.dataDictionary = {'altitude_AGL': 0, 'altitude_AGL_set': 0, 'altitude_ABS': 40, 'heading': 0, 
                               'compass': 0, 'attitude_pitch': 0, 'attitude_roll': 0, 'vertical_speed_KTS': 0,
                               'airspeed_KTS': 0, 'OAT': 0, 'latitude': '40d26a46q', 'longitude': '79d58a56q'}
        
        # Ordered list of keys for telemetry data
        self.datalist = ['altitude_AGL', 'altitude_AGL_set', 'altitude_ABS', 'heading', 'compass', 'attitude_pitch', 
                         'attitude_roll', 'vertical_speed_KTS', 'airspeed_KTS', 'OAT', 'latitude', 'longitude']
        
        # Example data packet for testing purposes
        self.dataPacket = {
            'start_byte': 0xBA,         # Start byte, assumed to be 0xBA
            'uav_address': 4041,        # UAV address, dummy value
            'command_bytes': [0xFF, 0x00],  # Command bytes, dummy values
            'fixed_byte_1': 0x00,       # Fixed byte 1, dummy value
            'fixed_byte_2': 0x05,       # Fixed byte 2, dummy value
            'length': 10,               # Length of the packet, dummy value
            'crc': 0xAB,                # CRC, dummy value
            'data': [
                {'Timestamp': 162255.56},   # Timestamp (dummy value)
                {'Hash': 123456},           # Hash value (dummy value)
                {'Variable0': 42.5},        # Variable 0, example variable
                {'Variable1': 13.8},        # Variable 1, example variable
                {'Variable2': 13.8},        # Variable 2, example variable
                {'Variable3': 13.8},        # Variable 3, example variable
                {'Variable4': 13.8},        # Variable 4, example variable
                {'Variable5': 13.8},        # Variable 5, example variable
                {'Variable6': 13.8},        # Variable 6, example variable
                {'Variable7': 13.8},        # Variable 7, example variable
                {'Variable8': 13.8},        # Variable 8, example variable
                {'Variable9': 13.8},        # Variable 9, example variable
                {'Variable10': 13.8},       # Variable 10, example variable
                {'Variable11': 13.8},       # Variable 11, example variable
            ],
            'end_crc': 0x1234            # End CRC, dummy value
        }

        print("Veronte Init")

    def packetStruct(self):
        """
        Reads and parses telemetry data from the serial stream.
        Populates self.packet according to the ordered keys in self.datalist.
        """
        try:

            self.data = self.readData()

            if self.data:  # Only process valid data
                
                # Parse telemetry data into self.packet using the ordered list
                telemetry_data = self.data[1]

                if (len(telemetry_data) == 13):

                    print(len(telemetry_data))
                    
                    for i, key in enumerate(self.datalist):
                        print(str(i) + ' | ' + key)
                        self.packet[key] = telemetry_data[i].get(f"Variable{i}", 0)

                    self.packet['latitude'] = self.decimal_to_dms(self.packet['latitude'])
                    self.packet['longitude'] = self.decimal_to_dms(self.packet['longitude'])

                    print("p: " + str(self.packet['attitude_pitch']) + "| r: " + str(self.packet['attitude_roll']) + "|y: " + str(self.packet['heading']) )
                
                    #print(self.packet)
                    # Return the packet and all other data elements that are not telemetry data
                    return [self.packet, self.data[0]]
            else:
                return [self.dataDictionary, self.dataPacket]

        except Exception as e:

            print(f"Error parsing telemetry packet: {e}")

            return [self.dataDictionary, self.dataPacket]
            

    def readData(self):
        
        """
        Reads and parses a telemetry packet from the serial stream.
        """
        try:
            packet = {}

            # Check if there's data available in the serial buffer
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

                    # Now read the data segment (length - 2 bytes)
                    data_length = packet['length'] - 2

                    telemetry_data = []

                    # Read timestamp (FLOAT32, mixed-endian)
                    timestamp_bytes = self.VeronteSerial.read(4)
                    timestamp = self.unpack_mixed_endian_float(timestamp_bytes)
                    #telemetry_data.append({"Timestamp": timestamp})

                    # Read hash value (UINT32)
                    hash_value = struct.unpack('I', self.VeronteSerial.read(4))[0]
                    #telemetry_data.append({"Hash": hash_value})

                    # Read variables (XTYPE, assuming float32 for example)
                    for i in range((data_length // 4)):  # Adjust as per actual format
                        variable_bytes = self.VeronteSerial.read(4)
                        variable = self.unpack_mixed_endian_float(variable_bytes)
                        telemetry_data.append({f"Variable{i}": round(variable,3)})

                    packet['data'] = telemetry_data

                    # Read the final CRC (2 bytes)
                    packet['end_crc'] = struct.unpack('<H', self.VeronteSerial.read(2))[0]

                    # Return the parsed telemetry data
                    return [packet, telemetry_data]

        except Exception as e:
            print(f"Error reading data: {e}")
            return {}

    def unpack_mixed_endian_float(self, byte_data):
        """
        Unpacks a mixed-endian float32 value from 4 bytes.
        Assumes mixed-endian means swapping AABBCCDD to CCDDAABB.
        """
        # Swapping bytes AABBCCDD to CCDDAABB
        mixed_endian_bytes = byte_data[2:4] + byte_data[0:2]
        return struct.unpack('f', mixed_endian_bytes)[0]

    def getTelemetryAsJSON(self):
        """
        Returns the parsed telemetry packet as a JSON string.
        """
        packet = self.packetStruct()
        #return json.dumps(packet[0], indent=4)
    
    def decimal_to_dms(self, decimal_degree):
        """
            Convert a decimal degree value to degrees, minutes, and seconds (DMS) format.
            
            Args:
            decimal_degree (float): The decimal degree value (positive for N/E, negative for S/W).
            
            Returns:
            tuple: A tuple in the form (degrees, minutes, seconds, direction).
        """
        # Determine if the value is latitude or longitude and set the direction accordingly
        if decimal_degree < 0:
            direction = 'S' if abs(decimal_degree) <= 90 else 'W'
        else:
            direction = 'N' if abs(decimal_degree) <= 90 else 'E'
        
        # Get the absolute value of the decimal degree
        decimal_degree = abs(decimal_degree)

        # Extract degrees
        degrees = int(decimal_degree)
        
        # Extract minutes
        minutes = int((decimal_degree - degrees) * 60)
        
        # Extract seconds
        seconds = (decimal_degree - degrees - minutes / 60) * 3600
        
        return str((degrees,minutes,seconds,direction))

if __name__ == '__main__':

    VeronteComport = '/dev/ttyS0'  # Veronte Serial Port
    Serialbitrate = 115200

    veronte = Veronte2(VeronteComport, Serialbitrate, 1)

    while True:
        #print(veronte.readData())
        veronte.getTelemetryAsJSON()
        #print(veronte.getTelemetryAsJSON())
