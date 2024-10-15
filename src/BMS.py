import VESCCAN
import random
import time

class BMS:

    def __init__(self,modeselect) -> None:
        
        self.modeselect = modeselect
        self.mode = {0:'GCS',1:'FUI'}
        
        self.vesc = VESCCAN.VESCCAN()

        self.packet = {}
        self.rawData = {}
        #self.previous_packet = None
        self.last_update_time = 0
        self.external_update_rate = 1.1

        '''
        self.dataDictionary = {'BAT1_temp_C':0,'BAT2_temp_C':0,'BAT3_temp_C':0,'BAT4_temp_C':0,'BAT5_temp_C':0,'BAT6_temp_C':0,'ESC1_temp_C':0,
                               'ESC2_temp_C':0,'ESC3_temp_C':0,'ESC4_temp_C':0,'ESC5_temp_C':0,'ESC6_temp_C':0,'MOT1_temp_C':0,'MOT2_temp_C':0,
                               'MOT3_temp_C':0,'MOT4_temp_C':0,'MOT5_temp_C':0,'MOT6_temp_C':0,'BAT1_soc_PCT':0,'BAT2_soc_PCT':0,'BAT3_soc_PCT':0,
                               'BAT4_soc_PCT':0,'BAT5_soc_PCT':0,'BAT6_soc_PCT':0,'MOT1_rpm_PCT':0,'MOT2_rpm_PCT':0,'MOT3_rpm_PCT':0,'MOT4_rpm_PCT':0,
                               'MOT5_rpm_PCT':0,'MOT6_rpm_PCT':0,'ESC1_V':0,'ESC2_V':0,'ESC3_V':0,'ESC4_V':0,'ESC5_V':0,'ESC6_V':0,'ESC1_CUR_AMP':0,
                               'ESC2_CUR_AMP':0,'ESC3_CUR_AMP':0,'ESC4_CUR_AMP':0,'ESC5_CUR_AMP':0,'ESC6_CUR_AMP':0}
        '''
        
        ''' RAW BMS Data Dictionary '''
        self.previous_packet = {'0': {'unit_id': 0, 'NoOfCells': 0, 'auxVoltagesIndividual1': 46.6, 'auxVoltagesIndividual2': 221.36, 'auxVoltagesIndividual3': 396.12, 'packVoltage': 279183360, 'chargerVoltage': 1354956800, 
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
        
        
        self.dataDictionary = {'BAT1_temp_C':0,'BAT2_temp_C':0,'BAT3_temp_C':0,'BAT4_temp_C':0,'BAT5_temp_C':0,'BAT6_temp_C':0,
                               'ESC1_temp_C':0,'ESC2_temp_C':0,'ESC3_temp_C':0,'ESC4_temp_C':0,'ESC5_temp_C':0,'ESC6_temp_C':0,
                               'MOT1_temp_C':0,'MOT2_temp_C':0,'MOT3_temp_C':0,'MOT4_temp_C':0,'MOT5_temp_C':0,'MOT6_temp_C':0,
                               'BAT1_soc_PCT':0,'BAT2_soc_PCT':0,'BAT3_soc_PCT':0,'BAT4_soc_PCT':0,'BAT5_soc_PCT':0,'BAT6_soc_PCT':0,
                               'MOT1_rpm_PCT':0,'MOT2_rpm_PCT':0,'MOT3_rpm_PCT':0,'MOT4_rpm_PCT':0,'MOT5_rpm_PCT':0,'MOT6_rpm_PCT':0,
                               'ESC1_V':0,'ESC2_V':0,'ESC3_V':0,'ESC4_V':0,'ESC5_V':0,'ESC6_V':0,
                               'ESC1_CUR_AMP':0,'ESC2_CUR_AMP':0,'ESC3_CUR_AMP':0,'ESC4_CUR_AMP':0,'ESC5_CUR_AMP':0,'ESC6_CUR_AMP':0}
        
        print("BMS Init")

    def packetStruct(self):

        self.current_time = time.time()

        if self.current_time - self.last_update_time >= self.external_update_rate:
            self.packet = self.bmsRead()
            #print(str(self.packet))
            self.previous_packet = self.packet
            self.last_update_time = self.current_time

        self.packet = self.previous_packet

        try:
                for x in range(11,17):
                   
                   if self.packet[f'{x}']['unit_id'] == x:
                       y = x - 10
                       self.dataDictionary[f'BAT{y}_temp_C'] = self.packet[f'{y}']['CAN_PACKET_BMS_TEMP0']
                       self.dataDictionary[f'BAT{y}_soc_PCT'] = self.packet[f'{y}']['SOC']
                       self.dataDictionary[f'ESC{y}_V'] = self.packet[f'{y}']['packVoltage']
                       self.dataDictionary[f'ESC{y}_CUR_AMP'] = self.packet[f'{y}']['packCurrent1']
                
                self.packet = {key : round(int(self.dataDictionary[key])) for key in self.dataDictionary}
                
                #print(str(x) + str(self.packet))
                       
        except:
    
               self.packet = {'BAT1_temp_C':random.randint(0,100),'BAT2_temp_C':random.randint(0,100),'BAT3_temp_C':random.randint(0,100),'BAT4_temp_C':random.randint(0,100),'BAT5_temp_C':random.randint(0,100),'BAT6_temp_C':random.randint(0,100),'ESC1_temp_C':random.randint(0,100),
                               'ESC2_temp_C':0,'ESC3_temp_C':random.randint(0,100),'ESC4_temp_C':0,'ESC5_temp_C':0,'ESC6_temp_C':0,'MOT1_temp_C':0,'MOT2_temp_C':0,
                               'MOT3_temp_C':random.randint(0,100),'MOT4_temp_C':0,'MOT5_temp_C':0,'MOT6_temp_C':random.randint(0,100),'BAT1_soc_PCT':random.randint(0,100),'BAT2_soc_PCT':random.randint(0,100),'BAT3_soc_PCT':random.randint(0,100),
                               'BAT4_soc_PCT':random.randint(0,100),'BAT5_soc_PCT':0,'BAT6_soc_PCT':random.randint(0,100),'MOT1_rpm_PCT':0,'MOT2_rpm_PCT':0,'MOT3_rpm_PCT':0,'MOT4_rpm_PCT':0,
                               'MOT5_rpm_PCT':0,'MOT6_rpm_PCT':random.randint(0,100),'ESC1_V':0,'ESC2_V':0,'ESC3_V':0,'ESC4_V':0,'ESC5_V':0,'ESC6_V':random.randint(0,100),'ESC1_CUR_AMP':0,
                               'ESC2_CUR_AMP':0,'ESC3_CUR_AMP':0,'ESC4_CUR_AMP':0,'ESC5_CUR_AMP':random.randint(0,100),'ESC6_CUR_AMP':0}

        #print(self.packet) 
        return [self.packet,self.previous_packet]
    
    def bmsRead(self):
        
        self.vesc.unitData = {'1':{},'2':{},'3':{},'4':{},'5':{},'6':{}}
        
        while len(self.vesc.unitData['6']) < 28:
        
            self.rawData = self.vesc.read_frame()
            
            if self.rawData['unit_id'] == 11:
                self.vesc.unitData['1'] |= self.rawData
            elif self.rawData['unit_id'] == 12:
                self.vesc.unitData['2'] |= self.rawData
            elif self.rawData['unit_id'] == 13:
                self.vesc.unitData['3'] |= self.rawData
            elif self.rawData['unit_id'] == 14:
                self.vesc.unitData['4'] |= self.rawData
            elif self.rawData['unit_id'] == 15:
                self.vesc.unitData['5'] |= self.rawData
            elif self.rawData['unit_id'] == 16:
                self.vesc.unitData['6'] |= self.rawData

        return self.vesc.unitData

if __name__ == "__main__":
    
    bms = BMS('FUI')
    
    while True:
        
        bms.packetStruct()
        
        print(bms.packet)
        print("\n")

