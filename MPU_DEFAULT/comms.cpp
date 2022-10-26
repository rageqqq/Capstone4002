
#include "Arduino.h"
#include "comms.h"

void accelToPacket(byte packet[], float ax, float ay, float az) {
  packet[1] = 0;
  packet[2] = 0;
  int index = 3;
  index = floatToPacket(index, packet, ax);
  index = floatToPacket(index, packet, ay);
  index = floatToPacket(index, packet, az);
  padPacket(packet, index);
}

void gyroToPacket(byte packet[], float gx, float gy, float gz) {
  packet[1] = 0;
  packet[2] = 1;
  int index = 3;
  index = floatToPacket(index, packet, gx);
  index = floatToPacket(index, packet, gy);
  index = floatToPacket(index, packet, gz);
  padPacket(packet, index);
}

void checksumToPacket(byte packet[], int packetSize) {
  int index = packetSize - 1;
  packet[index] = calculateChecksum(packet, packetSize);
}

void padPacket(byte packet[], int index) {
  for (int i = index; i < MAX_SIZE - 1; i++) {
    packet[i] = 0;
  }
}

byte calculateChecksum(byte packet[], int packetSize) {
  byte checksum = 0;

  for (int i = 0; i < packetSize - 1; i++) {
    checksum ^= packet[i];
  }

  return checksum;
}

int floatToPacket(int index, byte packet[], float data) {
  floatByteData x;
  x.floatValue = data;

  for (int i = 0; i < 4; i++) {
    packet[index] = x.byteValue[i];
    index++;
  }
  return index;
}
