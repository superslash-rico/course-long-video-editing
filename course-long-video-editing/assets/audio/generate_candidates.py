"""Generate original deterministic sound candidates; no third-party samples. Not an audio edit."""
import argparse
import math
import random
import struct
import wave
from pathlib import Path

RATE = 48000


def create(kind, seconds, seed):
    rng = random.Random(seed)
    result = []
    low = 0.0
    for i in range(round(RATE * seconds)):
        t = i / RATE
        u = t / seconds
        noise = rng.uniform(-1, 1)
        low += (noise - low) * (0.035 + 0.14 * u)
        if kind == 'soft-whoosh':
            env = math.sin(math.pi * u) ** 2
            sample = env * (low * 0.9 + noise * 0.10)
        elif kind == 'paper-settle':
            env = (1 - math.exp(-t * 140)) * math.exp(-t * 25) * (1 - u) ** 2
            sample = env * (noise * .22 + low * .7 + math.sin(2 * math.pi * 140 * t) * .12)
        else:
            env = (1 - math.exp(-t * 250)) * math.exp(-t * 85) * (1 - u) ** 2
            sample = env * (low * .4 + math.sin(2 * math.pi * 720 * t) * .4)
        result.append(sample)
    peak = max(abs(x) for x in result) or 1
    gain = 10 ** (-14 / 20) / peak
    # A silent endpoint avoids an edit click; noise/phase never depends on wall-clock.
    result[0] = result[-1] = 0.0
    return [max(-1, min(1, x * gain)) for x in result]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for kind, seconds, seed in [('soft-whoosh', .52, 301), ('paper-settle', .22, 302), ('select-soft', .10, 303)]:
        samples = create(kind, seconds, seed)
        data = b''.join(struct.pack('<hh', round(x * 32767), round(x * 32767)) for x in samples)
        with wave.open(str(args.output / (kind + '.wav')), 'wb') as output:
            output.setnchannels(2)
            output.setsampwidth(2)
            output.setframerate(RATE)
            output.writeframes(data)


if __name__ == '__main__':
    main()
