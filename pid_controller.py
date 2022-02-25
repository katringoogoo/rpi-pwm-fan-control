
class PIDController:
    def __init__(self, dt, kp, ki, kd, min_limit, max_limit, positive_feedback=False):
        self._dt = dt
        
        self._kp = kp
        self._ki = ki
        self._kd = kd

        self._min_limit = min_limit
        self._max_limit = max_limit

        self._positive_feedback = positive_feedback

        self._output  = 0
        
        self._a0 = kp + ki * dt + kd / dt
        self._a1 = -kp - 2 * kd / dt
        self._a2 = kd / dt

        # print(f'A0={self._a0} - A1={self._a1} - A2={self._a2}')

        self._error = [0, 0, 0]

    def update(self, setpoint, measured_value):
        self._error[2] = self._error[1]
        self._error[1] = self._error[0]
        self._error[0] = setpoint - measured_value

        final_output = self._output + self._a0 * self._error[0] + self._a1 * self._error[1] + self._a2 * self._error[2]

        if final_output < self._min_limit:
            final_output = self._min_limit
        if final_output > self._max_limit:
            final_output = self._max_limit
            
        self._output = final_output

        print(f'error={self._error} output={self._output}')

    @property
    def output(self):
        final_output = self._output
        if self._positive_feedback:
            final_output *= -1
        return final_output
