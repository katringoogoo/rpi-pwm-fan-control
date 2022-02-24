#!/usr/bin/env python3

from time import sleep, time

from gpiozero import PWMLED, DigitalInputDevice

from pid_controller import PIDController

PWM_PIN = 'GPIO6'
TACHO_PIN = 'GPIO12'

LOW_TEMP = 35
MAX_TEMP = 45

CHECK_SEC = 2

# PID Parameters
KP = 2
KI = 1
KD = 1
TAU = 1
PID_MIN = 0
PID_MAX = 100


class FanControl:
    PULSES_PER_ROTATION = 2
    FAN_FACTOR = 60 / PULSES_PER_ROTATION
    
    def __init__(self, tacho_pin, pwm_pin, low_temp, max_temp):
        self.fan = PWMLED(pwm_pin, frequency=25000)
        self.fan.value = 1.0

        self.last_rpm = 0
        self.rpm_pulses = 0        
        self.rpm_start_time = time()
        self.tacho = DigitalInputDevice(tacho_pin, pull_up=True)
        self.tacho.when_deactivated = lambda _: self._on_tacho_interrupt()        
        
        self.last_cpu_temp = 0
        
        self.pid_controller = PIDController(CHECK_SEC, KP, KI, KD, TAU, PID_MIN, PID_MAX)
        self.low_temp = low_temp
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
        self.pid_controller.update(self.low_temp, self.last_cpu_temp)
        
        new_value = self.pid_controller.value
        if new_value < 0:
            percent_diff = 0
        else:
            percent_diff = new_value

        return round(percent_diff, 2)


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
                             low_temp=LOW_TEMP, max_temp=MAX_TEMP)

    while True:
        fan_control.update()
        fan_control.print_current()
        sleep(CHECK_SEC)


if __name__ == '__main__':
    main()
