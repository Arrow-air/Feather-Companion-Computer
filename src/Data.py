from datetime import datetime
import os
import threading

class Data:

    def __init__(self,TCP,modeselect) -> None:
        
        self.modeselect = modeselect
        self.mode = {0:'GCS',1:'FUI'}

        #self.Lora = Lora
        #self.Lora.LoRaconfig()
        
        self.TCP = TCP

        self.packet = {}
        self.dataString = ''
        
        self.tlock = threading.Lock()

        self.now = {'TimeStamp':0}

        self.JoystickPacket  = {'command_pitch':0.2,'command_roll':0,'command_yaw':0,'command_throttle':0.3,'switch_states':0}

        self.ParachutePacket = {'parachute_state':0}

        self.Veronteout = []
        self.VeronteLog = {}

        self.VerontePacket  = {'altitude_AGL':0,'altitude_AGL_set':0,'altitude_ABS':40,'heading':0,'compass':0,'attitude_pitch':0,'attitude_roll':0,'vertical_speed_KTS':0,
                               'airspeed_KTS':0,'OAT':0,'latitude':'40d26a46q','longitude':'79d58a56q','flight_time':'50:39'}
        
        self.BMSout = []

        self.BMSLog = {'0': {'unit_id': 0, 'NoOfCells': 0, 'auxVoltagesIndividual1': 46.6, 'auxVoltagesIndividual2': 221.36, 'auxVoltagesIndividual3': 396.12, 'packVoltage': 279183360, 'chargerVoltage': 1354956800, 
        'packCurrent1': 3892510720, 'packCurrent2': 3490119680, 'Ah_Counter': 4093706240, 'Wh_Counter': 3892510720, 'cellPoint': 24, 'cellVoltage10': 4.66, 'cellVoltage11': 22.136, 'cellVoltage12': 39.612, 
        'bal_state': 59109745109237, 'cellVoltageLow': 3.0, 'cellVoltageHigh': 4.2, 'SOC': 31.37254901960784, 'SOH': 35.298, 'tBattHi': 30, 'BitF': 0, 'CAN_PACKET_BMS_TEMP0': 501.85, 'CAN_PACKET_BMS_HUM_HUM': 348.35, 'CAN_PACKET_BMS_HUM_TEMP1': 102.5}, 
        '1': {'unit_id': 1, 'NoOfCells': 0, 'auxVoltagesIndividual1': 46.6, 'auxVoltagesIndividual2': 221.36, 'auxVoltagesIndividual3': 396.12, 'packVoltage': 279183360, 'chargerVoltage': 1354956800, 
        'packCurrent1': 3892510720, 'packCurrent2': 3490119680, 'Ah_Counter': 4093706240, 'Wh_Counter': 3892510720, 'cellPoint': 24, 'cellVoltage10': 4.66, 'cellVoltage11': 22.136, 'cellVoltage12': 39.612, 
        'bal_state': 59109745109237, 'cellVoltageLow': 3.0, 'cellVoltageHigh': 4.2, 'SOC': 31.37254901960784, 'SOH': 35.298, 'tBattHi': 30, 'BitF': 0, 'CAN_PACKET_BMS_TEMP0': 501.85, 'CAN_PACKET_BMS_HUM_HUM': 348.35, 'CAN_PACKET_BMS_HUM_TEMP1': 102.5}, 
        '2': {'unit_id': 2, 'NoOfCells': 0, 'auxVoltagesIndividual1': 46.6, 'auxVoltagesIndividual2': 221.36, 'auxVoltagesIndividual3': 396.12, 'packVoltage': 279183360, 'chargerVoltage': 1354956800, 
        'packCurrent1': 3892510720, 'packCurrent2': 3490119680, 'Ah_Counter': 4093706240, 'Wh_Counter': 3892510720, 'cellPoint': 24, 'cellVoltage10': 4.66, 'cellVoltage11': 22.136, 'cellVoltage12': 39.612, 
        'bal_state': 59109745109237, 'cellVoltageLow': 3.0, 'cellVoltageHigh': 4.2, 'SOC': 31.37254901960784, 'SOH': 35.298, 'tBattHi': 30, 'BitF': 0, 'CAN_PACKET_BMS_TEMP0': 501.85, 'CAN_PACKET_BMS_HUM_HUM': 348.35, 'CAN_PACKET_BMS_HUM_TEMP1': 102.5}, 
        '3': {'unit_id': 3, 'NoOfCells': 0, 'auxVoltagesIndividual1': 46.6, 'auxVoltagesIndividual2': 221.36, 'auxVoltagesIndividual3': 396.12, 'packVoltage': 279183360, 'chargerVoltage': 1354956800, 
        'packCurrent1': 3892510720, 'packCurrent2': 3490119680, 'Ah_Counter': 4093706240, 'Wh_Counter': 3892510720, 'cellPoint': 24, 'cellVoltage10': 4.66, 'cellVoltage11': 22.136, 'cellVoltage12': 39.612, 
        'bal_state': 59109745109237, 'cellVoltageLow': 3.0, 'cellVoltageHigh': 4.2, 'SOC': 31.37254901960784, 'SOH': 35.298, 'tBattHi': 30, 'BitF': 0, 'CAN_PACKET_BMS_TEMP0': 501.85, 'CAN_PACKET_BMS_HUM_HUM': 348.35, 'CAN_PACKET_BMS_HUM_TEMP1': 102.5}, 
        '4': {'unit_id': 4, 'NoOfCells': 0, 'auxVoltagesIndividual1': 46.6, 'auxVoltagesIndividual2': 221.36, 'auxVoltagesIndividual3': 396.12, 'packVoltage': 279183360, 'chargerVoltage': 1354956800, 
        'packCurrent1': 3892510720, 'packCurrent2': 3490119680, 'Ah_Counter': 4093706240, 'Wh_Counter': 3892510720, 'cellPoint': 24, 'cellVoltage10': 4.66, 'cellVoltage11': 22.136, 'cellVoltage12': 39.612, 
        'bal_state': 59109745109237, 'cellVoltageLow': 3.0, 'cellVoltageHigh': 4.2, 'SOC': 31.37254901960784, 'SOH': 35.298, 'tBattHi': 30, 'BitF': 0, 'CAN_PACKET_BMS_TEMP0': 501.85, 'CAN_PACKET_BMS_HUM_HUM': 348.35, 'CAN_PACKET_BMS_HUM_TEMP1': 102.5}, 
        '5': {'unit_id': 5, 'NoOfCells': 0, 'auxVoltagesIndividual1': 46.6, 'auxVoltagesIndividual2': 221.36, 'auxVoltagesIndividual3': 396.12, 'packVoltage': 279183360, 'chargerVoltage': 1354956800, 
        'packCurrent1': 3892510720, 'packCurrent2': 3490119680, 'Ah_Counter': 4093706240, 'Wh_Counter': 3892510720, 'cellPoint': 24, 'cellVoltage10': 4.66, 'cellVoltage11': 22.136, 'cellVoltage12': 39.612, 
        'bal_state': 59109745109237, 'cellVoltageLow': 3.0, 'cellVoltageHigh': 4.2, 'SOC': 31.37254901960784, 'SOH': 35.298, 'tBattHi': 30, 'BitF': 0, 'CAN_PACKET_BMS_TEMP0': 501.85, 'CAN_PACKET_BMS_HUM_HUM': 348.35, 'CAN_PACKET_BMS_HUM_TEMP1': 102.5}}

        self.BMSPacket  = {'BAT1_temp_C':0,'BAT2_temp_C':30,'BAT3_temp_C':0,'BAT4_temp_C':0,'BAT5_temp_C':0,'BAT6_temp_C':0,'ESC1_temp_C':0,
                               'ESC2_temp_C':0,'ESC3_temp_C':0,'ESC4_temp_C':0,'ESC5_temp_C':0,'ESC6_temp_C':0,'MOT1_temp_C':0,'MOT2_temp_C':0,
                               'MOT3_temp_C':0,'MOT4_temp_C':0,'MOT5_temp_C':60,'MOT6_temp_C':0,'BAT1_soc_PCT':0,'BAT2_soc_PCT':0,'BAT3_soc_PCT':0,
                               'BAT4_soc_PCT':0,'BAT5_soc_PCT':0,'BAT6_soc_PCT':0,'MOT1_rpm_PCT':0,'MOT2_rpm_PCT':0,'MOT3_rpm_PCT':0,'MOT4_rpm_PCT':0,
                               'MOT5_rpm_PCT':100,'MOT6_rpm_PCT':50,'ESC1_V':0,'ESC2_V':0,'ESC3_V':0,'ESC4_V':0,'ESC5_V':0,'ESC6_V':100,'ESC1_CUR_AMP':0,
                               'ESC2_CUR_AMP':0,'ESC3_CUR_AMP':0,'ESC4_CUR_AMP':0,'ESC5_CUR_AMP':0,'ESC6_CUR_AMP':0}

        self.ESCout = []

        self.ESCLog = {'0': {'throttle_data': [100, 200, 300, 0], 'unit_id': 1922320, 'info_upload_6160': {'electrical_speed': 17874, 'bus_current': -28950, 'running_status': 276}, 
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
        
        self.ESCPacket = {'ESC1_temp_Ce':100, 'ESC2_temp_Ce':100,'ESC3_temp_Ce':80,'ESC4_temp_Ce':70,'ESC5_temp_Ce':90,'ESC6_temp_Ce':70,
                          'MOT1_temp_Ce':100,'MOT2_temp_Ce':100,'MOT3_temp_Ce':100,'MOT4_temp_Ce':0,'MOT5_temp_Ce':0,'MOT6_temp_Ce':70,
                          'MOT1_rpm_PCTe':100,'MOT2_rpm_PCTe':100,'MOT3_rpm_PCTe':1000,'MOT4_rpm_PCTe':0,'MOT5_rpm_PCTe':0,'MOT6_rpm_PCTe':0,
                          'ESC1_Ve':100,'ESC2_Ve':0,'ESC3_Ve':100,'ESC4_Ve':50,'ESC5_Ve':50,'ESC6_Ve':50,
                          'ESC1_CUR_AMPe':100,'ESC2_CUR_AMPe':100,'ESC3_CUR_AMPe':100,'ESC4_CUR_AMPe':100,'ESC5_CUR_AMPe':100,'ESC6_CUR_AMPe':100}
        
        self.IOPacket = {}

        self.dataDictionary = {}

        
        self.parameters = {
            "altitude_AGL":0,
            "altitude_AGL_set":0,
            "altitude_ABS":0,
            "heading":0,
            "compass":0,
            "attitude_pitch":0, # forward-backward rotation of the aircraft itself, in what angle the aircraft is leaning to forward or backward, range: -180 to 180(minus is leaning backward, positive is leaning forward)
            "attitude_roll":0, # right-left rotation of the aircraft itself, in what angle the aircraft is leaning side wise, range: -180 to 180(minus is leaning to the left side, positive is to the right side)
            "vertical_speed_KTS":0,
            "airspeed_KTS":0, # warning range: 55-60,-60-(-55), [kts], speed will be between 0-60 knots
            "OAT":0, # warning range: 30-max=100
            "latitude":'40d26a46q',
            'longitude':'79d58a56q',
            "flight_time":'59:39',

            "command_pitch":0, # right joystick, up-down, range: -1 to 1
            "command_roll":0, # right joystick, left-right, range: -1 to 1
            "command_throttle":0, # left joystick, up-down, range: -1 to 1
            "command_yaw":0, # left joystick, left-right, range: -1 to 1
            "switch_states":0,

            "parachute_state":0,

            "BAT1_temp_C":0, # warning range: 80-180
            "BAT2_temp_C":0, # warning range: 80-180
            "BAT3_temp_C":0, # warning range: 80-180
            "BAT4_temp_C":0, # warning range: 80-180
            "BAT5_temp_C":0, # warning range: 80-180
            "BAT6_temp_C":0, # warning range: 80-180

            "ESC1_temp_C":0,
            "ESC2_temp_C":0,
            "ESC3_temp_C":0,
            "ESC4_temp_C":0,
            "ESC5_temp_C":0,
            "ESC6_temp_C":0,

            "MOT1_temp_C":0,
            "MOT2_temp_C":0,
            "MOT3_temp_C":0,
            "MOT4_temp_C":0,
            "MOT5_temp_C":0,
            "MOT6_temp_C":0,

            "BAT1_soc_PCT":10, # the percentage of the battery left, warning range: 1-15
            "BAT2_soc_PCT":20, # the percentage of the battery left, warning range: 1-15
            "BAT3_soc_PCT":30, # the percentage of the battery left, warning range: 1-15
            "BAT4_soc_PCT":40, # the percentage of the battery left, warning range: 1-15
            "BAT5_soc_PCT":50, # the percentage of the battery left, warning range: 1-15
            "BAT6_soc_PCT":60, # the percentage of the battery left, warning range: 1-15

            "MOT1_rpm_PCT":2000, # warning range: 120-max=140
            "MOT2_rpm_PCT":3000, # warning range: 120-max=140
            "MOT3_rpm_PCT":3000, # warning range: 120-max=140
            "MOT4_rpm_PCT":2000, # warning range: 120-max=140
            "MOT5_rpm_PCT":3000, # warning range: 120-max=140
            "MOT6_rpm_PCT":3000, # warning range: 120-max=140

            "ESC1_V":100,
            "ESC2_V":100,
            "ESC3_V":100,
            "ESC4_V":100,
            "ESC5_V":100,
            "ESC6_V":100,
            
            "ESC1_CUR_AMP":150,
            "ESC2_CUR_AMP":150,
            "ESC3_CUR_AMP":150,
            "ESC4_CUR_AMP":150,
            "ESC5_CUR_AMP":150,
            "ESC6_CUR_AMP":150,
            "TimeStamp":0
        }

        try:
            os.mkdir('./Logs')
        except OSError as error:
            pass

        self.Starttimestamp = str(datetime.now().year)+ '_' + str(datetime.now().month)+ '_' + str(datetime.now().day) + '-' + str(datetime.now().hour) + '_' + str(datetime.now().minute)

        self.logFile = open('./Logs/FeatherFlightLog-'+self.Starttimestamp+'.csv','w',encoding='utf-8')
        
        print("Data Init")
    
        
    def packetStruct(self):
        
        self.VerontePacket = self.Veronteout[0]
        self.VeronteLog = self.Veronteout[1]

        self.ESCPacket = self.ESCout[0]
        self.ESCLog = self.ESCout[1]

        self.BMSPacket = self.BMSout[0]
        self.BMSLog = self.BMSout[1]

        self.V = self.VerontePacket.keys()
        self.J = self.JoystickPacket.keys()
        self.B = self.BMSPacket.keys()
        self.E = self.ESCPacket.keys()
        
        for x in range(1,7):
            
                self.BMSPacket[f'MOT{x}_rpm_PCT'] = self.ESCPacket[f'MOT{x}_rpm_PCTe']
                self.BMSPacket[f'ESC{x}_CUR_AMP'] = self.ESCPacket[f'ESC{x}_CUR_AMPe']
                self.BMSPacket[f'ESC{x}_V'] = self.ESCPacket[f'ESC{x}_Ve']
                self.BMSPacket[f'ESC{x}_temp_C'] = self.ESCPacket[f'ESC{x}_temp_Ce']
                self.BMSPacket[f'MOT{x}_temp_C'] = self.ESCPacket[f'MOT{x}_temp_Ce']

        for key in self.V:
            self.parameters[key] = self.VerontePacket[key]
        for key in self.J:
            self.parameters[key] = self.JoystickPacket[key]
        for key in self.B:
            self.parameters[key] = self.BMSPacket[key]
        
        self.ParachutePacket['parachute_state'] = 0
        self.parameters['TimeStamp'] = self.now['TimeStamp']
        
        print(self.parameters)
        self.packet = self.parameters

    def logUpdate(self):
        
        self.logPacket = self.VerontePacket | self.VeronteLog | self.JoystickPacket | self.ParachutePacket | self.BMSLog | self.ESCLog | self.IOPacket | self.now
        #print(self.logPacket)
        self.logFile.write(str(self.logPacket) + '\n')
        
        return 0

    def telemetryUpdate(self):
        
        self.telemetryPacket = self.packet
        #with self.tlock:
        #self.Lora.packet = bytes(str(self.telemetryPacket) + '\n', 'ascii')
        #self.Lora.LoRaTransmit()
        self.TCP.packet = self.telemetryPacket
        self.TCP.TCPServer()
        return 0
    
    def gcsUpdate(self):
        
        self. dataString = self.TCP.TCPClient()
        self.packet = self.dataString
        #print(self.dataString)
        #selfdataDictionary = ast.literal_eval(self. dataString)
