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
			0xC780801	Throttle Data 6152 ID
			0xC780901	Throttle Data 6153 ID
			0x14781010	Info Upload 6160 ID
			0x14781110	Info Upload 6161 ID
			0x107D5510	Heartbeat ID
		'''
		
		data = message.data[0:len(message.data) - 1] # Remove tail byte
		
		if message.arbitration_id in range(0xC780801,0xC780807):
			self.parse_throttle_data1(data)
		elif message.arbitration_id in range(0xC780901,0xC780907): #0x181:
			self.parse_throttle_data2(data)
		elif message.arbitration_id in range(0x14781010,0x14781017):#0x182:
			self.parse_info_upload_6160(data)
		elif message.arbitration_id in range(0x14781110,0x14781117):#0x183:
			self.parse_info_upload_6161(data)
		elif message.arbitration_id in range(0x107D5510,0x107D5517):#0x184:
			#self.parse_heartbeat(data)
			pass
		
		self.esc_data['unit_id'] = message.arbitration_id
		#print(self.esc_data['unit_id'])

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
		
	def parse_throttle_data1(self, data):
		throttles = struct.unpack('<7B', data)
		self.esc_data['throttle_data1'] = self.reverseMakeThrot(throttles)
		#print(self.esc_data['throttle_data'])
	
	def parse_throttle_data2(self, data):
		throttles = struct.unpack('<7B', data)
		self.esc_data['throttle_data2'] = self.reverseMakeThrot(throttles)
		#print(self.esc_data['throttle_data2'])


	def parse_info_upload_6160(self, data):
		electrical_speed, bus_current, running_status = struct.unpack('<HhH', data)
		self.esc_data['info_upload_6160'] = {
		'electrical_speed': electrical_speed/10,
		'RPM': (electrical_speed/10)*3,
		'bus_current': bus_current/10,
		'running_status': running_status
		}
		#print(self.esc_data['info_upload_6160'])

	def parse_info_upload_6161(self, data):
		output_throttle, bus_voltage, mos_temp, cap_temp, motor_temp = struct.unpack('<HhBBB', data)
		self.esc_data['info_upload_6161'] = {
		'output_throttle': output_throttle,
		'bus_voltage': bus_voltage/10,
		'temperatures': {
		'MOS': mos_temp - 40,
		'Capacitance': cap_temp - 40,
		'Motor': motor_temp - 40
		}
		}
		#print(self.esc_data['info_upload_6161'])

	def parse_heartbeat(self, data):
		power_on_timeA, power_on_timeB, power_on_timeC, power_on_timeD, health_status, current_mode, user_defined = struct.unpack('<7B', data)
		power_on_time = (power_on_timeA << 24) | (power_on_timeB << 16) | (power_on_timeC << 8) | power_on_timeD
		self.esc_data['heartbeat'] = {
		'power_on_time': power_on_time,
		'health_status': health_status,
		'current_mode': current_mode,
		'user_defined': user_defined
		}
		#print(self.esc_data['heartbeat'])

	def get_data(self):
		return self.esc_data

if __name__ == "__main__":
	
	cyphalcan = CyphalCAN3()

	while True:
		
		cyphalcan.unitData = {'0':{},'1':{},'2':{},'3':{},'4':{},'5':{}}
		
		while len(cyphalcan.unitData['5']) < 8:
			
			cyphalcan.esc_data = {}
			
			cyphalcan.receive_data()
			rawData = cyphalcan.get_data()
			
			if (rawData['unit_id'] - 0xC780801 == 0 and rawData['throttle_data1'][1] == 0 and rawData['throttle_data1'][2] == 0 and rawData['throttle_data1'][3] == 0) or rawData['unit_id'] - 0x14781010 == 0 or rawData['unit_id'] - 0x14781110 == 0 or rawData['unit_id'] - 0x107D5510 == 0:
				rawData['throttle_data2'] = []
				cyphalcan.unitData['0'] |= rawData
			elif (rawData['unit_id'] - 0xC780801 == 0 and rawData['throttle_data1'][0] == 0 and rawData['throttle_data1'][2] == 0 and rawData['throttle_data1'][3] == 0) or rawData['unit_id'] - 0x14781010 == 1 or rawData['unit_id'] - 0x14781110 == 1 or rawData['unit_id'] - 0x107D5510 == 1:
				rawData['throttle_data2'] = []
				cyphalcan.unitData['1'] |= rawData
			elif (rawData['unit_id'] - 0xC780801 == 0 and rawData['throttle_data1'][0] == 0 and rawData['throttle_data1'][1] == 0 and rawData['throttle_data1'][3] == 0) or rawData['unit_id'] - 0x14781010 == 2 or rawData['unit_id'] - 0x14781110 == 2 or rawData['unit_id'] - 0x107D5510 == 2:
				rawData['throttle_data2'] = []
				cyphalcan.unitData['2'] |= rawData
			elif (rawData['unit_id'] - 0xC780901 == 0 and rawData['throttle_data2'][1] == 0 and rawData['throttle_data2'][2] == 0 and rawData['throttle_data2'][3] == 0) or rawData['unit_id'] - 0x14781010 == 4 or rawData['unit_id'] - 0x14781110 == 4 or rawData['unit_id'] - 0x107D5510 == 4:
				rawData['throttle_data'] = []
				cyphalcan.unitData['3'] |= rawData
			elif (rawData['unit_id'] - 0xC780901 == 0 and rawData['throttle_data2'][0] == 0 and rawData['throttle_data2'][2] == 0 and rawData['throttle_data2'][3] == 0) or rawData['unit_id'] - 0x14781010 == 5 or rawData['unit_id'] - 0x14781110 == 5 or rawData['unit_id'] - 0x107D5510 == 5:
				rawData['throttle_data'] = []
				cyphalcan.unitData['4'] |= rawData
			elif (rawData['unit_id'] - 0xC780901 == 0 and rawData['throttle_data2'][0] == 0 and rawData['throttle_data2'][1] == 0 and rawData['throttle_data2'][3] == 0) or rawData['unit_id'] - 0x14781010 == 6 or rawData['unit_id'] - 0x14781110 == 6 or rawData['unit_id'] - 0x107D5510 == 6:
				rawData['throttle_data'] = []
				cyphalcan.unitData['5'] |= rawData
			
			print(len(cyphalcan.unitData['5']))

		print(cyphalcan.unitData)

