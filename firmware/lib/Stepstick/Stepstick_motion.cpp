#include "Stepstick.h"


void Stepstick::motion_planner(int32_t destination) {


    if (destination > _max_range) {destination = _max_range;}
    if (destination < _min_range) {destination = _min_range;}
    _destination = destination;

    char new_dir = sgn(destination - _current_pos) ;

    int32_t distance_from_end = abs(_current_pos - _destination);

    int acceleration_length = (_slow_spd_timing - _fast_spd_timing) * _microsteps;


    ////////// Same direction, allready running
    if ( (_current_state == GO_FAST || _current_state == ACCELERATE || _current_state == GO ) && new_dir == get_direction()){
        if (distance_from_end < acceleration_length) {
            switch_state(DECELERATE);
            return;
        } 
        else {
        _decelerate_switch = destination - acceleration_length * get_direction();
        acceleration_length = (timing - _fast_spd_timing) * _microsteps;
        _go_fast_switch = _current_pos +  acceleration_length;
        return;
        }
    }

    ////////// Opposite direction, allready running
    if ((_current_state == GO_FAST || _current_state == ACCELERATE || _current_state == GO ) && new_dir != get_direction()){
         switch_state(DECELERATEnGO);
         return;
    }

    if (_current_state == DECELERATE) {
        switch_state(DECELERATEnGO);
    }


    if (distance_from_end < (acceleration_length*2)) { 
        //_go_fast_switch = _current_pos + (distance_from_end / 2) * new_dir;
        //_decelerate_switch =  _go_fast_switch + new_dir;
        timing = _slow_spd_timing*4;
        set_direction(new_dir);
        switch_state(GO);
        return;
    }

    else { // general case
    _go_fast_switch = _current_pos + acceleration_length * new_dir;
    _decelerate_switch = _destination - acceleration_length * new_dir;
    }


    timing = _slow_spd_timing;
    set_direction(new_dir);
    switch_state(ACCELERATE);
    return;
    
}