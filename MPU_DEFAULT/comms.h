
#ifndef comms.h
#define comms.h

#include "Arduino.h"

#define HELLO 'H'
#define ACK 'A'
#define NAK 'N'
#define MAX_SIZE 19

typedef union {
  float floatValue;
  byte byteValue[4];
} floatByteData;

void accelToPacket(byte [], float, float, float);
void gyroToPacket(byte [], float, float, float);
void checksumToPacket(byte [], int);
void padPacket(byte [], int);

byte calculateChecksum(byte[], int);

int floatToPacket(int, byte [], float);

#endif
