"""Atmosferik arka plan müziği üret (assets/muzik/ambiyans.wav)."""

import math
import os
import struct
import wave

OUT = os.path.join(os.path.dirname(__file__), '..', 'assets', 'muzik', 'ambiyans.wav')
SR = 22050
SURE_SN = 48


def _olustur():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    n = SR * SURE_SN
    freqs = (55.0, 73.4, 98.0, 146.8)
    with wave.open(OUT, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        for i in range(n):
            t = i / SR
            s = 0.0
            for j, f in enumerate(freqs):
                s += (0.09 - j * 0.012) * math.sin(2 * math.pi * f * t + math.sin(t * 0.07 * (j + 1)))
            s += 0.03 * math.sin(2 * math.pi * 3.2 * t)  # hafif titreme
            env = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * 0.04))
            s *= env
            s = max(-1.0, min(1.0, s)) * 0.55
            w.writeframes(struct.pack('<h', int(s * 32767)))
    print(f'OK {OUT}', flush=True)


if __name__ == '__main__':
    _olustur()
