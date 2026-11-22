import wave

import numpy as np

from timeline3 import (FPS, TOTAL, FIREWORKS, sfx_events)

SR = 44100
DUR = TOTAL / FPS + 0.8
N = int(SR * DUR)
buf = np.zeros(N)

NOTE_OFF = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6,
            'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}


def freq(note):
    name, octv = note[:-1], int(note[-1])
    return 440.0 * 2 ** ((NOTE_OFF[name] + 12 * (octv - 4) - 9) / 12)


def square_wave(ph, duty=0.5):
    return np.where((ph % 1.0) < duty, 1.0, -1.0)


def add_note(t0, dur, f, duty=0.5, vol=0.2, echo=0.0):
    i0 = int(t0 * SR)
    n = int(dur * SR)
    i1 = min(i0 + n, N)
    if i0 >= N:
        return
    t = np.arange(i1 - i0) / SR
    env = np.minimum(1.0, t / 0.006) * np.exp(-t / (dur * 0.75))
    sig = square_wave(t * f, duty) * env * vol
    buf[i0:i1] += sig
    if echo > 0:
        d = int(0.19 * SR)
        j0, j1 = i0 + d, i1 + d
        if j1 <= N:
            buf[j0:j1] += sig[: j1 - j0] * echo


def saw(t0, dur, f0, f1, vol):
    i0 = int(t0 * SR)
    n = int(dur * SR)
    i1 = min(i0 + n, N)
    if i0 >= N:
        return
    t = np.arange(i1 - i0) / SR
    sw = f0 * (f1 / f0) ** (t / dur)
    ph = np.cumsum(sw) / SR
    sig = 2 * (ph % 1.0) - 1.0
    env = np.minimum(1.0, t / 0.004) * np.exp(-t / (dur * 0.5))
    buf[i0:i1] += sig * env * vol


def kick(t0, vol=0.55):
    i0 = int(t0 * SR)
    n = int(0.16 * SR)
    i1 = min(i0 + n, N)
    t = np.arange(i1 - i0) / SR
    f = 120 * np.exp(-t * 22) + 42
    ph = np.cumsum(f) / SR
    buf[i0:i1] += np.sin(2 * np.pi * ph) * np.exp(-t * 18) * vol


def noise_hit(t0, dur, vol, decay=None, seed=0, lowpass=None, attack=0.0):
    i0 = int(t0 * SR)
    n = int(dur * SR)
    i1 = min(i0 + n, N)
    if i0 >= N:
        return
    t = np.arange(i1 - i0) / SR
    r = np.random.default_rng(seed)
    sig = r.uniform(-1, 1, i1 - i0)
    if lowpass is not None:
        k = max(1, int(SR / lowpass))
        sig = np.convolve(sig, np.ones(k) / k, mode='same')
    env = np.exp(-t / (decay if decay else dur * 0.35))
    if attack > 0:
        env *= np.minimum(1.0, t / attack)
    buf[i0:i1] += sig * env * vol


def pop(t0, seed, thump_freq):
    noise_hit(t0, 0.14, 0.22, decay=0.06, seed=seed)
    i0 = int(t0 * SR)
    n = int(0.18 * SR)
    i1 = min(i0 + n, N)
    t = np.arange(i1 - i0) / SR
    f = thump_freq * np.exp(-t * 10) + 45
    buf[i0:i1] += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14) * 0.4


def whistle(t0):
    i0 = int(t0 * SR)
    n = int(0.5 * SR)
    i1 = min(i0 + n, N)
    t = np.arange(i1 - i0) / SR
    sig = square_wave(t * 2250, 0.5)
    warble = 0.6 + 0.4 * np.sin(2 * np.pi * 46 * t)
    env = np.minimum(1.0, t / 0.01) * (0.4 + 0.6 * np.exp(-t / 0.35))
    buf[i0:i1] += sig * warble * env * 0.25


BPM = 136
BEAT = 60 / BPM          # noire : majuscule
E8 = BEAT / 2            # croche : minuscule
LOOP_BEATS = 32
LOOP = LOOP_BEATS * BEAT
MUSIC_T0 = 0.15

# Partition de l'utilisateur (Majuscule = noire, Minuscule = croche) :
# MIB5 SI5 SOL#5 mib6 si6 mib6 si6 mib6 si6 (+2 temps de silence)
# MIB5 SI5 SOL#5 mib6 si6 mib6 si6 mi6 mib6 (+2 temps)
# MIB5 SI5 SOL#5 (+1) SI5 (+1) MIB5 (+1 temps et demi)
# do#5 si5 do#5 (+1) mib6 si6 mib6 si6 mi6 mib6 (+2 temps)
MELODY = [
    (0.0, 'D#6', 1), (1.0, 'B5', 1), (2.0, 'G#5', 1),
    (3.0, 'D#6', .5), (3.5, 'B6', .5), (4.0, 'D#6', .5), (4.5, 'B6', .5),
    (5.0, 'D#6', .5), (5.5, 'B6', .5),
    (8.0, 'D#6', 1), (9.0, 'B5', 1), (10.0, 'G#5', 1),
    (11.0, 'D#6', .5), (11.5, 'B6', .5), (12.0, 'D#6', .5), (12.5, 'B6', .5),
    (13.0, 'E6', .5), (13.5, 'D#6', .5),
    (16.0, 'D#6', 1), (17.0, 'B5', 1), (18.0, 'G#5', 1),
    (20.0, 'B5', 1), (22.0, 'D#6', 1),
    (24.5, 'C#5', .5), (25.0, 'B5', .5), (25.5, 'C#5', .5),
    (27.0, 'D#6', .5), (27.5, 'B6', .5), (28.0, 'D#6', .5), (28.5, 'B6', .5),
    (29.0, 'E6', .5), (29.5, 'D#6', .5),
]
BASS_BARS = ['G#2', 'G#2', 'G#2', 'G#2', 'G#2', 'G#2', 'C#3', 'D#3']


def build_music():
    music_end = (TOTAL / FPS) - 1.3
    nloops = int(np.ceil((music_end - MUSIC_T0) / LOOP)) + 1
    s = 0
    for L in range(nloops):
        base = MUSIC_T0 + L * LOOP
        if base > music_end:
            break
        for (b, note, dur) in MELODY:
            t = base + b * BEAT
            if t >= music_end:
                break
            add_note(t, dur * BEAT * 0.9, freq(note), duty=0.5, vol=0.16,
                     echo=0.22 if dur >= 1 else 0.12)
        for bi in range(8):
            fr = freq(BASS_BARS[bi])
            for k in range(8):
                t = base + (bi * 8 + k) * E8
                if t >= music_end:
                    break
                f = fr if k % 2 == 0 else fr * 2
                add_note(t, E8 * 0.48, f, duty=0.25, vol=0.115)
            # rythme zouk : grosse caisse sur TOUS les demi-temps,
            # caisse claire sur chaque temps, charley sur les contretemps
            for k8 in range(8):
                t = base + (bi * 8 + k8) * E8
                if t >= music_end:
                    break
                onbeat = k8 % 2 == 0
                kick(t, vol=0.62 if onbeat else 0.36)
                if onbeat:
                    noise_hit(t, 0.11, 0.26, decay=0.05, seed=s); s += 1
                else:
                    noise_hit(t, 0.03, 0.085, decay=0.018, seed=s); s += 1


def build_sfx():
    s = 1000
    for t, kind, i in sfx_events():
        if kind == 'kick':
            kick(t, vol=0.5)
            noise_hit(t, 0.08, 0.15, decay=0.03, seed=s); s += 1
        elif kind == 'goal':
            arp = ['C5', 'E5', 'G5', 'C6']
            for j, note in enumerate(arp):
                add_note(t + j * 0.07, 0.22, freq(note), duty=0.5, vol=0.26)
            noise_hit(t + 0.1, 1.1, 0.34, decay=0.55, seed=s,
                      lowpass=2600, attack=0.18); s += 1
        elif kind == 'save':
            saw(t, 0.5, 118, 96, 0.30)
            saw(t, 0.5, 112, 92, 0.30)
            noise_hit(t, 0.15, 0.2, decay=0.05, seed=s); s += 1
        elif kind == 'whistle':
            whistle(t)
            whistle(t + 0.55)
        elif kind == 'fanfare':
            arp = ['C5', 'E5', 'G5', 'C6', 'E6', 'G6', 'C7']
            for j, note in enumerate(arp):
                add_note(t + j * 0.09, 0.30, freq(note), duty=0.5, vol=0.24)
            tchord = t + len(arp) * 0.09 + 0.12
            for note, v in [('C6', 0.14), ('E6', 0.12), ('G6', 0.12),
                            ('C7', 0.1)]:
                add_note(tchord, 1.6, freq(note), duty=0.5, vol=v, echo=0.3)
            kick(tchord - 0.1, vol=0.6)
            noise_hit(tchord - 0.35, 0.4, 0.14, decay=0.2, seed=s); s += 1
        elif kind == 'pop':
            pop(t, s, 50 + (i * 13) % 45); s += 1


def main():
    global buf
    build_music()
    build_sfx()
    fade = int(0.5 * SR)
    buf[-fade:] *= np.linspace(1.0, 0.0, fade)
    peak = np.max(np.abs(buf))
    if peak > 0.95:
        buf *= 0.95 / peak
    data = (buf * 32767).astype(np.int16).tobytes()
    with wave.open('music.wav', 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data)
    print('music.wav', DUR, 's, peak', round(float(peak), 3))


if __name__ == '__main__':
    main()
