
#ifndef comms.h
#define comms.h

#include "Arduino.h"

#define HELLO 'H'
#define ACK 'A'
#define NAK 'N'
#define MAX_SIZE 19


void missToPacket(byte []);
void hitToPacket(byte []);
void checksumToPacket(byte [], int);
void padPacket(byte [], int);

byte calculateChecksum(byte[], int);


#endif
