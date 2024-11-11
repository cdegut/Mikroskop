#include "Stepstick.h"

void  Stepstick::setup_TMC(TMC2209Stepper * TMCdriver, uint8_t microsteps, uint16_t current){
  _TMCdriver = TMCdriver;
  _TMCdriver->begin();
  _TMCdriver->toff(5);  //4
  _TMCdriver->rms_current(current);        // Set motor RMS current          // Set microsteps to 1/8th   
  setTMC_microsteps(microsteps, true);

  step();  //switches the drive back to run current.
  _TMCdriver->pwm_autoscale(true); // Needed for stealthChop 
  delay(130); //max needed delay for pwmautoscale
  _TMCdriver->pwm_autograd(true);

}

void  Stepstick::setTMC_microsteps(uint8_t microsteps, bool interpol) {
  _TMCdriver->microsteps(microsteps);
  _microsteps = microsteps;
  _TMCdriver->intpol(true);           // set interpolatoion to 256 on    
}

void Stepstick::config_endstops(uint8_t minPin, uint8_t maxPin){
  /* Use limit switches for the timed step functions*/
  _maxPin = maxPin;
  pinMode(_maxPin, INPUT_PULLUP);
  _minPin = minPin;
  pinMode(_minPin, INPUT_PULLUP);
}

void Stepstick::setup_stallguard(uint8_t DiagPin, uint16_t Stall_value) {
  _DiagPin = DiagPin;
  pinMode(_DiagPin, INPUT_PULLDOWN);
  _TMCdriver->TCOOLTHRS(0xFFFFF); // switch the diag out[put between cool step and stallguard bellow that value. set at max to always haave SG
  _TMCdriver->SGTHRS(Stall_value);
}

void Stepstick::config_SG_thresold(uint16_t Stall_value) {
  _TMCdriver->SGTHRS(Stall_value);
}

void Stepstick::config_coolstep(){
  _TMCdriver->seimin(0); // minimum current for smart current control 0=1/2   1=1/4
  _TMCdriver->sedn(0b01); //current down step speed

//min and max StallGuardvalue for smart current control and smart current enable 
  _TMCdriver->semin(0); //if the StallGuard4 result falls below SEMIN*32, the motor current becomes increased to reduce motor load angle
                        //0 to deactivate coolstep
  _TMCdriver->semax(4); // If the StallGuard4 result is equal to or above (SEMIN+SEMAX+1)*32, the motor current becomes decreased to save energy.
}

void Stepstick::config_speed(int slow_spd, int fast_spd){
    _slow_spd_timing = slow_spd;
    _fast_spd_timing = fast_spd;
    timing = slow_spd;

    //_acceleration_length = 1;
    //_acceleration_factor = acceleration_factor;

    //_acceleration_length = (slow_spd - fast_spd) * _microsteps;
    //Serial.print("acceleration lengh in steps: ");
    //Serial.println(_acceleration_length);
}

void Stepstick::config_hyst(int hyst_steps){
  _hyst_steps = hyst_steps;
}


void Stepstick::config_range(int32_t min_range, int32_t max_range)
{
  _max_range = max_range;
  _min_range = min_range;
}