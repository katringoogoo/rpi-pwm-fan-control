#!/usr/bin/env python3

from time import sleep, time

from gpiozero import PWMLED, DigitalInputDevice

from pid_controller import PIDController

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


class FanControl:
    PULSES_PER_ROTATION = 2
    FAN_FACTOR = 60 / PULSES_PER_ROTATION
    
    def __init__(self, tacho_pin, pwm_pin, target_temp, max_temp):
        self.fan = PWMLED(pwm_pin, frequency=25000)
        self.fan.value = 1.0

        self.last_rpm = 0
        self.rpm_pulses = 0        
        self.rpm_start_time = time()
        self.tacho = DigitalInputDevice(tacho_pin, pull_up=True)
        self.tacho.when_deactivated = lambda _: self._on_tacho_interrupt()        
        
        self.last_cpu_temp = 0
        
        self.pid_controller = PIDController(DELTA_T, KP, KI, KD, MIN_LIMIT, MAX_LIMIT, 
                                            positive_feedback=True)
        self.target_temp = target_temp
        self.max_temp = max_temp
     
    def _on_tacho_interrupt(self):
        self.rpm_pulses += 1
        
    def _get_rpm(self):
        diff_time = time() - self.rpm_start_time
        frequency = self.rpm_pulses / diff_time
        rpm = int(frequency * self.FAN_FACTOR)
        self.rpm_start_time = time()
        self.rpm_pulses = 0
        return rpm

    def _get_cpu_temp(self):
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = f.readline()
            return round(float(temp)/1000, 2)

    def _get_fan_value(self):
        self.pid_controller.update(self.target_temp, self.last_cpu_temp)
        
        input_value = self.pid_controller.output

        value_range = MAX_LIMIT - MIN_LIMIT
                
        output_range = FAN_MAX - FAN_MIN
        
        value_in_percent = FAN_MIN + ((output_range / value_range) * (input_value - MIN_LIMIT))

        print(f'input_value: {input_value} -> output_value: {value_in_percent}')
        
        # override
        if self.last_cpu_temp > self.max_temp:
            # set to 100% in case we are overtemp
            value_in_percent = FAN_MAX

        return round(value_in_percent, 2)

    def update(self):
        self.last_cpu_temp = self._get_cpu_temp()
        self.last_rpm = self._get_rpm()
        self.fan_pwm_duty = self._get_fan_value()
        
        # actually set fan value
        self.fan.value = self.fan_pwm_duty / 100.0
    
    def print_current(self):
        print(f'CPU Temp: {self.last_cpu_temp} C - Fan: {self.last_rpm} rpm - Fan PWM: {self.fan_pwm_duty} %')


def main():
    fan_control = FanControl(tacho_pin=TACHO_PIN, pwm_pin=PWM_PIN,
                             target_temp=TARGET_TEMP, max_temp=MAX_TEMP)

    while True:
        fan_control.update()
        fan_control.print_current()
        sleep(DELTA_T)


if __name__ == '__main__':
    main()
