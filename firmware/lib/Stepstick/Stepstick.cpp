#include "Stepstick.h"

// use_pin_mode option use the normal method instead of trying to guess register
// step are about 10us slower in this mode should almost never cause an issue
Stepstick::Stepstick(uint8_t stepPin, uint8_t dirPin)
{
  _stepPin = stepPin;
  _dirPin = dirPin;

}

Stepstick::Stepstick(uint8_t stepPin, uint8_t dirPin, uint8_t enPin, uint8_t idxPin)
{
  _stepPin = stepPin;
  _dirPin = dirPin;
  _enPin = enPin;
  _idxPin = idxPin;
}

void Stepstick::begin() 
{
  pinMode(_stepPin, OUTPUT);
  pinMode(_dirPin, OUTPUT);

  if (_enPin != -1) {
    pinMode(_enPin, OUTPUT);
    digitalWrite(_enPin, LOW);
  }

  if (_idxPin != -1) {
    pinMode(_idxPin, INPUT_PULLDOWN);
  }

}


void Stepstick::step() 
{
  digitalWrite(_stepPin, HIGH);
  delayMicroseconds(pulse_width - 2); // pulse duration - 2us for digital read/writeon R4 minima
  digitalWrite(_stepPin, LOW);
  _current_pos = _current_pos + _current_dir;
}

//Execute a single step per timing cycle, 
bool Stepstick::timed_step() {
  if (timing < 0 ){return false;}
  if ((unsigned long)(micros() - _last_step_time) >= timing )
  {
    _last_step_time = micros();
    step();
    return true;
  }
  return false;
}

int8_t Stepstick::endstops_check() { 
  
  if (_maxPin != -1) {

    uint8_t max_endstop;   

    max_endstop = digitalRead(_maxPin);

    if (max_endstop == 0 && _current_dir == 1 ) {
    #ifdef DEBUG
    Serial.println("Max endstop reached");
    #endif
    return 1;   
    }   
  }

  if (_minPin != -1) {

    uint8_t min_endstop;   

    if (_use_pin_mode){
      min_endstop = digitalRead(_minPin);
    }

    if (min_endstop == 0 && _current_dir == -1 ) {
    #ifdef DEBUG
    Serial.println("Min endstop reached");
    #endif
    return -1;   
    }   
  }

  return 0;
}


bool Stepstick::stall_check() {
  if (digitalRead(_DiagPin) == 1){
    stall_flag = true;
    last_stall_value = _TMCdriver->SG_RESULT();   
    switch_state(STALL_RECOVERY);
    return true;
  }
  else return false;
}

void Stepstick::stall_recovery() {
  if  (_stall_recovery_counter == 0) {
  reverse_direction(); }

  if (_stall_recovery_counter == _microsteps*3 ){
    reverse_direction();
    switch_state(OFF);
    _stall_recovery_counter = 0;
    return;
  }
  if (timed_step() == true) {
    _stall_recovery_counter++;
  }
  return;
}


void Stepstick::timing_based_acceleration(){
  return;
  /*
  int32_t distance_from_end = abs(_current_pos - _destination);

  if (distance_from_end >= _acceleration_length  && timing > _fast_spd_timing ){
    timing = timing - timing* _acceleration_factor;
    return;
  }
  else if (distance_from_end < _deceleratiob_length && timing < _slow_spd_timing){
    timing = timing + timing* _acceleration_factor;
  }
  else {
    timing = _slow_spd_timing;
  } */

} 

//Set the motor destination for timed step, 
//Set the direction accordingly
void Stepstick::set_destination(int32_t destination){
  
  if (destination > _max_range) {destination = _max_range;}
  if (destination < _min_range) {destination = _min_range;}
  
  _destination = destination;
  set_direction(sgn(destination - _current_pos));

}

/*set _dirPin in the appropriate state. 
And perform hysteresis steps according to _hyst_step and if hystersis is set to true (default)*/
void Stepstick::set_direction(int8_t dir, bool hysteresys)
{
  if( dir == _current_dir){return;}

  if (_invert == true) {
    if ( dir == 1) {
      digitalWrite(_dirPin, LOW);
    } else {
      digitalWrite(_dirPin, HIGH);
    }
  }

  if ( dir == -1) {
    digitalWrite(_dirPin, LOW);
  } else {
    digitalWrite(_dirPin, HIGH);
  }
  
  _current_dir = dir;

  // make _hyst_steps that are unacounted for in _curent_position
  if (_hyst_steps > 0) {
  hysteresis_comp();
  }
}

void Stepstick::reverse_direction(bool hysteresys)
{
  set_direction(get_direction() * (-1));
}


/*called after direction change if _hyst_step is not 0*/
void Stepstick::hysteresis_comp(){
    for (int32_t i = 0; i < _hyst_steps; i++) {
      step();
      _current_pos = _current_pos - _current_dir; //revert the position counter to make ghost steps
      delayMicroseconds(_slow_spd_timing);
    }
}

int Stepstick::evaluate_SGTHRS(int steps){

  int SG_value = 0;

  int i = 0;
  int n = 0;
  while ( i <= (steps) ) {
    if (timed_step() == true) {
      i++;
      if (i % (_microsteps*4) == 0)  {
        SG_value += _TMCdriver->SG_RESULT();
        n++;
      }
    }
  }

  return SG_value / n ;
  
}

/*
// initialise the 0 position, slowly step in negative dir until reach endstop
void Stepstick::axis_find_zero(uint16_t bump) {
  if ( _minPin == -1){
    #ifdef DEBUG
    serial.println("Min pin not defined, use configure_endstops(minPin, maxPin) to do so, maxPin can be set to -1 if no max endstop")
    #endif
    return;
  }

  //first
  set_direction(-1, false);
  while ( endstops_check() == 0 )
  {
    timed_step(true);
    delayMicroseconds(10);
  }
  override_position(0);

  //bump
  
  set_destination(bump);
  timing = _slow_spd_timing;
  while (!at_destination()){
    timed_step(true,true);
    delayMicroseconds(10);
  }

  // Go back
  _destination = 0; //avoid some bugs
  set_direction(-1, false);
  timing = _slow_spd_timing *2;
  while ( endstops_check() == 0 )
  {
    timed_step(true);
    delayMicroseconds(10);
  }

  _current_pos = 0;
  _min_range = 0;
}
*/

/* misc commands */

// initialise the 0 position, slowly step in negative dir until reach endstop

int32_t Stepstick::get_position() {return _current_pos;}

int32_t Stepstick::get_destination() {return _destination;}

int8_t Stepstick::get_direction() {return _current_dir;}

void Stepstick::override_position(int32_t position) {_current_pos = position;}

void Stepstick::set_max_range(int32_t max_range){ _max_range = max_range;}

void Stepstick::invert_motor(){_invert = true;}

void Stepstick::use_pin_mode(){_use_pin_mode = true;}

bool Stepstick::at_destination() {
  if (_current_pos == _destination ) {return true;}
  return false; }



void Stepstick::axis_find_zero_stallguard(uint16_t bump) {
  timing = _slow_spd_timing;
  //first
  set_direction(1, false);
  for ( int i = 0; i <= _microsteps * 3; i++  ) //3 full step initialise avoid gett SG readings too low
    {
      step();
      delayMicroseconds(timing);
    }

  set_direction(-1, false);
  Serial.println("Finding 0");
  Serial.println(get_direction());
  for ( int i = 0; i <= _microsteps * 3; i++ ) { //3 full step initialise avoid gett SG readings too low on startup
      step();
      delayMicroseconds(timing);
    }
  switch_state(TIMER_STALLGUARD);
  while ( get_state() != OFF )
  {
    run();
    delayMicroseconds(10);
  }

  override_position(0);

  // Bump
  set_destination(bump);
  Serial.println("Bump!");
  switch_state(GO);
  while ( get_state() != OFF ) {
    run();
    delayMicroseconds(10);
  }

  // Auto Evaluation of SGTHRS 
  set_direction(-1, false);
  Serial.print("StallGuard Value autoevaluation:");

  int SG_value = evaluate_SGTHRS(bump/2);
  int SGTHRS = (SG_value/3);

  Serial.print(SG_value);
  Serial.print(" STGTHRS: ");
  Serial.println(SGTHRS);

  _TMCdriver->SGTHRS(SGTHRS);

  //  
  Serial.println("Finding 0 again with new value");
  switch_state(TIMER_STALLGUARD);
  for ( int i = 0; i <= _microsteps * 3; i++ ) { //3 full step initialise avoid gett SG readings too low on startup
      step();
      delayMicroseconds(timing);
    }

  while ( get_state() != OFF ){ 
      run();
      delayMicroseconds(10);
    }

  override_position(0);

  _current_pos = 0;
  _min_range = 0;
  Serial.println("Done");
}


