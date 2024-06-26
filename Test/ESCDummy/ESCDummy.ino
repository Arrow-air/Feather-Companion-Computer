#include <mcp_can.h>
#include <SPI.h>

const int CAN0_CS = 17;

MCP_CAN CAN0(CAN0_CS);

void setup() 
{
  Serial.begin(115200);
  delay(10000);

  while (CAN_OK != CAN0.begin(CAN_500KBPS)) 
  {
    Serial.println("CAN BUS Shield init fail");
    Serial.println(" Init CAN BUS Shield again");
    delay(100);
  }
  Serial.println("CAN BUS Shield init ok!");
}

uint8_t tid = 0;
uint8_t nodeID = 0x10;
uint8_t idinc = 0;

void loop() 
{
  byte Tailbyte;
  byte SET = 0b11100000;

  Tailbyte = SET | (tid & 0x1F);

  //sendCommandControl(Tailbyte);
  //tid++;
  //delay(10);

  //setDeviceID(Tailbyte);
  //tid++;
  //delay(1);

  sendThrottleData(Tailbyte,nodeID + idinc);
  tid++;
  delay(1);

  sendInfoUpload6160(Tailbyte,nodeID + idinc);
  tid++;
  delay(1);

  sendInfoUpload6161(Tailbyte,nodeID + idinc);
  tid++;
  delay(1);

  sendHeartbeat(Tailbyte,nodeID + idinc);
  tid++;
  delay(1);

  idinc++;

  if(tid > 31)
  {
    tid = 0;
  }
  if(idinc > 5)
  {
    idinc = 0;
  }

}

unsigned long calculateCanId(uint8_t priority, uint16_t subjectID, uint8_t sourceNodeID) 
{
    unsigned long canID = 0;

    // Priority (3 bits, bits 26-28)
    canID |= ((priority & 0x07) << 26);

    // Service, not message (1 bit, bit 25)
    canID |= (0b0 << 25);

    // Anonymous (1 bit, bit 24)
    canID |= (0b0 << 24);

    // Reserved bits (3 bits, bits 21-23)
    canID |= (0b000 << 21);

    // Subject ID (13 bits, bits 8-20)
    canID |= ((unsigned long)(subjectID & 0x1FFF) << 8);

    // Reserved bit (1 bit, bit 7)
    canID |= (0b0 << 7);

    // Source Node ID (7 bits, bits 0-6)
    canID |= (sourceNodeID & 0x7F);

    return canID;  // CAN ID fully constructed
}


void x_MakeThrot(uint16_t *throt, uint8_t *throtOut)
{
  /*
  Note: the length of the pointer throt must be more than 4
  the length of the pointer throtOut must be more than 8
  */

  /* Remove the upper two digits */
  throt[0] &= 0x3fffu;
  throt[1] &= 0x3fffu;
  throt[2] &= 0x3fffu;
  throt[3] &= 0x3fffu;

  /* Split the upper 6 bits of the last throttle */
  throt[0] |= ((throt[3]<<2)&0xc000u);
  throt[1] |= ((throt[3]<<4)&0xc000u);
  throt[2] |= ((throt[3]<<6)&0xc000u);

  /* Copy data */
  *(uint16_t *)(&throtOut[0]) = throt[0];
  *(uint16_t *)(&throtOut[2]) = throt[1];
  *(uint16_t *)(&throtOut[4]) = throt[2];
  *(uint16_t *)(&throtOut[6]) = throt[3];
}

void sendCommandControl(uint8_t Tail ,uint8_t sourceNodeID) 
{
  byte data[4];

  data[0] = 0x01; // Example command
  data[1] = 0x10; // Node ID
  data[2] = 0x00; // Reserved
  data[3] = Tail; // Tail Byte

  unsigned long id = calculateCanId(2,6144,sourceNodeID);

  Serial.print("0x");
  Serial.print(id,HEX);
  if (CAN0.sendMsgBuf(id, 1, 4, data) == CAN_OK)
  {
    Serial.print("\t");
    Serial.println("send Command Control sent");
  }
  else
  {
    Serial.print("\t");
    Serial.println("send Command Control Fuxked");
  }
}

void setDeviceID(uint8_t Tail,uint8_t sourceNodeID) 
{
  byte data[3];

  data[0] = 0x00; // 0
  data[1] = 0x10; // Node ID
  data[2] = Tail; // Tail Byte

  unsigned long id = calculateCanId(4,6145,sourceNodeID);

  Serial.print("0x");
  Serial.print(id,HEX);
  if (CAN0.sendMsgBuf(id, 1, 3, data) == CAN_OK)
  {
    Serial.print("\t");
    Serial.println("set Device ID sent");
  }
  else
  {
    Serial.print("\t");
    Serial.println("set Device ID Fuxked");
  }
}

void sendThrottleData(uint8_t Tail,uint8_t sourceNodeID) 
{ 
  // 0 - 2048
  uint16_t throt[4] = {100,200,300,0};

  uint8_t data[8] = {0};
  uint8_t data2[8] = {0};

  x_MakeThrot(throt,data);
  x_MakeThrot(throt,data2);

  for(int x; x < 7; x++)
  {
    Serial.print("1-3 Motors to 7 bytes: ");
    Serial.print("0x");
    Serial.print(data[x],HEX);
    Serial.print("\t");
    Serial.print("4-6 Motors to 7 bytes: ");
    Serial.print("0x");
    Serial.println(data2[x],HEX);
  }

  unsigned long id = calculateCanId(3,6152,sourceNodeID);
  data[7] = Tail; // Tail Byte
  data2[7] = Tail; // Tail Byte

  Serial.print("0x");
  Serial.print(id,HEX);
  if (CAN0.sendMsgBuf(id, 1, 8, data) == CAN_OK)
  {
    Serial.print("\t");
    Serial.println("Throttle Data 6152 sent");
  }
  else
  {
    Serial.print("\t");
    Serial.println("Throttle Data 6152 Fuxked");
  }
  tid++;
  delay(10);

  id = calculateCanId(3,6153,sourceNodeID);

  Serial.print("0x");
  Serial.print(id,HEX);
  if (CAN0.sendMsgBuf(id, 1, 8, data2) == CAN_OK)
  {
    Serial.print("\t");
    Serial.println("Throttle Data 6153 sent");
  }
  else
  {
    Serial.print("\t");
    Serial.println("Throttle Data 6153 Fuxked");
  }
}

void sendInfoUpload6160(uint8_t Tail,uint8_t sourceNodeID) 
{
  byte data[7];

  data[0] = random(0, 256); // Electrical speed (low byte)
  data[1] = random(0, 50); // Electrical speed (high byte)
  data[2] = random(0, 200); // Bus current (low byte)
  data[3] = 0; // Bus current (high byte)
  data[4] = 0b00010100; // Running status (low byte)
  data[5] = 0b00000001; // Running status (high byte)
  data[6] = Tail; // Tail Byte 

  unsigned long id = calculateCanId(5,6160,sourceNodeID);

  Serial.print("0x");
  Serial.print(id,HEX);
  if (CAN0.sendMsgBuf(id, 1, 7, data) == CAN_OK)
  {
    Serial.print("\t");
    Serial.println("Info Upload 6160 sent");
  }
  else
  {
    Serial.print("\t");
    Serial.println("Info Upload 6160 Fuxked");
  }
  
}

void sendInfoUpload6161(uint8_t Tail,uint8_t sourceNodeID) 
{
  byte data[8];

  data[0] = random(0, 100); // Output throttle (low byte)
  data[1] = 0; // Output throttle (high byte)
  data[2] = random(0, 100); // Bus voltage (low byte)
  data[3] = 0; // Bus voltage (high byte)
  data[4] = random(40, 100); // MOS temperature
  data[5] = random(40, 100); // Capacitance temperature
  data[6] = random(40, 100); // Motor temperature
  data[7] = Tail; // Tail Byte

  unsigned long id = calculateCanId(5,6161,sourceNodeID);

  Serial.print("0x");
  Serial.print(id,HEX);
  if (CAN0.sendMsgBuf(id, 1, 8, data) == CAN_OK)
  {
    Serial.print("\t");
    Serial.println("Info Upload 6161 sent");
  }
  else
  {
    Serial.print("\t");
    Serial.println("Info Upload 6161 Fuxked");
  }
}

void sendHeartbeat(uint8_t Tail,uint8_t sourceNodeID) 
{
  byte data[7];

  unsigned long powerOnTime = millis() / 1000;

  data[0] = powerOnTime & 0xFF;
  data[1] = (powerOnTime >> 8) & 0xFF;
  data[2] = (powerOnTime >> 16) & 0xFF;
  data[3] = (powerOnTime >> 24) & 0xFF;
  data[4] = random(0, 4); // Node health status
  data[5] = random(0, 4); // Node current mode
  data[6] = Tail; // Tail Byte

  unsigned long id = calculateCanId(4,7509,sourceNodeID);

  Serial.print("0x");
  Serial.print(id,HEX);

  Serial.print("\t");

  if (CAN0.sendMsgBuf(id, 1, sizeof(data), data) == CAN_OK)
  {
    Serial.println("Heartbeat sent");
  }
  else
  {
     Serial.println("Heartbeat Fuxked");
  }
  Serial.println("\n");
}
