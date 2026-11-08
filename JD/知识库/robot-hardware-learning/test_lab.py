from decimal import Decimal
import pathlib
import tempfile
import unittest

from lab import differential_wheels, energy_wh, power_budget, classify_measurement, audit_csv


class EngineeringTest(unittest.TestCase):
    def test_straight_turn_and_rotation(self):
        self.assertEqual(differential_wheels(.2,0,.05,.3),(4,4))
        left,right=differential_wheels(0,1,.05,.3)
        self.assertAlmostEqual(left,-3)
        self.assertAlmostEqual(right,3)
        left,right=differential_wheels(.2,.5,.05,.3)
        self.assertAlmostEqual(left,2.5)
        self.assertAlmostEqual(right,5.5)

    def test_invalid_geometry_and_velocity(self):
        for args in [(1,0,0,.3),(1,0,.05,-1),(float('nan'),0,.05,.3)]:
            with self.assertRaises(ValueError): differential_wheels(*args)

    def test_energy_units_and_nonuniform_sampling(self):
        self.assertEqual(energy_wh([(0,1000),(3600,1000)]),Decimal(1000))
        self.assertEqual(energy_wh([(0,0),(1800,1000),(3600,0)]),Decimal(500))
        self.assertEqual(energy_wh([(0,3600),(1,3600),(3,3600)]),Decimal(3))

    def test_energy_rejects_bad_order_and_missing_samples(self):
        for samples in [[(0,1)],[(1,1),(0,1)],[(0,1),(0,2)],[(0,1),(1,'NaN')],[(0,-1),(1,2)]]:
            with self.assertRaises(ValueError): energy_wh(samples)

    def test_power_balance(self):
        budget=power_budget([(5,.4),(3.3,.2)],.9)
        self.assertAlmostEqual(budget['output_w'],2.66)
        self.assertAlmostEqual(budget['input_w']-budget['loss_w'],2.66)
        for efficiency in [0,1.1,float('nan')]:
            with self.assertRaises(ValueError): power_budget([(5,1)],efficiency)

    def test_measurement_guard_band(self):
        self.assertEqual(classify_measurement(3.30,3.20,3.40,.02),'pass')
        self.assertEqual(classify_measurement(3.39,3.20,3.40,.02),'review')
        self.assertEqual(classify_measurement(3.50,3.20,3.40,.02),'fail')
        with self.assertRaises(ValueError): classify_measurement(3,4,2,.01)

    def test_traceability_csv_and_duplicate_rejection(self):
        source=pathlib.Path(__file__).with_name('measurements.csv')
        self.assertEqual([x['result'] for x in audit_csv(source)],['pass','review','fail'])
        with tempfile.TemporaryDirectory() as directory:
            path=pathlib.Path(directory)/'duplicate.csv'
            lines=source.read_text(encoding='utf-8').splitlines()
            path.write_text('\n'.join([lines[0],lines[1],lines[1]]),encoding='utf-8')
            with self.assertRaises(ValueError): audit_csv(path)


if __name__=='__main__': unittest.main()
