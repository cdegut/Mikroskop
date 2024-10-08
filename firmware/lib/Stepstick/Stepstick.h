#ifndef Stepstick_h
#define Stepstick_h

#include <TMCstepper.h>
#include "Arduino.h"

#define DEBUG
//#define TIMING

#define OFF 0
#define STEPPING 1
#define TIMER 10
#define TIMER_COUNTED_STEP 11
#define TIMER_ENDSTOP 12
#define TIMER_STALLGUARD 13
#define GO 20
#define GO_ACC 21
#define GO_ES 22
#define GO_SG 23
#define GO_SG_ACC 24
#define STALL_RECOVERY 200
#define init_TIMER_STALLGUARD 201
#define ACCELERATE 100
#define GO_FAST 101
#define DECELERATE 102
#define DECELERATEnGO 103

#define PRINT_SG_RESULT




class Stepstick {
  
  public:
    Stepstick(uint8_t stepPin, uint8_t dirPin);
    Stepstick(uint8_t stepPin, uint8_t dirPin, uint8_t enPin);
    void begin();
    void setup_TMC(TMC2209Stepper *TMCdriver, uint8_t microsteps = 4,  uint16_t current = 800);

    //basic movement
    void step();
    void set_direction(int8_t dir, bool hysteresys = false);
    void reverse_direction(bool hysteresys = false);

    void run();

    void switch_state(int8_t new_state);
    uint8_t get_state();

    bool timed_step();
    //void timed_step(bool check_endstops,  uint8_t use_destination, uint8_t acceleration);

    //travel
    void motion_planner(int32_t destination);
    void set_destination(int32_t destination); //simply set destination for timed_step
    int32_t get_destination();
    bool at_destination();

    void set_step_counter(uint32_t step_counter);




    void axis_find_zero_stallguard(uint16_t bump = 1000); //bump = bump lenght
    int8_t endstops_check();


    //get values 
    int32_t get_position();
    int8_t get_direction();


    //Cofigurations
    bool enable = true; // enable for timed step (allow to stop the motor)
    void config_axis(uint8_t zeroPin, int slow_spd, int fast_spd, int32_t max_range, int hyst_steps);
    void config_endstops(uint8_t MinPin, uint8_t MaxPin = -1); //set pin to -1 to deactivate
    void setup_stallguard(uint8_t DiagPin, uint16_t Stall_value);
    void config_SG_thresold(uint16_t Stall_value);
    int evaluate_SGTHRS(int full_steps);
    bool stall_flag;
    int last_stall_value;
    void config_coolstep();
    void setTMC_microsteps(uint8_t microsteps, bool interpol = true);
    void config_speed(int slow_spd, int fast_spd);
    void config_hyst(int hyst_steps);
    void set_max_range(int32_t max_range);
    void override_position(int32_t position);

    //options
    void invert_motor(); /* inverse all change of direction*/
    void use_pin_mode(); // fallback to pin methods instead of port manipulation
    uint8_t pulse_width = 4; //fast steps pulse width in us
    int32_t timing = -1; // timing for timed steps, set at -1 will disable 

 private:
    void hysteresis_comp();
    void timing_based_acceleration();
    bool stall_check();
    void stall_recovery();

    // TMC driver object
    TMC2209Stepper *_TMCdriver;
    uint8_t _microsteps = 16;

    //States related
    uint8_t _current_state = 0;
    uint8_t _stall_recovery_counter = 0;
    uint8_t _TIMER_STALLGUARD_counter = 0;
    uint32_t _step_counter = 0;

    //travel values
    int32_t _destination = 0;
    int8_t _current_dir = -1; // motor direction either +1 or -1  

    // pins 
    uint8_t _stepPin;
    uint8_t _dirPin;
    uint8_t _DiagPin = -1;
    uint8_t _enPin = -1;

     /*
    //port and bitmasks
    uint8_t _port;
    volatile uint16_t *_stepPortOutputRegister; //pointer to the port register
    uint8_t _step_bitmask;  // contain the pin bit mask for direct port manipulation in the form 0b00010000
    uint8_t _step_bitmaskNOT; // contain the NOT pin bit mask for direct port manipulation in the form 0b11101111
    
    dual endstop port and bitmasks
    */
    int8_t _maxPin = -1;
    int8_t _minPin = -1;
    /*
    uint8_t _maxPin_mask;
    const volatile uint16_t *_maxPin_Inputport;
    uint8_t _minPin_mask;
    const volatile uint16_t *_minPin_Inputport; */

    //AVR was 
    //volatile uint8_t *_maxPin_Inputport;
    //volatile uint8_t *_minPin_Inputport;

    // non mandatory variable
    int _slow_spd_timing = 500;
    int _fast_spd_timing = 500;
    //int _acceleration_length = 50;
    //int _deceleratiob_length = 55;
    int _go_fast_switch;
    int _decelerate_switch;
    uint8_t _acceleration_counter;
    int32_t _max_range = 2147483647;
    int32_t _min_range = -2147483648;
    float _acceleration_factor = 0.01;

    // others important values
    uint32_t _last_step_time = 0; // only for timed step
    int32_t _current_pos;
    int8_t _last_dir = -1;
    int _hyst_steps = 0;

    //Options
    bool _invert = false;
    bool _use_pin_mode = false;

    
    
};

// keywords
#endif

/* template to get the sign of a value, to feed to the set_direction functions*/
template <typename T> int sgn(T val) {
    return (T(0) < val) - (val < T(0));
}