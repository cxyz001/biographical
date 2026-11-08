import pathlib
import tempfile
import unittest
import wave
from fractions import Fraction

from media_lab import inspect_wav, rescale_exact, simulate_latest, write_tone


class MediaTest(unittest.TestCase):
    def test_generated_pcm_duration_and_size(self):
        with tempfile.TemporaryDirectory() as directory:
            p = pathlib.Path(directory)/'tone.wav'
            write_tone(p)
            self.assertEqual(inspect_wav(p), dict(channels=1,sample_width=2,
                sample_rate=16000,frames=32000,duration=2,pcm_bytes=64000))
            with wave.open(str(p),'rb') as source:
                self.assertEqual(len(source.readframes(32000)), 64000)

    def test_tone_rejects_aliasing_and_invalid_duration(self):
        for kwargs in [dict(frequency=8000),dict(seconds=0),dict(seconds=float('nan')),
                       dict(rate=True),dict(rate=1),dict(frequency=-1)]:
            with self.assertRaises(ValueError): write_tone('unused.wav',**kwargs)

    def test_time_base_and_fractional_ticks(self):
        self.assertEqual(rescale_exact(90000,Fraction(1,90000),Fraction(1,1000)),1000)
        self.assertEqual(rescale_exact(1024,Fraction(1,48000),Fraction(1,1000)),Fraction(64,3))
        self.assertEqual(rescale_exact(-9000,Fraction(1,90000),Fraction(1,1000)),-100)
        with self.assertRaises(ValueError): rescale_exact(1,Fraction(0),Fraction(1))

    def test_slow_consumer_drops_oldest_without_exceeding_bound(self):
        result=simulate_latest()
        self.assertEqual(result['consumed'],[1,5,9])
        self.assertEqual(result['dropped'],[0,2,3,4,6,7,8])
        self.assertEqual(result['pending'],[10,11])
        self.assertEqual(result['peak'],3)
        self.assertEqual(sorted(result['consumed']+result['dropped']+result['pending']),list(range(12)))

    def test_fast_consumer_and_invalid_capacity(self):
        result=simulate_latest(1,10,1)
        self.assertEqual(result['consumed'],list(range(10)))
        self.assertEqual(result['dropped'],[])
        for value in [0,-1,True,1.5]:
            with self.assertRaises(ValueError): simulate_latest(value)


if __name__ == '__main__': unittest.main()
