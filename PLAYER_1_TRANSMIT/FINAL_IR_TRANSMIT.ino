 /*
 * SimpleSender.cpp
 *
 *  Demonstrates sending IR codes in standard format with address and command
 *  An extended example for sending can be found as SendDemo.
 *
 *  Copyright (C) 2020-2021  Armin Joachimsmeyer
 *  armin.joachimsmeyer@gmail.com
 *
 *  This file is part of Arduino-IRremote https://github.com/Arduino-IRremote/Arduino-IRremote.
 *
 *  MIT License
 */
#include <Arduino.h>
#include "comms.h"

//#define SEND_PWM_BY_TIMER
//#define USE_NO_SEND_PWM
//#define NO_LED_FEEDBACK_CODE // saves 418 bytes program memory

#include "PinDefinitionsAndMore.h" //Define macros for input and output pin etc.
#include <IRremote.hpp>
#define DELAY 2
int ledPin = 4;  // LED connected to digital pin 13
#define inPin A2
int val = 0;      // variable to store the read value
int counter = 0;
int DELAYTIME = 50;

bool handshakeComplete = false;
int seqNo = 0;

byte packet[20];
int packetSize = 20;

bool shoot;
char str[5] = "shoot";

void setup() {
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(ledPin, OUTPUT);  // sets the digital pin 13 as output
    pinMode(inPin, INPUT);    // sets the digital pin 7 as input
    Serial.begin(115200);

    IrSender.begin(); // Start with IR_SEND_PIN as send pin and if NO_LED_FEEDBACK_CODE is NOT defined, enable feedback LED at default feedback LED pin

    handshakeComplete = false;
    seqNo = 0;
}

uint16_t sAddress = 0x0102;
uint16_t eCommand = 0x12;
uint16_t fCommand = 0x12;
uint16_t sRepeats = 0;

void loop() {
  val = analogRead(inPin);   // read the input pin
  if(Serial.available()) { //handshake stuff
    if(Serial.read() == HELLO) {
      Serial.write(ACK);
      handshakeComplete = false;
      delay(500);
    }
    if(!handshakeComplete) {
      if(Serial.read() == ACK) {
        handshakeComplete = true;
        shoot = false;
      }
    }
  }
  if(counter < DELAY){
    if(val == 1023) {
      counter++;
      } else {
       counter = 0;
      }
    }else{
      counter = 0;
      if(val == 1023) {
        shoot = true;
      }
    }
    //delay(DELAYTIME);
  if(handshakeComplete) {
    if(shoot) {
      digitalWrite(ledPin, HIGH);
      sendPacket(packet, true); 
      IrSender.sendNEC(sAddress, fCommand, sRepeats);
      //val=0;
      delay(200);
      digitalWrite(ledPin, LOW);
      shoot = false;
    } else {
        digitalWrite(ledPin, LOW);
        sendPacket(packet, false);
    }
    delay(DELAYTIME);
  }
}

void sendPacket(byte packet[], bool shootStatus) {
  packet[0] = seqNo;
  if(shootStatus) {
    shotFiredToPacket(packet);
  } else {
    transmitToPacket(packet);
  }
  checksumToPacket(packet, packetSize);
  Serial.write(packet, packetSize);
  seqNo++;
}
