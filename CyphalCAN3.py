import can
import struct

class CyphalCAN3:
	def __init__(self,):

		self.can0 = can.interface.Bus(channel='can0', bustype='socketcan', bitrate=500000)

		self.esc_data = {}

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
		print(message)
		if message:
			self.parse_message(message)

	def parse_message(self, message):
		print(message.arbitration_id)

		if message.arbitration_id == 0x180:
			self.parse_command_control(message.data)
		elif message.arbitration_id == 0x181:
			self.parse_throttle_data(message.data)
		elif message.arbitration_id == 0x182:
			self.parse_info_upload_6160(message.data)
		elif message.arbitration_id == 0x183:
			self.parse_info_upload_6161(message.data)
		elif message.arbitration_id == 0x184:
			self.parse_heartbeat(message.data)

	def parse_command_control(self, data):
		command, node_id = struct.unpack('<BBx', data)
		self.esc_data['command_control'] = {'command': command, 'node_id': node_id}

	def parse_throttle_data(self, data):
		throttles = struct.unpack('<7B', data)
		self.esc_data['throttle_data'] = throttles

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
		power_on_time, health_status, current_mode = struct.unpack('<I2B', data)
		self.esc_data['heartbeat'] = {
		'power_on_time': power_on_time,
		'health_status': health_status,
		'current_mode': current_mode
		}

	def get_data(self):
		return self.esc_data

if __name__ == "__main__":
	
	esc_controller = CyphalCAN3()
	# esc_controller.send_command(node_id=0x10, command=0x01)
	# esc_controller.read_register(node_id=0x10, register_index=0x04)
	esc_controller.receive_data()
	data = esc_controller.get_data()
	print(data)

