#include <SPI.h>
#include "mcp_can.h"

// Define the CS pin for the CAN module
#define CAN0_CS 17

// Define dummy data for different commands
unsigned long txId;
unsigned char len = 8;
//constexpr unsigned long commands[8] = {0x2B1A, 0x260A, 0x271A, 0x280A, 0x291A, 0x2A7A, 0x2D1A, 0x2C1A};
constexpr unsigned long commands[8] = {11018, 9738, 9994, 10250, 10506, 10762, 11530, 11274};

// Instantiate the CAN object
MCP_CAN CAN0(CAN0_CS);

void setup() 
{
  // Start serial communication
  Serial.begin(115200);

  delay(10000);

  // Initialize CAN bus at 500 kbps
  if (CAN0.begin(CAN_500KBPS) == CAN_OK) 
  {
    Serial.println("CAN BUS Shield initialized successfully!");
  } 
  else 
  {
    Serial.println("CAN BUS Shield initialization failed...");
    while (1);
  }

  // Set the CAN filter and mask to allow all messages
  CAN0.init_Mask(0, 0, 0x00000000);  // Initialize mask 0
  CAN0.init_Mask(1, 0, 0x00000000);  // Initialize mask 1
  CAN0.init_Filt(0, 0, 0x00000000);  // Initialize filter 0
  CAN0.init_Filt(1, 0, 0x00000000);  // Initialize filter 1
  CAN0.init_Filt(2, 0, 0x00000000);  // Initialize filter 2
  CAN0.init_Filt(3, 0, 0x00000000);  // Initialize filter 3
  CAN0.init_Filt(4, 0, 0x00000000);  // Initialize filter 4
  CAN0.init_Filt(5, 0, 0x00000000);  // Initialize filter 5
}

void loop() 
{
  static unsigned long lastSent = 0;

  unsigned long now = millis();
  
  if (now - lastSent >= 10)
  { // Send data every second
    for (unsigned char unit_id = 0; unit_id < 6; ++unit_id) 
    {  // Loop through each unit
      for (unsigned char i = 0; i < 8; ++i) 
      {
        setCommandData(commands[i], unit_id);
        delay(1); // Small delay between commands
      }
    }
    lastSent = now;
  }
}

// Function to calculate CAN ID
unsigned long calculateCanId(unsigned char controller_id, unsigned long command) 
{
  uint32_t CAN_ID = (0 << 26) | (((command >> 8) & 0xFF) << 8) | controller_id; //(((command >> 8) & 0xFF) << 8)
  return CAN_ID;
}

// Function to send CAN frame
void sendDummyData(unsigned long id, unsigned char len, unsigned char *data) 
{
  if (CAN0.sendMsgBuf(id, 1, len, data) == CAN_OK) 
  {
    Serial.print(id);
    Serial.print("\t");
    Serial.print(len);
    Serial.print("\t");
    Serial.print(sizeof(data));
    Serial.print("\t");

    for(int i = 0; i < len; i++)
    {
      Serial.print(data[i]);
      Serial.print("\t");
    }
    
    Serial.println("Message Sent Successfully!");
  } 
  else 
  {
    Serial.print(id);
    Serial.print("\t");
    Serial.print(len);
    Serial.print("\t");
    Serial.print(sizeof(data));
    Serial.print("\t");

    for(int i = 0; i < len; i++)
    {
      Serial.print(data[i]);
      Serial.print("\t");
    }
    Serial.println("Error Sending Message...");
  }
}

// Function to set data for different commands for a specific unit
void setCommandData(unsigned long command, unsigned char unit_id) 
{
    txId = calculateCanId(unit_id, command);
    unsigned char data[8];
    
    /*if (command == commands[0]) // CAN_PACKET_BMS_TEMPS
    {
        Serial.print("CMD:0 ");
        len = 8;
        data[0] = 0;
        data[1] = 24;  // NoOfCells
        int16_t aux1 = 1234;  // 12.34V
        int16_t aux2 = 5678;  // 56.78V
        int16_t aux3 = 9101;  // 91.01V
        memcpy(data + 2, &aux1, 2);
        memcpy(data + 4, &aux2, 2);
        memcpy(data + 6, &aux3, 2);
        sendDummyData(txId, len, data);
    }*/
    if (command == commands[0]) // CAN_PACKET_BMS_TEMPS
    {
        Serial.print("CMD:0 ");
        len = 8;
        uint8_t totalNoOfAux = 24;  // Assuming totalNoOfAux is 24
        static uint8_t auxPointer = 0;  // Keep track of aux pointer across calls

        while (auxPointer < totalNoOfAux) 
        {
          // Prepare the data buffer
          data[0] = auxPointer;  // Aux point
          data[1] = totalNoOfAux;  // NoOfCells

          // Fill the data buffer with aux voltages
          if (auxPointer < totalNoOfAux) 
          {
            int16_t auxVoltage = 1234 + auxPointer * 10;  // Simulate aux voltage
            memcpy(data + 2, &auxVoltage, 2);
            auxPointer++;
          } 
          else 
          {
            memset(data + 2, 0, 2);  // Fill with zeros if no more aux
          }

          if (auxPointer < totalNoOfAux) 
          {
            int16_t auxVoltage = 5678 + auxPointer * 10;  // Simulate aux voltage
            memcpy(data + 4, &auxVoltage, 2);
            auxPointer++;
          } 
          else 
          {
            memset(data + 4, 0, 2);  // Fill with zeros if no more aux
          }

          if (auxPointer < totalNoOfAux) 
          {
            int16_t auxVoltage = 9101 + auxPointer * 10;  // Simulate aux voltage
            memcpy(data + 6, &auxVoltage, 2);
            auxPointer++;
          } 
          else 
          {
            memset(data + 6, 0, 2);  // Fill with zeros if no more aux
          }

          // Transmit the data
          sendDummyData(txId, len, data);

          // Reset auxPointer if it reaches the end of aux
          if (auxPointer >= totalNoOfAux) 
          {
            auxPointer = 0;
          }
        }
    }
    else if (command == commands[1]) // CAN_PACKET_BMS_V_TOT
    {
        Serial.print("CMD:1 ");
        len = 8;
        int32_t packVoltage = 100000;  // 100.0V
        int32_t chargerVoltage = 50000;  // 50.0V
        memcpy(data, &packVoltage, 4);
        memcpy(data + 4, &chargerVoltage, 4);
        sendDummyData(txId, len, data);
    }
    else if (command == commands[2]) // CAN_PACKET_BMS_I
    {
        Serial.print("CMD:2 ");
        len = 8;
        int32_t packCurrent1 = 5000;  // 50.0A
        int32_t packCurrent2 = -2000;  // -20.0A (discharging)
        memcpy(data, &packCurrent1, 4);
        memcpy(data + 4, &packCurrent2, 4);
        sendDummyData(txId, len, data);
    }
    else if (command == commands[3]) // CAN_PACKET_BMS_AH_WH
    {
        Serial.print("CMD:3 ");
        len = 8;
        int32_t Ah_Counter = 15000;  // 15.0 Ah
        int32_t Wh_Counter = 450000;  // 450.0 Wh
        memcpy(data, &Ah_Counter, 4);
        memcpy(data + 4, &Wh_Counter, 4);
        sendDummyData(txId, len, data);
    }
    /*else if (command == commands[4]) // CAN_PACKET_BMS_V_CELL
    {
        Serial.print("CMD:4 ");
        len = 8;
        data[0] = 24;  // cellPoint
        data[1] = 24;  // NoOfCells
        int16_t cellVoltage1 = 3700;  // 3.7V
        int16_t cellVoltage2 = 3800;  // 3.8V
        int16_t cellVoltage3 = 3900;  // 3.9V
        memcpy(data + 2, &cellVoltage1, 2);
        memcpy(data + 4, &cellVoltage2, 2);
        memcpy(data + 6, &cellVoltage3, 2);
    }*/
    else if (command == commands[4]) // CAN_PACKET_BMS_V_CELL
    {
      Serial.print("CMD:4 ");
      len = 8;

      uint8_t totalNoOfCells = 24;  // Assuming totalNoOfCells is 24
      static uint8_t cellPointer = 0;  // Keep track of cell pointer across calls

      // Prepare the data buffer
      data[0] = cellPointer;  // cellPoint
      data[1] = totalNoOfCells;  // NoOfCells

      while (cellPointer < totalNoOfCells) 
      {
        // Fill the data buffer with cell voltages
        if (cellPointer < totalNoOfCells) 
        {
          int16_t cellVoltage = 3700 + cellPointer * 10;  // Simulate cell voltage
          memcpy(data + 2, &cellVoltage, 2);
          cellPointer++;
        } 
        else 
        {
          memset(data + 2, 0, 2);  // Fill with zeros if no more cells
        }

        if (cellPointer < totalNoOfCells) 
        {
          int16_t cellVoltage = 3700 + cellPointer * 10;  // Simulate cell voltage
          memcpy(data + 4, &cellVoltage, 2);
          cellPointer++;
        } 
        else 
        {
          memset(data + 4, 0, 2);  // Fill with zeros if no more cells
        }

        if (cellPointer < totalNoOfCells) 
        {
          int16_t cellVoltage = 3700 + cellPointer * 10;  // Simulate cell voltage
          memcpy(data + 6, &cellVoltage, 2);
          cellPointer++;
        } 
        else 
        {
          memset(data + 6, 0, 2);  // Fill with zeros if no more cells
        }

        // Transmit the data
        sendDummyData(txId, len, data);

        // Reset cellPointer if it reaches the end of cells
        if (cellPointer >= totalNoOfCells) 
        {
          cellPointer = 0;
        }
      }
    }
    else if (command == commands[5]) // CAN_PACKET_BMS_BAL
    {
        Serial.print("CMD:5 ");
        len = 8;
        data[0] = 24;  // NoOfCells
        // Value between 0 and 100
        uint8_t value = 42;

        // Map the value to a 56-bit number
        uint64_t bal_state = mapTo56Bit(value);

        // Split the number into 7 slots
        for (int i = 0; i < 7; ++i) 
        {
            data[i + 1] = (bal_state >> (8 * i)) & 0xFF;
        }
        sendDummyData(txId, len, data);
    }
    else if (command == commands[6]) // CAN_PACKET_BMS_SOC_SOH_TEMP_STAT
    {
        Serial.print("CMD:6 ");
        len = 8;
        int16_t cellVoltageLow = 3000;  // 3.0V
        int16_t cellVoltageHigh = 4200;  // 4.2V
        data[0] = (cellVoltageLow >> 8) & 0xFF; data[1] = cellVoltageLow & 0xFF;
        data[2] = (cellVoltageHigh >> 8) & 0xFF; data[3] = cellVoltageHigh & 0xFF;
        data[4] = static_cast<uint8_t>(80 / 0.392156862745098);  // SOC 80%
        data[5] = static_cast<uint8_t>(90 / 0.3922);  // SOH 90%
        data[6] = 30;  // tBattHi 30°C
        data[7] = 0;  // BitF
        sendDummyData(txId, len, data);
    }
    else if (command == commands[7]) // CAN_PACKET_BMS_HUM
    {
        Serial.print("CMD:7 ");
        len = 6;
        int16_t temp0 = 2500;  // 25.0°C
        int16_t humidity = 5000;  // 50.0%
        int16_t temp1 = 2600;  // 26.0°C
        memcpy(data, &temp0, 2);
        memcpy(data + 2, &humidity, 2);
        memcpy(data + 4, &temp1, 2);
        sendDummyData(txId, len, data);
    }
}

uint64_t mapTo56Bit(uint8_t value) 
{
    // Scale the value to fit in the range of a 56-bit number
    // Maximum value for 56-bit number: 2^56 - 1
    uint64_t max_56_bit = (1ULL << 56) - 1;
    return (value * max_56_bit) / 100;
}