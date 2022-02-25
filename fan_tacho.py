import time

from gpiozero import DigitalInputDevice


class FanTacho:
    def __init__(self, pin, pull_up=True, pulses_per_rotation = 2):
        self._hertz_to_rpm = 60.0 / pulses_per_rotation
        
        self._current_rpm = 0
        self._rpm_pulses = 0
        self._rpm_start_time = time.time()
        
        self._tacho = DigitalInputDevice(pin=pin, pull_up=pull_up)
        self._tacho.when_deactivated = lambda _: self._on_interrupt()     
    
    def _on_interrupt(self):        
        self._rpm_pulses += 1        
        
    def update(self):
        diff_time = time.time() - self._rpm_start_time
        frequency = self._rpm_pulses / diff_time
        self._current_rpm = int(frequency * self._hertz_to_rpm)
        self._rpm_start_time = time.time()
        self._rpm_pulses = 0
        
    @property
    def rpm(self):
        return self._current_rpm