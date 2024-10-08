#pragma once
#ifndef MAIN_H
#define MAIN_H

#include <Arduino.h>
#include <Stepstick.h>
#include <TMCStepper.h>
#include <Wire.h>
#include <FastLED.h>
#include "config.h"
#include "pwm.h"

extern PwmOut Led1;
extern PwmOut Led2;
extern CRGBArray<NeoPixelCount> NeoPixel;

extern Stepstick X; 
extern TMC2209Stepper X_driver;

extern Stepstick Y; 
extern TMC2209Stepper Y_driver;

extern Stepstick Focus; 
extern TMC2209Stepper F_driver;

struct boollong{ 
  bool checksum ;
  long value;
  
};



void home_XYF(uint16_t bump);
boollong readDestination(byte cmd);
void receiveData(int numberofbyte);
void sendData();
void neopixelSolidColour(uint8_t R ,uint8_t G, uint8_t B);
void run_loop(Stepstick &axis);
void run_loop(Stepstick &axis1, Stepstick &axis2);
void run_loop(Stepstick &axis1, Stepstick &axis2, Stepstick &axis3);

#endif