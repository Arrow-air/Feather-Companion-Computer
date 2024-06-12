import CyphalCAN3 as CyphalCAN
import asyncio

class ESC:

    def __init__(self,modeselect) -> None:

        self.modeselect = modeselect
        self.mode = {0:'GCS',1:'FUI'}
        
        self.packet = {}
        self.superDictionary = {}
        '''
            {'0': {'throttle_data': [100, 200, 300, 0], 'unit_id': 1922320, 'info_upload_6160': {'electrical_speed': 17874, 'bus_current': -28950, 'running_status': 276}, 
            'info_upload_6161': {'output_throttle': 55522, 'bus_voltage': 27311, 'temperatures': {'MOS': -13, 'Capacitance': 38, 'Motor': 99}}, 
            'heartbeat': {'power_on_time': 1310720000, 'health_status': 0, 'current_mode': 2}}, '1': {'throttle_data': [100, 200, 300, 0], 'unit_id': 1922321, 
            'info_upload_6160': {'electrical_speed': 40760, 'bus_current': 21069, 'running_status': 276}, 'info_upload_6161': {'output_throttle': 13643, 'bus_voltage': -160, 'temperatures': {'MOS': -23, 'Capacitance': 207, 'Motor': 40}}, 
            'heartbeat': {'power_on_time': 1310720000, 'health_status': 2, 'current_mode': 1}}, '2': {'throttle_data': [100, 200, 300, 0], 'unit_id': 1922322, 
            'info_upload_6160': {'electrical_speed': 27304, 'bus_current': -4973, 'running_status': 276}, 'info_upload_6161': {'output_throttle': 29021, 'bus_voltage': -10915, 'temperatures': {'MOS': 82, 'Capacitance': 3, 'Motor': -8}}, 
            'heartbeat': {'power_on_time': 1310720000, 'health_status': 1, 'current_mode': 3}}, '3': {'throttle_data': [100, 200, 300, 0], 'unit_id': 1922323, 'info_upload_6160': {'electrical_speed': 24129, 'bus_current': 12841, 'running_status': 276}, 
            'info_upload_6161': {'output_throttle': 46188, 'bus_voltage': 13616, 'temperatures': {'MOS': 203, 'Capacitance': 60, 'Motor': 194}}, 'heartbeat': {'power_on_time': 1327497216, 'health_status': 3, 'current_mode': 2}}, 
            '4': {'throttle_data': [100, 200, 300, 0], 'unit_id': 1922324, 'info_upload_6160': {'electrical_speed': 22952, 'bus_current': -13042, 'running_status': 276}, 'info_upload_6161': {'output_throttle': 49754, 'bus_voltage': 7367, 'temperatures': {'MOS': 91, 'Capacitance': 138, 'Motor': 209}}, 
            'heartbeat': {'power_on_time': 1327497216, 'health_status': 3, 'current_mode': 3}}, '5': {'throttle_data': [100, 200, 300, 0], 'unit_id': 1922325, 
            'info_upload_6160': {'electrical_speed': 47445, 'bus_current': -14407, 'running_status': 276}, 'info_upload_6161': {'output_throttle': 58803, 'bus_voltage': -16785, 'temperatures': {'MOS': -8, 'Capacitance': 3, 'Motor': 147}}, 
            'heartbeat': {'power_on_time': 1327497216, 'health_status': 0, 'current_mode': 2}}}
        '''

        self.superpacket = {'command_control':{'command': '', 'node_id': 0}, 'throttle_data':0,'info_upload_6160':{'electrical_speed': 0,'bus_current': 0,'running_status': 0},
                           'info_upload_6161': {'output_throttle': 0,'bus_voltage': 0,'temperatures': 0},'heartbeat': {'power_on_time': 0,'health_status': 0,'current_mode': 0}}

        self.dataDictionary = {'ESC1_temp_Ce':0, 'ESC2_temp_Ce':0,'ESC3_temp_Ce':0,'ESC4_temp_Ce':0,'ESC5_temp_Ce':0,'ESC6_temp_Ce':0,
                               'MOT1_temp_Ce':0,'MOT2_temp_Ce':0,'MOT3_temp_Ce':0,'MOT4_temp_Ce':0,'MOT5_temp_Ce':0,'MOT6_temp_Ce':0,
                               'MOT1_rpm_PCTe':0,'MOT2_rpm_PCTe':0,'MOT3_rpm_PCTe':0,'MOT4_rpm_PCTe':0,'MOT5_rpm_PCTe':0,'MOT6_rpm_PCTe':0,
                               'ESC1_Ve':0,'ESC2_Ve':0,'ESC3_Ve':0,'ESC4_Ve':0,'ESC5_Ve':0,'ESC6_Ve':0,
                               'ESC1_CUR_AMPe':0,'ESC2_CUR_AMPe':0,'ESC3_CUR_AMPe':0,'ESC4_CUR_AMPe':0,'ESC5_CUR_AMPe':0,'ESC6_CUR_AMPe':0}
     
        self.esc = CyphalCAN.CyphalCAN3()


        print("ESC Init")

    def packetStruct(self):

        self.superDictionary = self.escRead()
        data = self.superDictionary

        for i in range(0,5):


            x = i + 1
            
            self.dataDictionary[f'MOT{x}_rpm_PCTe'] = data[f'{i}']['info_upload_6160']['electrical_speed']
            self.dataDictionary[f'ESC{x}_CUR_AMPe'] = data[f'{i}']['info_upload_6160']['bus_current']
            self.dataDictionary[f'ESC{x}_Ve'] = data[f'{i}']['info_upload_6161']['bus_voltage']
            self.dataDictionary[f'ESC{x}_temp_Ce'] = data[f'{i}']['info_upload_6161']['temperatures']['MOS']

        self.packet = self.dataDictionary
        
        #print(self.packet)
        
        return self.packet

    def escRead(self):
        
        self.esc.unitData = {'0':{},'1':{},'2':{},'3':{},'4':{},'5':{}}
        
        while len(self.esc.unitData['5']) < 5:
			
            self.esc.esc_data = {}
            
            self.esc.receive_data()
            rawData = self.esc.get_data()
            
            if rawData['unit_id'] - 0x180810 == 0 or rawData['unit_id'] - 0x180910 == 0 or rawData['unit_id'] - 0x181010 == 0 or rawData['unit_id'] - 0x181110 == 0 or rawData['unit_id'] - 0x1D5510 == 0:
                self.esc.unitData['0'] |= rawData
            elif rawData['unit_id'] - 0x180810 == 1 or rawData['unit_id'] - 0x180910 == 1 or rawData['unit_id'] - 0x181010 == 1 or rawData['unit_id'] - 0x181110 == 1 or rawData['unit_id'] - 0x1D5510 == 1:
                self.esc.unitData['1'] |= rawData
            elif rawData['unit_id'] - 0x180810 == 2 or rawData['unit_id'] - 0x180910 == 2 or rawData['unit_id'] - 0x181010 == 2 or rawData['unit_id'] - 0x181110 == 2 or rawData['unit_id'] - 0x1D5510 == 2:
                self.esc.unitData['2'] |= rawData
            elif rawData['unit_id'] - 0x180810 == 3 or rawData['unit_id'] - 0x180910 == 3 or rawData['unit_id'] - 0x181010 == 3 or rawData['unit_id'] - 0x181110 == 3 or rawData['unit_id'] - 0x1D5510 == 3:
                self.esc.unitData['3'] |= rawData
            elif rawData['unit_id'] - 0x180810 == 4 or rawData['unit_id'] - 0x180910 == 4 or rawData['unit_id'] - 0x181010 == 4 or rawData['unit_id'] - 0x181110 == 4 or rawData['unit_id'] - 0x1D5510 == 4:
                self.esc.unitData['4'] |= rawData
            elif rawData['unit_id'] - 0x180810 == 5 or rawData['unit_id'] - 0x180910 == 5 or rawData['unit_id'] - 0x181010 == 5 or rawData['unit_id'] - 0x181110 == 5 or rawData['unit_id'] - 0x1D5510 == 5:
                self.esc.unitData['5'] |= rawData
        
        return self.esc.unitData

if __name__ == "__main__":
    
    esc = ESC('FUI')
    
    while True:
        
        esc.packetStruct()
        
        print("\n")
