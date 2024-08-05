import can
import struct

class CyphalCAN3:
	def __init__(self):

		self.can0 = can.interface.Bus(channel='can0', bustype='socketcan', bitrate=500000)

		self.esc_data = {}
		self.unitData = {'0':{},'1':{},'2':{},'3':{},'4':{},'5':{}}

	def send_command(self, node_id: int, command: int):
		can_id = 0x180 + node_id
		data = struct.pack('<B2x', command)
		message = can.Message(arbitration_id=can_id, data=data, is_extended_id=True)
		self.can0.send(message)

	def read_register(self, node_id: int, register_index: int):
		can_id = 0x100 + node_id
		data = struct.pack('<BB', 0x00, register_index)
		message = can.Message(arbitration_id=can_id, data=data, is_extended_id=True)
		self.can0.send(message)

	def write_register(self, node_id: int, register_index: int, value: int):
		can_id = 0x100 + node_id
		data = struct.pack('<BBH', 0x02, register_index, value)
		message = can.Message(arbitration_id=can_id, data=data, is_extended_id=True)
		self.can0.send(message)

	def get_node_info(self, node_id: int):
		can_id = 0x1AE + node_id
		data = bytearray()
		message = can.Message(arbitration_id=can_id, data=data, is_extended_id=True)
		self.can0.send(message)

	def receive_data(self):
		message = self.can0.recv()
		#print(message.data)
		if message:
			self.parse_message(message)

	def parse_message(self, message):
		
		'''
			0x180810	Throttle Data 6152 sent
			0x180910	Throttle Data 6153 sent
			0x181010	Info Upload 6160 sent
			0x181110	Info Upload 6161 sent
			0x1D5510	Heartbeat sent
		'''
		
		data = message.data[0:len(message.data) - 1] # Remove tail byte
		
		if message.arbitration_id in range(0x180810,0x180817) or message.arbitration_id in range(0x180910,0x180917): #0x181:
			self.parse_throttle_data(data)
		elif message.arbitration_id in range(0x181010,0x181017):#0x182:
			self.parse_info_upload_6160(data)
		elif message.arbitration_id in range(0x181110,0x181117):#0x183:
			self.parse_info_upload_6161(data)
		elif message.arbitration_id in range(0x1D5510,0x1D5517):#0x184:
			self.parse_heartbeat(data)
		
		self.esc_data['unit_id'] = message.arbitration_id

	def parse_command_control(self, data):
		command, node_id = struct.unpack('<BBx', data)
		self.esc_data['command_control'] = {'command': command, 'node_id': node_id}
	
	def reverseMakeThrot(self, throtOut):
		# Extract the original 7 bytes
		throt0 = throtOut[0] | (throtOut[1] << 8)
		throt1 = throtOut[2] | (throtOut[3] << 8)
		throt2 = throtOut[4] | (throtOut[5] << 8)
		throt3 = throtOut[6]

		# Reconstruct the last throttle
		throt3 = throt3 | ((throt0 & 0xC000) >> 2)
		throt3 = throt3 | ((throt1 & 0xC000) >> 4)
		throt3 = throt3 | ((throt2 & 0xC000) >> 6)

		# Mask out the extra bits
		throt0 &= 0x3FFF
		throt1 &= 0x3FFF
		throt2 &= 0x3FFF

		# Combine the values into the original list
		throt = [throt0, throt1, throt2, throt3]

		return throt
		
	def parse_throttle_data(self, data):
		throttles = struct.unpack('<7B', data)
		self.esc_data['throttle_data'] = self.reverseMakeThrot(throttles)

	def parse_info_upload_6160(self, data):
		electrical_speed, bus_current, running_status = struct.unpack('<HhH', data)
		self.esc_data['info_upload_6160'] = {
		'electrical_speed': electrical_speed,
		'bus_current': bus_current,
		'running_status': running_status
		}

	def parse_info_upload_6161(self, data):
		output_throttle, bus_voltage, mos_temp, cap_temp, motor_temp = struct.unpack('<HhBBB', data)
		self.esc_data['info_upload_6161'] = {
		'output_throttle': output_throttle,
		'bus_voltage': bus_voltage,
		'temperatures': {
		'MOS': mos_temp - 40,
		'Capacitance': cap_temp - 40,
		'Motor': motor_temp - 40
		}
		}

	def parse_heartbeat(self, data):
		power_on_timeA,power_on_timeB,power_on_timeC,power_on_timeD, health_status, current_mode = struct.unpack('<6B', data)
		power_on_time = (power_on_timeA << 24) | (power_on_timeB << 16) | (power_on_timeC << 8) | power_on_timeD
		self.esc_data['heartbeat'] = {
		'power_on_time': power_on_time,
		'health_status': health_status,
		'current_mode': current_mode
		}

	def get_data(self):
		return self.esc_data

if __name__ == "__main__":
	
	cyphalcan = CyphalCAN3()
	
	while True:
		
		cyphalcan.unitData = {'0':{},'1':{},'2':{},'3':{},'4':{},'5':{}}
		
		while len(cyphalcan.unitData['5']) < 5:
			
			cyphalcan.esc_data = {}
			
			cyphalcan.receive_data()
			rawData = cyphalcan.get_data()
			
			if rawData['unit_id'] - 0x180810 == 0 or rawData['unit_id'] - 0x180910 == 0 or rawData['unit_id'] - 0x181010 == 0 or rawData['unit_id'] - 0x181110 == 0 or rawData['unit_id'] - 0x1D5510 == 0:
				cyphalcan.unitData['0'] |= rawData
				cyphalcan.unitData['1'] |= rawData
				cyphalcan.unitData['2'] |= rawData
				cyphalcan.unitData['3'] |= rawData
				cyphalcan.unitData['4'] |= rawData
				cyphalcan.unitData['5'] |= rawData
			'''
			elif rawData['unit_id'] - 0x180810 == 1 or rawData['unit_id'] - 0x180910 == 1 or rawData['unit_id'] - 0x181010 == 1 or rawData['unit_id'] - 0x181110 == 1 or rawData['unit_id'] - 0x1D5510 == 1:
				cyphalcan.unitData['1'] |= rawData
			elif rawData['unit_id'] - 0x180810 == 2 or rawData['unit_id'] - 0x180910 == 2 or rawData['unit_id'] - 0x181010 == 2 or rawData['unit_id'] - 0x181110 == 2 or rawData['unit_id'] - 0x1D5510 == 2:
				cyphalcan.unitData['2'] |= rawData
			elif rawData['unit_id'] - 0x180810 == 3 or rawData['unit_id'] - 0x180910 == 3 or rawData['unit_id'] - 0x181010 == 3 or rawData['unit_id'] - 0x181110 == 3 or rawData['unit_id'] - 0x1D5510 == 3:
				cyphalcan.unitData['3'] |= rawData
			elif rawData['unit_id'] - 0x180810 == 4 or rawData['unit_id'] - 0x180910 == 4 or rawData['unit_id'] - 0x181010 == 4 or rawData['unit_id'] - 0x181110 == 4 or rawData['unit_id'] - 0x1D5510 == 4:
				cyphalcan.unitData['4'] |= rawData
			elif rawData['unit_id'] - 0x180810 == 5 or rawData['unit_id'] - 0x180910 == 5 or rawData['unit_id'] - 0x181010 == 5 or rawData['unit_id'] - 0x181110 == 5 or rawData['unit_id'] - 0x1D5510 == 5:
				cyphalcan.unitData['5'] |= rawData
			'''
		print(cyphalcan.unitData['0'])
