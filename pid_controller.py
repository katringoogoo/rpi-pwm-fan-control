
class PIDController:
    def __init__(self, time, kp, ki, kd, tau, lim_min, lim_max):
        self._kp = kp
        self._ki = ki
        self._kd = kd
        self._tau = tau
        self._lim_min = lim_min
        self._lim_max = lim_max
        self._time = time
        self._integrator = 0
        self._prev_delta = 0
        self._differentiator = 0
        self._prev_measure = 0
        self._out = 0

    def update(self, setpoint, measure):
        delta_value = setpoint-measure
        # error=measure-setpoint
        
        # Proportional gain
        proportional = self._kp * delta_value
        
        # Integral gain
        self._integrator += 0.5 * self._ki * self._time * (delta_value + self._prev_delta)
        
        # Anti-wind-up
        if self._lim_max > proportional:
            integrator_lim_max = self._lim_max - proportional
        else:
            integrator_lim_max = 0
            
        if self._lim_min < proportional:
            integrator_lim_min = self._lim_min - proportional
        else:
            integrator_lim_min = 0
            
        # Clamp integrator
        if self._integrator > integrator_lim_max:
            self._integrator = integrator_lim_max
        else:
            self._integrator = integrator_lim_min
            
        # Differentiator gain
        d = 2 * self._kd * measure - self._prev_measure
        a = 2 * self._tau - self._time
        b = 2 * self._tau + self._time
        self._differentiator = a * self._differentiator / b + d
        
        # Calculate output
        self._out = proportional+self._integrator+self._differentiator
        
        # Apply limits
        if self._out > self._lim_max:
            self._out = self._lim_max
        elif self._out < self._lim_min:
            self._out = self._lim_min
            
        # Store data
        self._prev_delta = delta_value
        self._prev_measure = measure

    @property
    def value(self):
        return self._out
