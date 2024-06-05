import can
import struct
import time

class CyphalCAN2:
    def __init__(self, channel, bustype='socketcan', bitrate=500000):
        self.channel = channel
        self.bustype = bustype
        self.bitrate = bitrate
        self.can0 = can.interface.Bus(channel=self.channel, bustype=self.bustype, bitrate=self.bitrate)
        self.data_dict = {}

    def send_command(self, can_id, data):
        message = can.Message(arbitration_id=can_id, data=data, is_extended_id=True)
        self.can0.send(message)

    def read_message(self):
        message = self.can0.recv()
        if message:
            self.process_message(message)

    def process_message(self, message):
        can_id = message.arbitration_id
        data = message.data
        self.data_dict[can_id] = data

    def get_data(self):
        return self.data_dict

    def close(self):
        self.can0.shutdown()

    def start_communication(self, duration=10):
        start_time = time.time()
        while time.time() - start_time < duration:
            self.read_message()
        return self.get_data()

    # Example functions for ESC commands
    def set_throttle(self, node_id, throttle_values):
        can_id = 0x18000000 | (node_id << 8) | 0x152  # Example CAN ID based on PDF protocol
        data = self.pack_throttle_data(throttle_values)
        self.send_command(can_id, data)

    def pack_throttle_data(self, throttle_values):
        # Packing throttle data based on provided document's example
        # Assuming throttle_values is a list of four 14-bit values
        data = [0] * 7
        throt = throttle_values[:4]
        throt[0] &= 0x3FFF
        throt[1] &= 0x3FFF
        throt[2] &= 0x3FFF
        throt[3] &= 0x3FFF
        throt[0] |= ((throt[3] << 2) & 0xC000)
        throt[1] |= ((throt[3] << 4) & 0xC000)
        throt[2] |= ((throt[3] << 6) & 0xC000)
        data[0:2] = struct.pack('<H', throt[0])
        data[2:4] = struct.pack('<H', throt[1])
        data[4:6] = struct.pack('<H', throt[2])
        data[6] = throt[3] & 0xFF
        return data

    # New method to set node ID
    def set_node_id(self, old_node_id, new_node_id):
        can_id = 0x18000000 | (old_node_id << 8) | 0x145  # Example CAN ID for setting node ID
        data = struct.pack('<BB', 0, new_node_id)
        self.send_command(can_id, data)

    # Method to send a register read command
    def read_register(self, node_id, register_index):
        can_id = 0x18000000 | (node_id << 8) | 0x100  # Example CAN ID for reading a register
        data = struct.pack('<BB', 0, register_index)
        self.send_command(can_id, data)

    # Method to send a register write command
    def write_register(self, node_id, register_index, value):
        can_id = 0x18000000 | (node_id << 8) | 0x100  # Example CAN ID for writing to a register
        data = struct.pack('<BBH', 2, register_index, value)
        self.send_command(can_id, data)

    # Example of a more complex command
    def execute_command(self, node_id, command, parameter=None):
        can_id = 0x18000000 | (node_id << 8) | 0x1B3  # Example CAN ID for executing a command
        if parameter is None:
            data = struct.pack('<H', command)
        else:
            data = struct.pack('<HH', command, parameter)
        self.send_command(can_id, data)

# Usage example
if __name__ == "__main__":
    esc = CyphalCAN2(channel='can0')
    try:
        # Example: set throttle
        #esc.set_throttle(node_id=0x10, throttle_values=[0x123, 0x234, 0x345, 0x456])

        # Example: set node ID
        #esc.set_node_id(old_node_id=0x10, new_node_id=0x11)

        # Example: read register
        #esc.read_register(node_id=0x10, register_index=0x04)

        # Example: write register
        #esc.write_register(node_id=0x10, register_index=0x04, value=0x05)

        # Example: execute command
        #esc.execute_command(node_id=0x10, command=65535)  # Restart command

        # Start communication for 10 seconds
        data = esc.start_communication(duration=10)

        # Print the structured data
        print(data)
    finally:
        esc.close()
