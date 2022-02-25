
from typing import List


class PIDController:
    def __init__(self, dt: float, kp: float, ki: float, kd: float, min_limit: float, max_limit: float,
                 positive_feedback: bool = False):
        self._min_limit: float = min_limit
        self._max_limit: float = max_limit

        self._positive_feedback: bool = positive_feedback

        self._output_value: float = 0
        
        self._a0: float = kp + ki * dt + kd / dt
        self._a1: float = -kp - 2 * kd / dt
        self._a2: float = kd / dt

        # print(f'A0={self._a0} - A1={self._a1} - A2={self._a2}')

        self._error: List[float] = [0.0, 0.0, 0.0]

    def calculate(self, target_value: float, measured_value: float):
        self._error[2] = self._error[1]
        self._error[1] = self._error[0]
        self._error[0] = target_value - measured_value

        final_output = self._output_value + self._a0 * self._error[0] + self._a1 * self._error[1] + self._a2 * self._error[2]

        # clamp output value
        if final_output < self._min_limit:
            final_output = self._min_limit
        if final_output > self._max_limit:
            final_output = self._max_limit
            
        self._output_value = final_output

        # print(f'error={self._error} output={self._output}')

    @property
    def output(self) -> float:
        return -self._output_value if self._positive_feedback else self._output_value
