#include "Stepstick.h"

void Stepstick::run() {

  switch(_current_state) {
    case OFF: // 0 Motor is off
      break;

    case STEPPING: //1
      // Step at every call
      step();
    
    break;

    case TIMER: // 2
      // Step based on internal timer
      timed_step();
    
    break;

    case TIMER_COUNTED_STEP:
      if (_step_counter == 0) {
        switch_state(OFF);
        return;
      }
      if (timed_step() == true) {
        _step_counter--;
      }

    break;
    case TIMER_ENDSTOP: // 3
      // Step based on internal timer
      // Stop if reach and endstop
      if (endstops_check() != 0){
        switch_state(0);
        return;
      }
      timed_step();
    
    break;

    case TIMER_STALLGUARD: // 4
      // Stepping, internal timing
      // Stop if stallGuard is triggered
      if(stall_check() == true) {return;}
      timed_step();
    
    break;

     case GO:
      // Stepping, internal timing
      // Stop when reach specific position
      if (_current_pos == _destination) {
        switch_state(OFF);
        return;
      }
      timed_step();
      return; 

      case GO_ACC:
      // Stepping, internal timing
      // Stop when reach specific position
      // Update
      if (_current_pos == _destination) {
        switch_state(OFF);
        return;
      }
      timing_based_acceleration();
      timed_step();
      return;

    break;    

    case GO_ES:
      // Stepping, internal timing
      // Stop if reach and endstop
      // Stop when reach specific position

      if (endstops_check() != 0){
        switch_state(OFF);
        break;
      }
      if (_current_pos == _destination) {
        switch_state(OFF);
        break;
      }
      timed_step();
    
    break;
    
    case GO_SG:
      // Stepping, internal timing
      // Stop when reach specific position
      // Stop if stalled

      if(stall_check()) {return;}
      if (_current_pos == _destination) {
        switch_state(OFF);
        break;
      }
      timed_step();
    
    break;

    
    case STALL_RECOVERY: //STALL Recovery
      // do one full step in reverse
      stall_recovery();
    
    break;

    case init_TIMER_STALLGUARD: // init_TIMER_STALLGUARD
      //full step and switch to GO_SG
      if (_TIMER_STALLGUARD_counter == _microsteps * 3) {
        switch_state(TIMER_STALLGUARD);
        _TIMER_STALLGUARD_counter = 0;
        return;
      }
      if (timed_step() == true) {
        _TIMER_STALLGUARD_counter++;
      }
      return; 


    case ACCELERATE:
      if (_current_pos == _go_fast_switch) {
          switch_state(GO_FAST);
          return;
        }
      if (timed_step() == true) {
      _acceleration_counter++;
      if (_acceleration_counter == _microsteps *acceleration_multiplier) {
        timing--;
        _acceleration_counter =0;
        }
      }
      break;

    case GO_FAST:

    if (_current_pos == _decelerate_switch) {
        switch_state(DECELERATE);
        _acceleration_counter =0;
        return;
      }
      timed_step();
      return; 

    break;

    case DECELERATE:
    if (_current_pos == _destination) {
      timing = _slow_spd_timing;
      switch_state(OFF);
      if (at_destination() == true) {
        }
      return;
      }

      if (timed_step() == true) {
      _acceleration_counter++;
      if (_acceleration_counter == _microsteps) {
        timing++;
        _acceleration_counter =0;
        }
      }

    break;

    case DECELERATEnGO:

      if (timing >= _slow_spd_timing) {
        reverse_direction();
        timing = _slow_spd_timing;
        motion_planner(_destination);
      }

      if (timed_step() == true) {
      _acceleration_counter++;

      if (_acceleration_counter == _microsteps -1) {
        timing++;
        _acceleration_counter =0;
        }

      }
    
    break;
      
    default:
    return;
    // code block
  }
}

void Stepstick::switch_state(int8_t new_state){
  _current_state = new_state;}

uint8_t Stepstick::get_state() {return _current_state;}

void Stepstick::set_step_counter(uint32_t step_counter) { _step_counter = step_counter;}