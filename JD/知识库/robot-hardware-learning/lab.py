"""Offline engineering arithmetic and production-record checks; no hardware IO."""
import argparse
import csv
from decimal import Decimal
import json
import math
import pathlib


def positive(value, name, allow_zero=False):
    number = float(value)
    if not math.isfinite(number) or (number < 0 if allow_zero else number <= 0):
        raise ValueError(f'invalid {name}')
    return number


def differential_wheels(linear, angular, radius, track):
    """Ideal rolling kinematic conversion only; not a motor command generator."""
    linear, angular = float(linear), float(angular)
    if not all(math.isfinite(x) for x in (linear, angular)):
        raise ValueError('nonfinite velocity')
    radius, track = positive(radius, 'radius'), positive(track, 'track')
    return ((linear-angular*track/2)/radius, (linear+angular*track/2)/radius)


def energy_wh(samples):
    """Integrate measured real power, ordered seconds, using trapezoids."""
    if len(samples) < 2:
        raise ValueError('at least two samples required')
    total = Decimal(0)
    previous = None
    for timestamp, power in samples:
        timestamp, power = Decimal(str(timestamp)), Decimal(str(power))
        if not timestamp.is_finite() or not power.is_finite() or timestamp < 0 or power < 0:
            raise ValueError('expected finite nonnegative seconds and watts')
        if previous is not None:
            old_t, old_p = previous
            if timestamp <= old_t:
                raise ValueError('timestamps must strictly increase')
            total += (timestamp-old_t)*(power+old_p)/2/3600
        previous = timestamp, power
    return total


def power_budget(loads, efficiency):
    """Single converter estimate; not a wire, fuse or supply selection rule."""
    efficiency = positive(efficiency, 'efficiency')
    if efficiency > 1:
        raise ValueError('efficiency must be <= 1')
    if not loads:
        raise ValueError('loads required')
    output = sum(positive(v, 'volts')*positive(i, 'amps', True) for v,i in loads)
    return dict(output_w=output, input_w=output/efficiency, loss_w=output/efficiency-output)


def classify_measurement(value, lower, upper, uncertainty):
    """Illustrative conservative guard band; project rules must be approved."""
    value, lower, upper, uncertainty = map(float, (value,lower,upper,uncertainty))
    if not all(math.isfinite(x) for x in (value,lower,upper,uncertainty)) or lower > upper or uncertainty < 0:
        raise ValueError('invalid measurement or limits')
    if value-uncertainty >= lower and value+uncertainty <= upper:
        return 'pass'
    if value+uncertainty < lower or value-uncertainty > upper:
        return 'fail'
    return 'review'


def audit_csv(path):
    results, seen = [], set()
    with pathlib.Path(path).open(encoding='utf-8', newline='') as source:
        reader = csv.DictReader(source)
        required = {'serial','board_rev','firmware','value_v','lower_v','upper_v','uncertainty_v'}
        if not required <= set(reader.fieldnames or []):
            raise ValueError('missing CSV columns')
        for row in reader:
            for key in ('serial','board_rev','firmware'):
                if not row[key].strip(): raise ValueError(f'empty {key}')
            if row['serial'] in seen: raise ValueError('duplicate serial; explicit retest policy required')
            seen.add(row['serial'])
            state = classify_measurement(row['value_v'], row['lower_v'],row['upper_v'],row['uncertainty_v'])
            results.append(dict(serial=row['serial'],board_rev=row['board_rev'],firmware=row['firmware'],result=state))
    if not results: raise ValueError('no measurements')
    return results


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['kinematics','energy','budget','audit'])
    parser.add_argument('--csv',type=pathlib.Path,default=pathlib.Path(__file__).with_name('measurements.csv'))
    args=parser.parse_args()
    if args.command=='kinematics':
        left,right=differential_wheels(0.2,0.5,0.05,0.3)
        result=dict(left_rad_s=left,right_rad_s=right)
    elif args.command=='energy': result=dict(energy_wh=str(energy_wh([(0,1000),(3600,1000)])))
    elif args.command=='budget': result=power_budget([(5,0.4),(3.3,0.2)],0.9)
    else: result=audit_csv(args.csv)
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__': main()
