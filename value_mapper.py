
class ValueMapper:
    def __init__(self, input_min: float, input_max: float, output_min: float, output_max: float):
        input_value_range = input_max - input_min
        output_value_range = output_max - output_min
        
        self._factor: float = output_value_range / input_value_range
        self._input_min: float = input_min
        self._output_min: float = output_min
         
    def __call__(self, input_value: float) -> float:
        return self._output_min + self._factor * (input_value - self._input_min)
