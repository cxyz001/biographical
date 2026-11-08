"""Dependency-free PCM, timestamp and bounded decoded-frame exercises."""
import argparse
from collections import deque
from fractions import Fraction
import json
import math
import pathlib
import struct
import wave


def write_tone(path, seconds=2, rate=16000, frequency=440):
    if not math.isfinite(seconds) or not 0 < seconds <= 30:
        raise ValueError('seconds must be in (0, 30]')
    if not isinstance(rate, int) or isinstance(rate, bool) or not 8000 <= rate <= 96000:
        raise ValueError('rate must be an integer in [8000, 96000]')
    if not math.isfinite(frequency) or not 0 < frequency < rate / 2:
        raise ValueError('frequency must be below Nyquist frequency')
    with wave.open(str(path), 'wb') as output:
        output.setparams((1, 2, rate, 0, 'NONE', 'not compressed'))
        for start in range(0, int(seconds * rate), 1024):
            end = min(start + 1024, int(seconds * rate))
            samples = (round(0.25 * 32767 * math.sin(2 * math.pi * frequency * i / rate))
                       for i in range(start, end))
            output.writeframesraw(b''.join(struct.pack('<h', x) for x in samples))


def inspect_wav(path):
    with wave.open(str(path), 'rb') as source:
        return dict(channels=source.getnchannels(), sample_width=source.getsampwidth(),
                    sample_rate=source.getframerate(), frames=source.getnframes(),
                    duration=source.getnframes() / source.getframerate(),
                    pcm_bytes=source.getnframes()*source.getnchannels()*source.getsampwidth())


def rescale_exact(timestamp, source_base, target_base):
    """Return a rational count of target ticks; this is NOT FFmpeg rounding."""
    if source_base <= 0 or target_base <= 0:
        raise ValueError('time bases must be positive')
    return Fraction(timestamp) * source_base / target_base


def simulate_latest(capacity=3, frames=12, consume_every=4):
    """Single-thread discrete simulation for decoded AI frames, not H264 packets."""
    for x in (capacity, frames, consume_every):
        if not isinstance(x, int) or isinstance(x, bool) or x <= 0:
            raise ValueError('parameters must be positive integers')
    queue = deque()
    consumed, dropped = [], []
    peak = 0
    for frame in range(frames):
        if len(queue) == capacity:
            dropped.append(queue.popleft())
        queue.append(frame)
        peak = max(peak, len(queue))
        if (frame + 1) % consume_every == 0:
            consumed.append(queue.popleft())
    return dict(consumed=consumed, dropped=dropped, pending=list(queue), peak=peak)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    tone = sub.add_parser('tone')
    tone.add_argument('output', type=pathlib.Path)
    inspect = sub.add_parser('inspect')
    inspect.add_argument('input', type=pathlib.Path)
    sub.add_parser('timeline')
    sub.add_parser('queue')
    args = parser.parse_args()
    if args.command == 'tone':
        write_tone(args.output)
        result = inspect_wav(args.output)
    elif args.command == 'inspect':
        result = inspect_wav(args.input)
    elif args.command == 'timeline':
        result = dict(video_ticks=90000, source_base='1/90000', target_base='1/1000',
                      target_ticks=str(rescale_exact(90000, Fraction(1,90000), Fraction(1,1000))),
                      audio_1024_samples_seconds=str(Fraction(1024,48000)))
    else:
        result = simulate_latest()
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
