
class ValueMapper:
    def __init__(self, input_min, input_max, output_min, output_max):
        input_value_range = input_max - input_min
        output_value_range = output_max - output_min
        
        self._factor = output_value_range / input_value_range
        self._input_min = input_min
        self._output_min = output_min
        
    def map(self, input_value):
        return self._output_min + self._factor * (input_value - self._input_min)
