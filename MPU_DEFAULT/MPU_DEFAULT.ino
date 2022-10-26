#include "Arduino.h"
#include "comms.h"

#include <Wire.h>
const int MPU = 0x68; // MPU6050 I2C address
float AccX, AccY, AccZ;
float GyroX, GyroY, GyroZ;
float AccErrorX, AccErrorY, GyroErrorX, GyroErrorY, GyroErrorZ;
int c = 0;

bool handshakeComplete = false;
int seqNo = 0;

byte accelPacket[20];
byte gyroPacket[20];
int packetSize = 20;

void setup() {
  Serial.begin(115200);
  Wire.begin();                      // Initialize comunication
  Wire.beginTransmission(MPU);       // Start communication with MPU6050 // MPU=0x68
  Wire.write(0x6B);                  // Talk to the register 6B
  Wire.write(0x00);                  // Make reset - place a 0 into the 6B register
  Wire.endTransmission(true);        //end the transmission
  
  // Call this function if you need to get the IMU error values for your module
  //calculate_IMU_error();
  delay(20);

  handshakeComplete = false;
  seqNo = 0; 
}
void loop() {

  if(Serial.available()) { //handshake stuff
    if(Serial.read() == HELLO) {
      Serial.write(ACK);
      handshakeComplete = false;
      delay(500);
    }
    if(!handshakeComplete) {
      if(Serial.read() == ACK) {
        handshakeComplete = true;
      }
    }
  }
  
  if(handshakeComplete) { //main loop
    // === Read acceleromter data === //
    Wire.beginTransmission(MPU);
    Wire.write(0x3B); // Start with register 0x3B (ACCEL_XOUT_H)
    Wire.endTransmission(false);
    Wire.requestFrom(MPU, 6, true); // Read 6 registers total, each axis value is stored in 2 registers
    //For a range of +-2g, we need to divide the raw values by 16384, according to the datasheet
    AccX = (Wire.read() << 8 | Wire.read()) / 16384.0; // X-axis value
    AccY = (Wire.read() << 8 | Wire.read()) / 16384.0; // Y-axis value
    AccZ = (Wire.read() << 8 | Wire.read()) / 16384.0; // Z-axis value
    // === Read gyroscope data === //
    Wire.beginTransmission(MPU);
    Wire.write(0x43); // Gyro data first register address 0x43
    Wire.endTransmission(false);
    Wire.requestFrom(MPU, 6, true); // Read 4 registers total, each axis value is stored in 2 registers
    GyroX = (Wire.read() << 8 | Wire.read()) / 131.0; // For a 250deg/s range we have to divide first the raw value by 131.0, according to the datasheet
    GyroY = (Wire.read() << 8 | Wire.read()) / 131.0;
    GyroZ = (Wire.read() << 8 | Wire.read()) / 131.0;
    // Correct the outputs with the calculated error values
    GyroX = GyroX + 0.56; // GyroErrorX ~(-0.56)
    GyroY = GyroY - 2; // GyroErrorY ~(2)
    GyroZ = GyroZ + 0.79; // GyroErrorZ ~ (-0.8)

    accelPacket[0] = seqNo;
    accelToPacket(accelPacket, AccX, AccY, AccZ);
    checksumToPacket(accelPacket, packetSize);
    Serial.write(accelPacket, packetSize);
    seqNo++;

    gyroPacket[0] = seqNo;
    gyroToPacket(gyroPacket, GyroX, GyroY, GyroZ);
    checksumToPacket(gyroPacket, packetSize);
    Serial.write(gyroPacket, packetSize);
    seqNo++;

    delay(50);
    
  }
  
}
