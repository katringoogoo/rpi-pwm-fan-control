#!/usr/bin/env python3

import time

from gpiozero import PWMLED

from fan_tacho import FanTacho
from pid_controller import PIDController
from value_mapper import ValueMapper


PWM_PIN = 'GPIO6'
TACHO_PIN = 'GPIO12'

TARGET_TEMP = 38
MAX_TEMP = 50

FAN_MIN = 30
FAN_MAX = 100

DELTA_T = 1

# PID Parameters
KP = 2
KI = 1
KD = 1

MIN_LIMIT = -100
MAX_LIMIT = 100


def get_cpu_temp():
    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
        temp = f.readline()
        return round(float(temp)/1000, 2)


def main():
    fan = PWMLED(PWM_PIN, frequency=25000)
    fan.value = 1.0    # set to 100% in the beginning

    tacho = FanTacho(TACHO_PIN)

    pid_controller = PIDController(DELTA_T, KP, KI, KD, MIN_LIMIT, MAX_LIMIT,
                                   positive_feedback=True)

    mapper = ValueMapper(MIN_LIMIT, MAX_LIMIT, FAN_MIN, FAN_MAX)

    while True:
        tacho.update()

        current_cpu_temp = get_cpu_temp()

        pid_controller.calculate(TARGET_TEMP, current_cpu_temp)

        controller_value = pid_controller.output

        fan_pwm_duty = round(mapper.map(controller_value), 2)

        print(f'controller_value: {controller_value} -> mapped: {fan_pwm_duty}')

        # override
        if current_cpu_temp > MAX_TEMP:
            # set to 100% in case we are overtemp
            fan_pwm_duty = FAN_MAX

        # actually set fan value
        fan.value = fan_pwm_duty / 100.0

        print(f'CPU Temp: {current_cpu_temp} C - Fan: {tacho.rpm} rpm - Fan PWM: {fan_pwm_duty} %')

        time.sleep(DELTA_T)


if __name__ == '__main__':
    main()
