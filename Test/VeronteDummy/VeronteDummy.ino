#include <Arduino.h>
#include <ArduinoJson.h>

void setup() 
{
  Serial.begin(115200);
  Serial1.begin(115200);
}

void loop() 
{
  // Create a JSON document
  StaticJsonDocument<512> doc;
  
  // Add random values to the JSON document
  doc["altitude_AGL"] = random(0, 100);
  doc["altitude_AGL_set"] = random(0, 100);
  doc["altitude_ABS"] = random(0, 100);
  doc["heading"] = random(0, 360);
  doc["compass"] = random(0, 360);
  doc["attitude_pitch"] = random(-30, 30);
  doc["attitude_roll"] = random(-30, 30);
  doc["vertical_speed_KTS"] = random(0, 60);
  doc["airspeed_KTS"] = random(0, 60);
  doc["OAT"] = random(0, 100);
  doc["latitude"] = String(random(0, 59)) + "d" + String(random(0, 59)) + "a" + String(random(0, 59)) + "q";
  doc["longitude"] = String(random(0, 59)) + "d" + String(random(0, 59)) + "a" + String(random(0, 59)) + "q";
  doc["flight_time"] = String(random(0, 59)) + ":" + String(random(0, 59));
  
  // Serialize the JSON document to a string
  String output;
  serializeJson(doc, output);

  // Send the string over UART
  Serial.println(output);
  Serial1.println(output);
  // Wait for a second before sending the next packet
  delay(10);
}
