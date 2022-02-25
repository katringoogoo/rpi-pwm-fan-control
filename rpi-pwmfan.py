#!/usr/bin/env python3

import argparse
import atexit
import io
import time

from gpiozero import PWMLED

from fan_tacho import FanTacho
from pid_controller import PIDController
from value_mapper import ValueMapper


########################################################################
# Set up some default values (can be overridden from cmdline)

PWM_PIN = 'GPIO12'
TACHO_PIN = 'GPIO6'

MIN_TEMP = 35
TARGET_TEMP = 40
MAX_TEMP = 45

FAN_MIN = 0.2
FAN_MAX = 1.0

DELTA_T = 2

# PID Parameters
KP = 2
KI = 1
KD = 1

PDI_LOWER_LIMIT = -100
PDI_UPPER_LIMIT = 100

PWM_FREQUENCY = 50

########################################################################


def get_cpu_temp():
    with io.open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
        return round(float(f.read().strip()) / 1000, 2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-pp', '--pin-pwm', type=str, default=PWM_PIN, help=f'PWM PIN e.g. {PWM_PIN}')
    parser.add_argument('-pt', '--pin-tacho', type=str, default=TACHO_PIN, help=f'Fan Tacho PIN e.g. {TACHO_PIN}')
    parser.add_argument('-t', '--target-temp', type=float, default=TARGET_TEMP, help='Target temperature')
    parser.add_argument('-tl', '--minimum-temp', type=float, default=MIN_TEMP, help='Minimum temperature, below fan is turned off')
    parser.add_argument('-tu', '--maximum-temp', type=float, default=MAX_TEMP, help='Maximum temperature, abive this value the fan runs at full speed')
    parser.add_argument('-fl', '--minimum-fan-duty-cycle', type=float, default=FAN_MIN, help=f'Minimum duty cycle of the fan (usually {FAN_MIN})')
    parser.add_argument('-fu', '--maximum-fan-duty-cycle', type=float, default=FAN_MAX, help=f'Maximum duty cycle of the fan {FAN_MAX}')
    parser.add_argument('-u', '--update-time', type=float, default=DELTA_T, help='Update time for all internal values')
    parser.add_argument('-kp', type=float, default=KP, help='PDI Controller proportional factor')
    parser.add_argument('-ki', type=float, default=KI, help='PDI Controller integrative factor')
    parser.add_argument('-kd', type=float, default=KD, help='PDI Controller derivative factor')
    parser.add_argument('-ll', '--pdi-lower-limit', type=float, default=PDI_LOWER_LIMIT, help='PDI Controller output value lower limit')
    parser.add_argument('-ul', '--pdi-upper-limit', type=float, default=PDI_UPPER_LIMIT, help='PDI Controller output value upper limit')
    parser.add_argument('-f', '--pwm-frequency', type=float, default=PWM_FREQUENCY, help='PWM Output frequency')
    parser.add_argument('-s', '--silent', action='store_true', help='Do not output any console logs')
    parser.add_argument('--use-pigpio', action='store_true', help='Use the pigpio library to support hardware PWM - see README before using')
    args = parser.parse_args()
    
    if args.use_pigpio:
        from gpiozero import Device
        from gpiozero.pins.pigpio import PiGPIOFactory
        Device.pin_factory = PiGPIOFactory()
    
    fan = PWMLED(args.pin_pwm, frequency=args.pwm_frequency)
    
    # make sure that we start with 100% an end with 100% fan power
    def fan_to_full():
        fan.value = 1.0
    
    fan_to_full()
    atexit.register(fan_to_full)

    tacho = FanTacho(args.pin_tacho)

    pid_controller = PIDController(args.update_time, 
                                   args.kp, args.ki, args.kd, 
                                   args.pdi_lower_limit, args.pdi_upper_limit,
                                   positive_feedback=True)

    value_mapper = ValueMapper(args.pdi_lower_limit, args.pdi_upper_limit,
                               args.minimum_fan_duty_cycle, args.maximum_fan_duty_cycle)

    while True:
        tacho.update()

        current_cpu_temp = get_cpu_temp()

        pid_controller.calculate(args.target_temp, current_cpu_temp)

        controller_value = pid_controller.output

        fan_pwm_duty = round(value_mapper(controller_value), 2)

        # print(f'controller_value: {controller_value} -> mapped: {fan_pwm_duty}')

        # override (this is more like a safeguard)
        limit = ''
        if current_cpu_temp < args.minimum_temp:
            # turn fan off if we're below min temp
            fan_pwm_duty = 0.0
            limit = 'l'
        if current_cpu_temp > args.maximum_temp:
            # set to 100% in case we are overtemp
            fan_pwm_duty = 1.0
            limit = 'h'

        # actually set fan value
        fan.value = fan_pwm_duty 

        if args.silent is False:
            print(f'CPU Temp: {current_cpu_temp} C - Fan: {tacho.rpm} rpm - Fan PWM: {fan_pwm_duty*100:.2f} % {limit}')

        time.sleep(args.update_time)


if __name__ == '__main__':   
    main()
