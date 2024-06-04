#include <mcp_can.h>
#include <SPI.h>

#define CAN0_INT 2    // Set INT to pin 2
MCP_CAN CAN0(17);     // Set CS to pin 17

// Function to send throttle command
void sendThrottleCommand(uint8_t node_id, uint16_t throttle_values[4]) 
{
    uint32_t can_id = 0x18000000 | (node_id << 8) | 0x152;
    Serial.println(can_id,HEX);
    uint8_t data[8];
    
    // Pack throttle data
    throttle_values[0] &= 0x3FFF;
    throttle_values[1] &= 0x3FFF;
    throttle_values[2] &= 0x3FFF;
    throttle_values[3] &= 0x3FFF;
    throttle_values[0] |= ((throttle_values[3] << 2) & 0xC000);
    throttle_values[1] |= ((throttle_values[3] << 4) & 0xC000);
    throttle_values[2] |= ((throttle_values[3] << 6) & 0xC000);
    data[0] = throttle_values[0] & 0xFF;
    data[1] = (throttle_values[0] >> 8) & 0xFF;
    data[2] = throttle_values[1] & 0xFF;
    data[3] = (throttle_values[1] >> 8) & 0xFF;
    data[4] = throttle_values[2] & 0xFF;
    data[5] = (throttle_values[2] >> 8) & 0xFF;
    data[6] = throttle_values[3] & 0xFF;
    data[7] = 0xE0;

    CAN0.sendMsgBuf(can_id, 1, 8, data);
}

// Function to set node ID
void setNodeId(uint8_t old_node_id, uint8_t new_node_id) 
{
    uint32_t can_id = 0x18000000 | (old_node_id << 8) | 0x145;
    Serial.println(can_id,HEX);
    uint8_t data[3] = {0, new_node_id,0xE0};
    CAN0.sendMsgBuf(can_id, 1, 3, data);
}

// Function to read a register
void readRegister(uint8_t node_id, uint8_t register_index) 
{
    uint32_t can_id = 0x18000000 | (node_id << 8) | 0x100;
    uint8_t data[3] = {0, register_index,0xE0};
    CAN0.sendMsgBuf(can_id, 1, 3, data);
}

// Function to write a register
void writeRegister(uint8_t node_id, uint8_t register_index, uint16_t value) 
{
    uint32_t can_id = 0x18000000 | (node_id << 8) | 0x100;
    uint8_t data[5] = {2, register_index, lowByte(value), highByte(value),0xE0};
    CAN0.sendMsgBuf(can_id, 1, 5, data);
}

// Function to execute a command
void executeCommand(uint8_t node_id, uint16_t command, uint16_t parameter = 0) 
{
    uint32_t can_id = 0x18000000 | (node_id << 8) | 0x1B3;
    uint8_t data[5];
    if (parameter == 0) 
    {
        data[0] = lowByte(command);
        data[1] = highByte(command);
        data[2] = 0xE0;
        CAN0.sendMsgBuf(can_id, 1, 3, data);
    } 
    else
    {
        data[0] = lowByte(command);
        data[1] = highByte(command);
        data[2] = lowByte(parameter);
        data[3] = highByte(parameter);
        data[4] = 0xE0;
        CAN0.sendMsgBuf(can_id, 1, 5, data);
    }
}

void setup() 
{
    Serial.begin(115200);

    // Initialize MCP2515 running at 16MHz with a baudrate of 500kb/s
    if (CAN0.begin(CAN_500KBPS) == CAN_OK) 
    {
        Serial.println("MCP2515 Initialized Successfully!");
    } 
    else 
    {
        Serial.println("Error Initializing MCP2515...");
        while (1);
    }

    // Set INT pin
    pinMode(CAN0_INT, INPUT);
}

void loop() {
    // Example usage of the functions

    // Send throttle command
    //uint16_t throttle_values[4] = {0x123, 0x234, 0x345, 0x456};
    //sendThrottleCommand(0x10, throttle_values);

    // Set node ID
    setNodeId(0x10, 0x11);

    // Read register
    //readRegister(0x10, 0x04);

    // Write register
    //writeRegister(0x10, 0x04, 0x05);

    // Execute command
    //executeCommand(0x10, 65535);  // Restart command

    long unsigned int rxId;
    unsigned char len = 0;
    unsigned char rxBuf[8];

    // Listen for incoming CAN messages
    if (CAN0.readMsgBuf(&len, rxBuf) == CAN_OK) 
    {
      rxId = CAN0.getCanId();

        Serial.print("Received ID: ");
        Serial.print(rxId, HEX);
        Serial.print(" Data: ");
        for (int i = 0; i < len; i++) 
        {
            Serial.print(rxBuf[i], HEX);
            Serial.print(" ");
        }
        Serial.println();
    }

    delay(1000); // Delay for demonstration
}