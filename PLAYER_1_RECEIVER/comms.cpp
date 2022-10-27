
#include "Arduino.h"
#include "comms.h"

void missToPacket(byte packet[]) {
  packet[1] = 1;
  packet[2] = 1;
  packet[3] = 0;
  int index = 4;
  padPacket(packet, index);
}

void hitToPacket(byte packet[]) {
  packet[1] = 1;
  packet[2] = 1;
  packet[3] = 1;
  int index = 4;
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
