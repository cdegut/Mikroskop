#pragma once
#include "main.h"

boollong destination;
int8_t led1pwr = 0;
int8_t led2pwr = 0;
uint8_t checksum_received = 0;
uint8_t checksum =0;
int8_t amount;


uint8_t index;
uint8_t R;
uint8_t G;
uint8_t B;

long wire_debounce_timer = millis();

boollong readDestination(byte cmd) {

  byte a = Wire.read();
  byte b = Wire.read();
  byte c = Wire.read();
  byte d = Wire.read();
  byte e = Wire.read();
  long value = a;
  value = (  value << 8 ) + b;
  value = (  value << 8 ) + c;
  value = (  value << 8 ) + d;
  byte checksum = a + b + c + d + cmd;
  boollong destination;
  destination.value = value;

    if (checksum == e ) {
      destination.checksum = true;
    } else {
      destination.checksum = false;
    }

  return destination;
}


//clean the Wire buffer
void emptyWire() {
  while ( Wire.available() )
    Wire.read();
}

void neopixelSolidColour(uint8_t R ,uint8_t G, uint8_t B) {

  for ( int i=0; i < NeoPixelCount ; i++){
  NeoPixel[i] = CRGB(R,G,B); 
  }
  FastLED.show();
}

void receiveData(int numberofbyte) {
  digitalWrite(ReadyPin, LOW); // Ready as low until operation are done 
  //long start_timer = micros();
  byte cmd = Wire.read();
  long timer = micros();
  
  /* ### Movements ### */
  switch (cmd) {
    case 0x01://set destination X axis
      destination = readDestination(cmd);
      if (destination.checksum == true ) {
        X.motion_planner(destination.value);       
      }
      break;

    case 0x02: //set destination Y axis
      destination = readDestination(cmd);
      if (destination.checksum == true ) { 
        Y.motion_planner(destination.value);
      }
      break;

    case 0x03:  //set destination Focus axis
      destination = readDestination(cmd);
      if (destination.checksum == true ) { 
        Focus.motion_planner(destination.value);
      }
      break;

    case 0x11: //push +X axis
        amount = Wire.read();
        if (Wire.read() != amount){return;}
        X.motion_planner(X.get_destination() + amount);
      break;
    
    case 0x12: //push Y axis
        amount = Wire.read();
        if (Wire.read() != amount){return;}
        Y.motion_planner(Y.get_destination() + amount);
      break;
        
    case 0x13: //push Focus
        amount = Wire.read();
        if (Wire.read() != amount){return;}
        Focus.motion_planner(Focus.get_destination() + amount);
      break;
    
    case 0x21: //push +X axis
        amount = Wire.read();
        if (Wire.read() != amount){return;}
        X.motion_planner(X.get_destination() - amount);
      break;
    
    case 0x22: //push Y axis
        amount = Wire.read();
        if (Wire.read() != amount){return;}
        Y.motion_planner(Y.get_destination() - amount);
      break;
        
    case 0x23: //push Focus
        amount = Wire.read();
        if (Wire.read() != amount){return;}
        Focus.motion_planner(Focus.get_destination() - amount);
      break;

  /* ### LEDs ### */
    case 0x04: //set leds power
     if (Wire.read() == cmd) { //simple cmd need to be sent twice to be executed (crude error check)
        led1pwr = Wire.read();
        led2pwr = Wire.read();
        checksum = Wire.read();

        Serial.println(checksum);
        if (led1pwr + led2pwr == checksum) {
          Led1.pulse_perc(led1pwr);
          Led2.pulse_perc(led2pwr);
        }
      }
    break;

    case 0x05: // NeoPixel solid colour

      if (Wire.read() == cmd) { //simple cmd need to be sent twice to be executed (crude error check)
        R = Wire.read();
        G = Wire.read();
        B = Wire.read();
        checksum_received = Wire.read();
        checksum = R+G+B;

        if (checksum_received == checksum) {
          neopixelSolidColour(R,G,B);
        }
      }

    break;

    case 0x06: // NeoPixel single colour

      if (Wire.read() == cmd) { //simple cmd need to be sent twice to be executed (crude error check)
        index = Wire.read();
        R = Wire.read();
        G = Wire.read();
        B = Wire.read();
        checksum_received = Wire.read();
        if (index > NeoPixelCount) {break;}
        
        checksum = index+R+G+B;
        if (checksum_received == checksum) {
          NeoPixel[index] = CRGB(R,G,B); 
          FastLED.show();
        }
      }
      break;

    }
  emptyWire();
  // empty the wire buffer if it overflowed
  //Serial.println(micros() - start_timer); 
}


/*#########################################
############ Send position ################
##########################################*/
long send_time;
bool new_time;

void sendData() {

  long X_pos = X.get_position();
  long Y_pos = Y.get_position();
  long F_pos = Focus.get_position();

  byte * Xarr = (byte *) &X_pos;
  byte * Yarr = (byte *) &Y_pos;
  byte * Farr = (byte *) &F_pos;

  byte  message[15];

  message[0] = Xarr[0];
  message[1] = Xarr[1];
  message[2] = Xarr[2];
  message[3] = Xarr[3];
  message[4] = Yarr[0];
  message[5] = Yarr[1];
  message[6] = Yarr[2];
  message[7] = Yarr[3];
  message[8] = Farr[0];
  message[9] = Farr[1];
  message[10] = Farr[2];
  message[11] = Farr[3];
  message[12] = led1pwr;
  message[13] = led2pwr;
  uint8_t sum = 0;
  for (int i = 0; i < 14; i++) {
        sum += message[i];
    }
  message[14] = sum;
  Wire.write(message, 15); 

}

