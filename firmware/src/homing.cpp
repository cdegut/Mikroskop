#include <main.h>

void run_loop(Stepstick &axis) {
  while (axis.get_state() != OFF) {
    axis.run();
    delayMicroseconds(5);
  }
}

void run_loop(Stepstick &axis1, Stepstick &axis2) {
  while (true) {

    axis1.run();
    axis2.run();
    delayMicroseconds(5);

    if (axis1.get_state() == OFF && axis2.get_state() == OFF) {
      break;
    }
  }
}

void run_loop(Stepstick &axis1, Stepstick &axis2, Stepstick &axis3) {
  while (true) {

    axis1.run();
    axis2.run();
    axis3.run();
    delayMicroseconds(5);

    if (axis1.get_state() == OFF && axis2.get_state() == OFF && axis3.get_state() != OFF) {
      break;
    }
  }
}

void home_XYF(uint16_t bump) {

  X.timing = Xslowspd;
  Y.timing = Yslowspd;
  Focus.timing = Fslowspd;

/* FOCUS AXIS */

  //4 full step +
  Focus.set_direction(1, false);
  Focus.set_step_counter(4*FmicroStep);
  Focus.switch_state(TIMER_COUNTED_STEP);
  run_loop(Focus);

  //find 0 init
  Focus.set_direction(-1, false);
  Serial.println("Finding 0 for focus axis");
  Focus.switch_state(init_TIMER_STALLGUARD);
  run_loop(Focus);
  Focus.override_position(0);
  Serial.print("Focus stalled with a value of:");
  Serial.println(Focus.last_stall_value);

  // Bump focus
  Focus.set_destination(bump);
  Serial.println("Bump!");
  Focus.switch_state(GO);
  run_loop(Focus);

  // Focus autoeval
  Focus.set_direction(-1, false);
  Serial.print("Focus StallGuard Value autoevaluation:"); 
  int SG_value = Focus.evaluate_SGTHRS(bump/2);
  int SGTHRS = (SG_value/FSg_autoeval_divider);
  Serial.println(SG_value);
  Serial.print("Focus STGTHRS: ");
  Serial.println(SGTHRS);
  Focus.config_SG_thresold(SGTHRS);

  // definite 0 focus
  Serial.println("Finding 0 again with new values");
  Focus.switch_state(init_TIMER_STALLGUARD);
  run_loop(Focus);
  Focus.override_position(0);
  Serial.print("Focus stalled with a value of:");
  Serial.println(Focus.last_stall_value);

/* XY axes */
  //4 full step +
  X.set_direction(1, false);
  X.set_step_counter(4*XmicroStep);
  X.switch_state(TIMER_COUNTED_STEP);
  Y.set_direction(1, false);
  Y.set_step_counter(4*YmicroStep);
  Y.switch_state(TIMER_COUNTED_STEP);
  run_loop(X,Y);

  //find 0 init 
  Serial.println("Finding 0 for X and Y axes");
  X.set_direction(-1, false);
  X.switch_state(init_TIMER_STALLGUARD);
  run_loop(X);

  Y.set_direction(-1, false);
  Y.switch_state(init_TIMER_STALLGUARD);
  run_loop(Y);
  Serial.print("X stalled with a value of:");
  Serial.println(X.last_stall_value);
  Serial.print("Y stalled with a value of:");
  Serial.println(Y.last_stall_value);
  X.override_position(0);
  Y.override_position(0);

  // Bump XY
  X.set_destination(bump);
  Y.set_destination(bump);
  X.switch_state(GO);
  Y.switch_state(GO);

  Serial.println("Bump!");
  run_loop(X,Y);

  Y.set_direction(-1, false);
  Serial.print("Y StallGuard Value autoevaluation:");
  SG_value = Y.evaluate_SGTHRS(bump/2);
  SGTHRS = (SG_value/YSg_autoeval_divider);
  Serial.println(SG_value);
  Serial.print("Y STGTHRS: ");
  Serial.println(SGTHRS);
  Y.config_SG_thresold(SGTHRS);

  X.set_direction(-1, false);
  Serial.print("X StallGuard Value autoevaluation:");
  SG_value = X.evaluate_SGTHRS(bump/2);
  SGTHRS = (SG_value/XSg_autoeval_divider);
  X.config_SG_thresold(SGTHRS);
  Serial.println(SG_value);
  Serial.print("X STGTHRS: ");
  Serial.println(SGTHRS);

  X.timing = Xslowspd;
  Y.timing = Yslowspd;
  Focus.timing = Fslowspd;
  // definite 0 focus
  Serial.println("Finding 0 again with new values");
  X.switch_state(init_TIMER_STALLGUARD);
  Y.switch_state(init_TIMER_STALLGUARD);
  run_loop(X);
  Serial.print("X stalled with a value of:");
  Serial.println(X.last_stall_value);

  run_loop(Y);
  Serial.print("Y stalled with a value of:");
  Serial.println(Y.last_stall_value);
  X.override_position(0);
  Y.override_position(0);

}
