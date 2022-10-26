/*
 * SimpleReceiver.cpp
 *
 * Demonstrates receiving NEC IR codes with IRrecv
 *
 *  This file is part of Arduino-IRremote https://github.com/Arduino-IRremote/Arduino-IRremote.
 *
 ************************************************************************************
 * MIT License
 *
 * Copyright (c) 2020-2022 Armin Joachimsmeyer
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is furnished
 * to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
 * INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
 * PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
 * CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
 * OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 ************************************************************************************
 */

/*
 * Specify which protocol(s) should be used for decoding.
 * If no protocol is defined, all protocols are active.
 */
//#define DECODE_DENON        // Includes Sharp
//#define DECODE_JVC
//#define DECODE_KASEIKYO
//#define DECODE_PANASONIC    // the same as DECODE_KASEIKYO
//#define DECODE_LG
#define DECODE_NEC          // Includes Apple and Onkyo
//#define DECODE_SAMSUNG
//#define DECODE_SONY
//#define DECODE_RC5
//#define DECODE_RC6

//#define DECODE_BOSEWAVE
//#define DECODE_LEGO_PF
//#define DECODE_MAGIQUEST
//#define DECODE_WHYNTER

//#define DECODE_DISTANCE     // universal decoder for pulse distance protocols
//#define DECODE_HASH         // special decoder for all protocols

//#define DEBUG               // Activate this for lots of lovely debug output from the decoders.

#include <Arduino.h>
#include "comms.h"
#define LED_PIN 5

#include "PinDefinitionsAndMore.h" //Define macros for input and output pin etc.
#include <IRremote.hpp>

bool hasHello = false;
bool handshakeComplete = false;
int seqNo = 0;

byte packet[20];
int packetSize = 20;

void setup() {
    Serial.begin(115200);
    // Just to know which program is running on my Arduino
    //Serial.println(F("START " __FILE__ " from " __DATE__ "\r\nUsing library version " VERSION_IRREMOTE));

    // Start the receiver and if not 3. parameter specified, take LED_BUILTIN pin from the internal boards definition as default feedback LED
    IrReceiver.begin(IR_RECEIVE_PIN, ENABLE_LED_FEEDBACK);

    //Serial.print(F("Ready to receive IR signals of protocols: "));
    //printActiveIRProtocols(&Serial);
    //Serial.println(F("at pin " STR(IR_RECEIVE_PIN)));

    hasHello = false;
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
  if(handshakeComplete) {
    if (IrReceiver.decode()) {

        // Print a short summary of received data
        //IrReceiver.printIRResultShort(&Serial);
        //IrReceiver.printIRSendUsage(&Serial);
        //if (IrReceiver.decodedIRData.protocol == UNKNOWN) {
            //Serial.println(F("Received noise or an unknown (or not yet enabled) protocol"));
            // We have an unknown protocol here, print more info
            //IrReceiver.printIRResultRawFormatted(&Serial, true);
        //}
        //Serial.println();

        /*
         * !!!Important!!! Enable receiving of the next value,
         * since receiving has stopped after the end of the current received data packet.
         */
        IrReceiver.resume(); // Enable receiving of the next value

        /*
         * Finally, check the received data and perform actions according to the received command
         */
        if (IrReceiver.decodedIRData.command == 0x11) {
          digitalWrite(LED_PIN, HIGH);
          sendPacket(packet, true);
          delay(200);
          digitalWrite(LED_PIN, LOW);
        } else {
          sendPacket(packet,false);
        }
    }
    delay(50);
  }
}

void sendPacket(byte packet[], bool hitStatus) {
  packet[0] = seqNo;
  if(hitStatus) {
    hitToPacket(packet);
  } else {
    missToPacket(packet);
  }
  checksumToPacket(packet, packetSize);
  Serial.write(packet, packetSize);
  seqNo++;
}
