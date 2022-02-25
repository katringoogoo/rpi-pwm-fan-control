from pid_controller import PIDController

DELTA_T = 1

# PID Parameters
KP = 2
KI = 1
KD = 1

MIN_LIMIT = -100
MAX_LIMIT = 100


def test_pid_controller():
    c = PIDController(DELTA_T, KP, KI, KD, MIN_LIMIT, MAX_LIMIT,
                      positive_feedback=True)

    for i in range(30, 55, 1):
        c.calculate(30, i)
        print(f'temp = {i} value = {c.output}')

    for i in range(55, 40, -1):
        c.calculate(30, i)
        print(f'temp = {i} value = {c.output}')


test_pid_controller()
