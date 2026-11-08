"""Offline Ruckig single-axis trajectory; no hardware output. Requires ruckig."""
from ruckig import InputParameter, OutputParameter, Result, Ruckig


def main():
    generator = Ruckig(1, 0.01)
    request = InputParameter(1)
    output = OutputParameter(1)
    request.current_position = [0.0]
    request.current_velocity = [0.0]
    request.current_acceleration = [0.0]
    request.target_position = [1.0]
    request.target_velocity = [0.0]
    request.target_acceleration = [0.0]
    request.max_velocity = [0.5]
    request.max_acceleration = [1.0]
    request.max_jerk = [2.0]
    print('step,position,velocity,acceleration')
    for step in range(10000):
        result = generator.update(request, output)
        if result not in (Result.Working, Result.Finished):
            raise RuntimeError(f'trajectory failed: {result}')
        print(f'{step},{output.new_position[0]},{output.new_velocity[0]},{output.new_acceleration[0]}')
        if result == Result.Finished:
            return
        output.pass_to_input(request)
    raise RuntimeError('offline iteration limit exceeded')


if __name__ == '__main__': main()
