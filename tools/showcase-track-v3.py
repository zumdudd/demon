#!/usr/bin/env python3
# ДЕМОН · concept + direction: ШУМ (shum) · built with Claude (Anthropic)
# music: ШУМ × Claude, synthesized from scratch, CC BY 4.0
"""showcase-track v3: the showcase song, synthesized in numpy. No samples, no outside audio.
v3: ДЕЛИКАТЕС rebuilt (a frantic drummer, parallel distortion, chops, metal hits, a short metal room, a bass riff);
    ПРИВАЛ rebuilt (moving, bleeding pads, rain); ГНИЛЬ rebuilt as a tape loop that wears down on each pass.
v2: the kick rebuilt (sub / body / click layers, exponential pitch dive onto A1 = 55 Hz, styles per section) + sidechain ducking of the bass.
v1: first version (its kick sat at 73-164 Hz: MIDI numbers one octave too high).

Eight sections, D minor, one original motif that travels through them. Each section is a whole number of bars
and is written twice: as a seamless loop (its tail wrapped onto its start) and as part of the chained track.

    python3 tools/showcase-track-v3.py OUTDIR

OUTDIR gets: track.wav, loops/NN-name.wav, map.json (sections, every kick / snare / hat, vocal spans, scene cues).
"""
import os, sys, json, math
import numpy as np
from scipy import signal

SR = 44100
rng = np.random.default_rng(1919)
A4 = 440.0
def hz(m): return A4 * 2 ** ((m - 69) / 12)
def secs(n): return np.arange(n) / SR
def N(s): return int(round(s * SR))

# ------------------------------------------------------------------ filters and helpers
def sos(kind, f, order=2, q=None):
    f = np.clip(np.atleast_1d(f), 20, SR / 2 - 200)
    return signal.butter(order, f if len(f) > 1 else f[0], btype=kind, fs=SR, output='sos')
def lp(x, f, o=2): return signal.sosfilt(sos('lowpass', f, o), x, axis=0)
def hp(x, f, o=2): return signal.sosfilt(sos('highpass', f, o), x, axis=0)
def bp(x, lo, hi, o=2): return signal.sosfilt(sos('bandpass', [lo, hi], o), x, axis=0)
def env_exp(n, tau): return np.exp(-secs(n) / tau)
def adsr(n, a, d, s, r):
    e = np.ones(n) * s; na, nd, nr = N(a), N(d), N(r)
    na = min(na, n); e[:na] = np.linspace(0, 1, na, endpoint=False) if na else e[:na]
    nd = min(nd, n - na); e[na:na + nd] = np.linspace(1, s, nd, endpoint=False) if nd else e[na:na + nd]
    if nr: e[-nr:] *= np.linspace(1, 0, min(nr, n))[-min(nr, n):]
    return e
def saw(f, n, ph=0.0):
    """band-limited saw by additive partials (fine for the short notes here)."""
    t = secs(n); out = np.zeros(n); f = float(f); k = 1
    while k * f < SR / 2.2 and k <= 60:
        out += ((-1) ** (k + 1)) * np.sin(2 * np.pi * k * f * t + ph * k) / k; k += 1
    return out * (2 / np.pi)
def square(f, n):
    t = secs(n); out = np.zeros(n); k = 1
    while k * f < SR / 2.2 and k <= 59: out += np.sin(2 * np.pi * k * f * t) / k; k += 2
    return out * (4 / np.pi)
def supersaw(f, n, voices=7, spread=0.18):
    out = np.zeros((n, 2))
    for i in range(voices):
        d = (i - (voices - 1) / 2) / ((voices - 1) / 2); fr = f * 2 ** (d * spread / 12)
        s = saw(fr, n, rng.uniform(0, 2 * np.pi)); pan = 0.5 + 0.45 * d
        out[:, 0] += s * (1 - pan); out[:, 1] += s * pan
    return out / voices * 1.6
def fm_bell(f, n, ratio=3.5, idx=4.0, tau=0.9):
    t = secs(n); e = env_exp(n, tau)
    return np.sin(2 * np.pi * f * t + idx * e * np.sin(2 * np.pi * f * ratio * t)) * e
def st(x, pan=0.5):
    return np.stack([x * math.cos(pan * math.pi / 2), x * math.sin(pan * math.pi / 2)], 1) * 1.414
def crush(x, bits=6, hold=4):
    y = np.round(x * 2 ** (bits - 1)) / 2 ** (bits - 1)
    if hold > 1: y = np.repeat(y[::hold], hold, axis=0)[:len(x)]
    return y
def add(buf, x, at):
    i = N(at)
    if i >= len(buf): return
    m = min(len(x), len(buf) - i)
    if x.ndim == 1: x = st(x)
    buf[i:i + m] += x[:m]

_IR = {}
def reverb(x, size=2.2, wet=0.25, damp=6000):
    key = (size, damp)
    if key not in _IR:
        n = N(size); e = np.exp(-secs(n) * 6.9 / size)
        ir = np.stack([lp(rng.standard_normal(n), damp) * e, lp(rng.standard_normal(n), damp) * e], 1)
        ir /= np.sqrt((ir ** 2).sum(0)); _IR[key] = ir
    ir = _IR[key]
    y = np.stack([signal.fftconvolve(x[:, c], ir[:, c]) for c in range(2)], 1)
    out = np.zeros_like(y); out[:len(x)] = x * (1 - wet); out += y * wet
    return out

# ------------------------------------------------------------------ drums
KICK_F0 = 55.0                                                             # A1, the fifth of D minor (kick tuned to the key)
KICK_STYLE = dict(                                                         # pitch dive (octaves, tau), amp (hold, decay), click, body drive
    soft=dict(oct=3.5, ptau=0.030, hold=0.010, tau=0.18, click=0.25, drive=1.6),    # hyperpop, the build
    hard=dict(oct=4.0, ptau=0.022, hold=0.015, tau=0.24, click=0.55, drive=5.0),    # industrial
    drop=dict(oct=4.5, ptau=0.030, hold=0.030, tau=0.42, click=0.45, drive=2.6),    # dubstep
    four=dict(oct=3.8, ptau=0.020, hold=0.008, tau=0.14, click=0.35, drive=2.0))    # the nightcore four-on-floor
def kick(style='soft', f0=KICK_F0):
    """three layers, the way kick synthesis guides build it: a clean sine sub, a saturated body for harmonics,
    a noise + tight-pitch click for the transient. The pitch dives exponentially (in octaves) onto f0."""
    k = KICK_STYLE[style]; n = N(0.9); t = secs(n)
    f = f0 * 2 ** (k['oct'] * np.exp(-t / k['ptau']))
    ph = 2 * np.pi * np.cumsum(f) / SR
    amp = np.where(t < k['hold'], 1.0, np.exp(-(t - k['hold']) / k['tau']))
    osc = np.sin(ph) * amp
    sub = lp(osc, 110, 4)                                                  # stays clean: distortion never touches the sub
    body = np.tanh(hp(osc, 90) * k['drive']) / np.tanh(k['drive']) * 0.55
    ct = 2 ** (6 * np.exp(-t / 0.004))
    click = (bp(rng.standard_normal(n), 2000, 9000) * np.exp(-t / 0.0035) + 0.6 * np.sin(2 * np.pi * np.cumsum(f0 * ct) / SR) * np.exp(-t / 0.006)) * k['click']
    x = sub + body + click
    return x / (np.abs(x).max() + 1e-9)
def duck(n, times, depth=0.7, attack=0.004, release=0.18):
    """sidechain: the bass dips under each kick so they don't fight in the low end."""
    g = np.ones(n); t = secs(N(release * 4))
    shape = 1 - depth * np.exp(-t / release) * np.minimum(1, t / attack)
    for at in times:
        i = N(at); m = min(len(shape), n - i)
        if m > 0: g[i:i + m] = np.minimum(g[i:i + m], shape[:m])
    return g
def snare(noise=0.7, tone=190, tau=0.16, dirt=0.0):
    n = N(0.45); t = secs(n)
    x = noise * bp(rng.standard_normal(n), 1200, 9000) * env_exp(n, tau) + (1 - noise) * np.sin(2 * np.pi * tone * t) * env_exp(n, 0.06)
    if dirt: x = np.tanh(crush(x, 5, 3) * (1 + 5 * dirt)) * 0.8 * env_exp(n, tau * 1.3)   # gate after the drive: the tail stays short
    return x
def hat(tau=0.035, open_=False):
    n = N(0.4 if open_ else 0.12)
    return hp(rng.standard_normal(n), 7500) * env_exp(n, 0.18 if open_ else tau) * 0.5
def clap():
    n = N(0.35); x = np.zeros(n); b = bp(rng.standard_normal(n), 900, 5000)
    for k, d in enumerate((0, 0.011, 0.023, 0.034)): i = N(d); x[i:] += b[:n - i] * env_exp(n - i, 0.012 if k < 3 else 0.14)
    return x * 0.7
def timp(m=38):
    n = N(1.6); t = secs(n); f = hz(m) * (1 + 0.08 * np.exp(-t / 0.08))
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR)) * env_exp(n, 0.55) \
        + 0.3 * lp(rng.standard_normal(n), 800) * env_exp(n, 0.05)


def smooth_noise(n, rate, seed=None):
    """random, smooth movement (not a plain LFO): noise low-passed at `rate` Hz, scaled to about ±1."""
    r = np.random.default_rng(seed) if seed is not None else rng
    x = lp(r.standard_normal(n + N(1.0)), max(0.05, rate), 2)[N(1.0):]
    return x / (np.abs(x).max() + 1e-9)
def moving_lp(x, cut, block=512):
    """low-pass whose cutoff follows the array `cut` (per sample), filter state carried across blocks."""
    out = np.zeros_like(x); zi = None
    for i in range(0, len(x), block):
        so = sos('lowpass', float(cut[i]), 2)
        if zi is None: zi = np.zeros((so.shape[0], 2) + x.shape[1:])
        out[i:i + block], zi = signal.sosfilt(so, x[i:i + block], axis=0, zi=zi)
    return out
def wow_flutter(x, wow_ms, flut_ms, seed=7):
    """tape speed wobble: a delay line moved by slow random wow + fast random flutter (per channel slightly different)."""
    n = len(x); out = np.zeros_like(x); idx = np.arange(n, dtype=float)
    for c in range(x.shape[1]):
        d = (wow_ms * (1 + smooth_noise(n, 0.6, seed + c)) + flut_ms * (1 + smooth_noise(n, 7.0, seed + 10 + c))) * SR / 1000
        out[:, c] = np.interp(idx - d, idx, x[:, c], left=0)
    return out
def tom(m, tau=0.16):
    n = N(0.6); t = secs(n); f = hz(m) * 2 ** (1.2 * np.exp(-t / 0.03))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / tau) + 0.25 * bp(rng.standard_normal(n), 300, 3000) * np.exp(-t / 0.02)
    return np.tanh(x * 2.5) * 0.7
def metal(f=410.0, tau=0.12):
    """an inharmonic FM clank: struck sheet metal, no sample."""
    n = N(0.5); t = secs(n); e = np.exp(-t / tau)
    x = np.sin(2 * np.pi * f * t + 5 * e * np.sin(2 * np.pi * f * 1.41 * t) + 2 * e * np.sin(2 * np.pi * f * 2.76 * t)) * e
    return hp(x, 300) * 0.8

# ------------------------------------------------------------------ section frame
class Sec:
    def __init__(self, name, bpm, bars, kind, level, scenes, title):
        self.name = name; self.bpm = bpm; self.bars = bars; self.kind = kind; self.level = level; self.scenes = scenes; self.title = title
        self.beat = 60 / bpm; self.dur = bars * 4 * self.beat; self.tail = 3.0
        self.buf = np.zeros((N(self.dur + self.tail), 2))
        self.hits = dict(kick=[], snare=[], hat=[]); self.vocal = []; self.parts = []
        self.bass = np.zeros_like(self.buf)
    def b(self, bar, beat=0.0): return (bar * 4 + beat) * self.beat           # time of bar / beat (beats from 0)
    def hit(self, kind, at, x, gain=1.0, pan=0.5):
        add(self.buf, st(x * gain, pan), at)
        if kind in self.hits: self.hits[kind].append(round(at, 4))
    def note(self, x, at, gain=1.0): add(self.buf, x * gain, at)
    def bassnote(self, x, at, gain=1.0): add(self.bass, x * gain, at)
    def mixbass(self, depth=0.7, release=0.18):
        self.buf += self.bass * duck(len(self.bass), self.hits['kick'], depth, release=release)[:, None]; self.bass[:] = 0

# the motif (original): two bars of 8ths in D minor, None = rest
MOTIF = [81, None, 77, 74, 76, 77, None, 81, 79, None, 77, 76, 74, None, None, None,
         84, None, 81, 77, 79, 81, None, 84, 86, None, 84, 81, 79, 77, 76, None]
PROG = [(50, 53, 57), (46, 50, 53), (53, 57, 60), (48, 52, 55)]          # Dm  Bb  F  C (roots in octave 3)

# ------------------------------------------------------------------ 1 · ПРИВАЛ: ДЕМОН alone, rain in the visor
def rain_bed(n, amount=1.0):
    """rain: soft filtered noise that breathes, plus single drops, some of them pitched like water on glass."""
    bed = lp(hp(rng.standard_normal((n, 2)), 900), 3800) * 0.018 * amount
    bed *= (0.75 + 0.25 * smooth_noise(n, 0.25))[:, None]
    drops = np.zeros((n, 2)); dur = n / SR
    for _ in range(int(dur * 7 * amount)):
        at = rng.uniform(0, dur); L = N(0.08)
        if rng.random() < 0.35:                                               # a pitched drop
            f = rng.uniform(1800, 3600); d = np.sin(2 * np.pi * f * (1 - 0.15 * secs(L) / 0.08) * secs(L)) * env_exp(L, 0.012) * 0.05
        else: d = bp(rng.standard_normal(L), 2200, 7000) * env_exp(L, 0.005) * rng.uniform(0.03, 0.12)
        add(drops, st(d, rng.uniform(0.1, 0.9)), at)
    return bed + drops

def pad_chord(ch, L, cut0=700, seed=0):
    """a pad the way pad guides build it: detuned triangle-ish + square-ish layers, dark low-pass with slow movement,
    slow pitch drift per voice (chorus), soft attack, long release so chords bleed, high-passed to keep the low end clear."""
    t = secs(L); out = np.zeros((L, 2))
    for j, m in enumerate(ch):
        for v, (det, pan) in enumerate(((-0.07, 0.25), (0.06, 0.75), (0.0, 0.5))):
            drift = 1 + 0.0025 * smooth_noise(L, 0.3, seed * 31 + j * 7 + v)
            ph = 2 * np.pi * np.cumsum(hz(m) * 2 ** (det / 12) * drift) / SR
            tri = (2 / np.pi) * np.arcsin(np.sin(ph)); sq = np.tanh(3 * np.sin(ph + 0.3)) * 0.5
            out += st((tri + sq * 0.6) / 3, pan)
    cut = cut0 * (1 + 0.5 * (0.5 + 0.5 * smooth_noise(L, 0.15, seed + 99)))
    out = hp(moving_lp(out, cut), 140)
    return out * adsr(L, 1.6, 1.0, 0.85, 3.5)[:, None] * 0.12

def s_calm():
    s = Sec('calm', 80, 4, 'calm', 0.22, ['hero-demon'], 'ПРИВАЛ · calm')
    n = len(s.buf); s.buf += rain_bed(n)
    for bar in range(4):
        ch = PROG[bar % 4]; L = N(s.b(1) + 4.0)
        s.note(pad_chord(ch, L, 700, bar), s.b(bar))
        sub = np.sin(2 * np.pi * hz(ch[0] - 12) * secs(L)) * adsr(L, 0.8, 0.5, 0.6, 2.5) * 0.12
        s.note(st(sub), s.b(bar))
    echo = np.zeros_like(s.buf)
    for i, m in enumerate(MOTIF[:16:2]):
        if m is None: continue
        at = s.b(0, i * 2) + 0.02; bell = st(fm_bell(hz(m - 12), N(2.4), 3.5, 2.0, 0.9) * 0.14, 0.35 + 0.3 * (i % 2))
        s.note(bell, at)
        for k, g in ((1, 0.35), (2, 0.15)): add(echo, bell * g, at + k * s.beat * 0.75)   # dotted-8th echo, filtered
    s.buf += lp(echo, 2500)
    s.buf = reverb(s.buf, 3.4, 0.38, 5000)[:len(s.buf)]
    return s

def s_rot():
    """ГНИЛЬ: the opening's motif as a tape loop that wears down on every pass (the Basinski idea): each pass more
    wow and flutter, fewer highs, more dropouts and hiss, a little more saturation, then it is gone."""
    s = Sec('outro', 80, 4, 'calm', 0.18, ['gnil', 'credits'], 'ГНИЛЬ · rot')
    L = N(s.b(1)); loop = np.zeros((L + N(4.0), 2))
    add(loop, pad_chord(PROG[0], L + N(3.0), 650, 7), 0.0)
    for i, m in enumerate(MOTIF[16::4]):
        if m is None: continue
        add(loop, st(fm_bell(hz(m - 12), N(2.0), 3.5, 2.0, 0.8) * 0.13, 0.4 + 0.2 * (i % 2)), i * s.beat)
    lb = loop[:L].copy(); lb[:N(4.0) if N(4.0) < L else L] += loop[L:L + min(L, N(4.0))]   # the loop's own tail wraps in
    for p in range(4):                                                        # four passes, each one older
        k = p / 3
        x = wow_flutter(lb, 0.6 + 6 * k, 0.15 + 1.2 * k, seed=11 + p)
        x = lp(np.tanh(x * (1 + 2 * k)) / np.tanh(1 + 2 * k), 9000 - 6000 * k)
        g = np.ones(L)
        for _ in range(int(1 + 5 * k)):                                       # dropouts: the oxide is gone here
            c = rng.integers(0, L); w = N(rng.uniform(0.05, 0.3 + 0.4 * k))
            dip = 1 - (0.6 + 0.4 * k) * np.hanning(w); a_, b_ = c, min(L, c + w); g[a_:b_] = np.minimum(g[a_:b_], dip[:b_ - a_])
        x = x * g[:, None] + lp(hp(rng.standard_normal((L, 2)), 2000), 6000) * (0.0012 + 0.0035 * k)
        s.note(x * (1 - 0.25 * k), s.b(p))
    s.buf += rain_bed(len(s.buf), 0.5) * np.linspace(1, 0, len(s.buf))[:, None]
    s.buf = reverb(s.buf, 3.4, 0.35, 4000)[:len(s.buf)]
    s.buf *= np.linspace(1, 0, len(s.buf))[:, None] ** 1.2
    return s

# ------------------------------------------------------------------ 2 · ЧУЕТ / ЗАРАЖЕНИЕ: the build, then the gap
def s_build():
    s = Sec('build', 140, 4, 'build', 0.6, ['chuet', 'zarazhenie', 'smena'], 'ЧУЕТ · the build')
    gap_at = s.b(3, 3)                                                        # the last beat is the gap (ДУША ВОН)
    t = 0.0; step = s.beat
    while t < gap_at:                                                         # snare roll 4ths → 8ths → 16ths → 32nds
        k = t / gap_at; step = s.beat / (1 if k < 0.25 else 2 if k < 0.5 else 4 if k < 0.8 else 8)
        s.hit('snare', t, snare(0.75, 200, 0.09), 0.25 + 0.55 * k, 0.5); t += step
    for bt in range(0, 15, 4): s.hit('kick', s.b(0, bt), kick('soft'), 0.7)
    n = N(gap_at); tt = secs(n)
    riser = bp(rng.standard_normal(n), 400, 5000) * (tt / gap_at) ** 3 * 0.12
    sweep = np.sin(2 * np.pi * np.cumsum(hz(38) * 2 ** (tt / gap_at * 3)) / SR) * (tt / gap_at) * 0.25
    s.note(st(riser + sweep), 0.0)
    L = N(gap_at); pad = sum(supersaw(hz(m), L, 5) for m in (50, 53, 57)) / 3
    cut = np.linspace(300, 6000, L); out = np.zeros_like(pad)
    for i in range(0, L, 2048): out[i:i + 2048] = lp(pad[i:i + 2048], cut[i])
    s.note(out * np.linspace(0.05, 0.3, L)[:, None], 0.0)
    s.buf[N(gap_at):] *= 0.0                                                  # the gap: silence before the slam
    s.vocal = []
    s.gap = gap_at
    return s

# ------------------------------------------------------------------ 3 · ДЕЛИКАТЕС: industrial noise drums
def s_deli():
    """Death Grips grammar from the research: a frantic live-feeling drummer (never one loop), chopped bits used as
    instruments, parallel distortion (punch kept, grit added), a short metal room instead of a big reverb,
    drums pushed a few ms off the grid, a dark monotone bass riff that ducks under the kick, and air left in the mix."""
    s = Sec('deli', 140, 8, 'slam', 0.95, ['delikates', 'krik', 'detonatsiya', 'detonatsiya'], 'ДЕЛИКАТЕС · industrial')
    dr = np.zeros_like(s.buf)
    def d(kind, at, x, g=1.0, pan=0.5):
        at = max(0.0, at + rng.normal(0, 0.006))                              # a human push against the grid
        add(dr, st(x * g * rng.uniform(0.82, 1.0), pan), at)
        if kind in s.hits: s.hits[kind].append(round(at, 4))
    pats = [[0, 0.75, 1.5, 2.5, 3.25], [0, 1.25, 1.75, 2.5], [0, 0.5, 1.5, 2.0, 2.75, 3.5], [0, 0.75, 2.25, 2.5, 3.0]]
    for bar in range(8):
        for bt in pats[(bar * 3 + bar // 4) % 4]: d('kick', s.b(bar, bt), kick('hard'), 1.0)
        for bt in (1, 3): d('snare', s.b(bar, bt), snare(0.85, 175, 0.11, dirt=0.6), 0.95)
        for q in range(16):                                                    # ghost notes, like a drummer's left hand
            if q % 4 and rng.random() < 0.22: d('ghost', s.b(bar, q / 4), snare(0.95, 0, 0.04, dirt=0.3), 0.25)
        for e in range(8):
            if rng.random() < 0.85: d('hat', s.b(bar, e / 2), hat(0.018, open_=(e == 7 and bar % 2 == 1)), 0.4 if e % 2 else 0.22, 0.65)
        if bar % 2 == 1:                                                       # metal on the off-beats
            for bt in (0.5, 2.5): d('metal', s.b(bar, bt), metal(rng.choice([380.0, 410.0, 520.0])), 0.45, rng.uniform(0.2, 0.8))
        if bar in (3, 7):                                                      # tom fill into the next phrase
            for k, m in enumerate((52, 50, 47, 45, 43, 40)): d('tom', s.b(bar, 3 + k / 6), tom(m), 0.8, 0.3 + 0.08 * k)
    # chops: a 16th of the drums stuttered at the end of bars 2 and 6 (cut-up as an instrument)
    for bar in (1, 5):
        src = dr[N(s.b(bar, 2)):N(s.b(bar, 2)) + N(s.beat / 4)].copy()
        for k in range(8):
            at = s.b(bar, 3 + k / 8); seg = src[:N(s.beat / 8)] * (1 - k / 10)
            i = N(at); dr[i:i + len(seg)] = seg
    # parallel distortion: the dry kit keeps the punch, a crushed copy (high-passed, so the low end stays clean) adds grit
    grit = hp(np.tanh(crush(dr, 6, 3) * 5) * 0.3, 180)
    room = reverb(grit, 0.25, 0.2, 6000)[:len(dr)]                             # a short metal room, not a hall
    s.buf += dr + room * 0.4
    # bass riff: D D F D A♭ G F D, crushed, ducking under the kick
    riff = [26, 26, 29, 26, 32, 31, 29, 26]
    for bar in range(8):
        for e, m in enumerate(riff):
            L = N(s.beat / 2 * 0.92); f = hz(m)
            v = np.tanh(saw(f, L) * 3.5) * adsr(L, 0.003, 0.08, 0.75, 0.03)
            s.bassnote(st(lp(crush(v, 6, 2), 1800) * 0.32), s.b(bar, e / 2))
    # shouts with no words: formant noise, the voice used as a drum; bar 7 gets chopped
    for bar in range(8):
        for bt in ((1.5, 3) if bar % 2 == 0 else (1.5, 2.75, 3.5)):
            Lv = N(0.18); src = rng.standard_normal(Lv) + 0.6 * saw(hz(50 + rng.integers(-2, 3)), Lv)
            v = sum(bp(src, fc * 0.85, fc * 1.15) for fc in (700, 1150, 2600)) * env_exp(Lv, 0.08)
            v = np.tanh(v * 3) * 0.2
            if bar == 6: v = np.concatenate([v[:N(0.04)]] * 4 + [v])[:N(0.3)]
            s.note(st(v, 0.45), s.b(bar, bt)); s.vocal.append([round(s.b(bar, bt), 3), round(s.b(bar, bt) + 0.18, 3)])
    s.mixbass(0.75, 0.16)
    s.buf = lp(np.tanh(s.buf * 1.05), 13000)                                    # a soft bus clip only: room for air
    return s

# ------------------------------------------------------------------ 4 · ПРИМАНКА: cute hyperpop, dark core
def s_lure():
    s = Sec('lure', 160, 8, 'loud', 0.62, ['primanka', 'kukla', 'dva-litsa'], 'ПРИМАНКА · hyperpop')
    for bar in range(8):
        dark = bar in (3, 7)                                                  # two bars where the mask slips
        for bt in (0, 2.5) if not dark else (0, 1, 2, 2.5, 3): s.hit('kick', s.b(bar, bt), kick('soft' if not dark else 'hard'), 0.8)
        for bt in (1, 3): s.hit('snare', s.b(bar, bt), clap(), 0.7)
        for e in range(16 if bar % 2 else 8): s.hit('hat', s.b(bar, e / (4 if bar % 2 else 2)), hat(0.015), 0.3, 0.3 + 0.4 * (e % 2))
        root = PROG[bar % 4][0] - 12
        L = N(s.b(1)); f0 = hz(root - 12)
        glide = f0 * (1 + 0.5 * np.exp(-secs(L) / 0.03))
        b808 = np.tanh(np.sin(2 * np.pi * np.cumsum(glide) / SR) * (1.5 if not dark else 4)) * adsr(L, 0.002, 0.2, 0.7, 0.1)
        s.bassnote(st(b808 * 0.45), s.b(bar))
        for k in range(8):                                                    # bell arp
            m = PROG[bar % 4][k % 3] + 24 + (12 if k >= 6 else 0)
            s.note(st(fm_bell(hz(m), N(0.5), 2.0, 1.5, 0.18) * 0.09, 0.2 + 0.6 * (k % 2)), s.b(bar, k / 2))
    for rep in range(4):                                                      # the motif, square + saw, bright
        for i, m in enumerate(MOTIF):
            if m is None: continue
            at = s.b(rep * 2, i / 2); L = N(s.beat / 2 * 0.95)
            v = (square(hz(m), L) * 0.5 + saw(hz(m + 12), L) * 0.25) * adsr(L, 0.004, 0.05, 0.7, 0.03)
            if rep in (1, 3) and i >= 24: v = crush(v, 4, 8)                  # the dark core shows through
            s.note(st(lp(v, 7000) * 0.17, 0.5), at); s.vocal.append([round(at, 3), round(at + s.beat / 2, 3)])
    s.mixbass(0.6, 0.15)
    s.buf = reverb(s.buf, 1.4, 0.18)[:len(s.buf)]
    return s

# ------------------------------------------------------------------ 5 · ПОДДЕЛКА: the same section, sped up (a forgery)
def s_nightcore(lure, r=1.30):
    s = Sec('nightcore', lure.bpm * r, 8, 'loud', 0.8, ['poddelka', 'konfetti'], 'ПОДДЕЛКА · nightcore ×1.30')
    src = loop_of(lure)                                                       # the seamless loop, so the forgery loops too
    idx = np.arange(0, len(src), r)                                       # a real speed-up: resampled, pitch goes up with it
    sped = np.stack([np.interp(idx, np.arange(len(src) + 1), np.append(src[:, c], src[0, c])) for c in range(2)], 1)
    s.buf[:len(sped)] += sped * 0.85
    for bar in range(8):                                                      # the four-on-floor every nightcore edit adds
        for bt in range(4): s.hit('kick', s.b(bar, bt), kick('four'), 0.6)
        for bt in (1, 3): s.hits['snare'].append(round(s.b(bar, bt), 4))
        for e in range(8): s.hits['hat'].append(round(s.b(bar, e / 2 + 0.25), 4)); add(s.buf, st(hat(0.012) * 0.25, 0.7), s.b(bar, e / 2 + 0.25))
    s.vocal = [[round(a / r, 3), round(b / r, 3)] for a, b in lure.vocal]
    s.r = r
    return s

# ------------------------------------------------------------------ 6 · ПЕРЕМОТКА: rewind, then the dubstep drop
def s_drop(prev):
    s = Sec('drop', 140, 8, 'slam', 1.0, ['peremotka', 'pitch', 'past'], 'ПЕРЕМОТКА · dubstep')
    tail = prev.buf[max(0, N(prev.dur) - N(1.2)):N(prev.dur)][::-1]           # the tape runs backwards, slowing
    k = np.linspace(1, 0.25, len(tail)); pos = np.cumsum(k); pos = pos[pos < len(tail) - 1]
    rew = np.stack([np.interp(pos, np.arange(len(tail)), tail[:, c]) for c in range(2)], 1) * np.linspace(1, 0, len(pos))[:, None]
    rew_len = min(len(rew), N(s.b(1)))
    s.buf[:rew_len] += rew[:rew_len] * 0.7
    rates = [2, 2, 4, 4, 3, 3, 8, 1]                                          # wobbles per beat, per bar
    for bar in range(1, 8):
        s.hit('kick', s.b(bar, 0), kick('drop'), 1.0)
        if bar % 2 == 0: s.hit('kick', s.b(bar, 2.75), kick('drop'), 0.8)
        s.hit('snare', s.b(bar, 2), snare(0.85, 180, 0.25, dirt=0.4), 1.0)
        for e in range(8): s.hit('hat', s.b(bar, e / 2), hat(0.02), 0.25, 0.6)
        L = N(s.b(1)); f = hz(26 + (3 if bar in (3, 7) else 0)); tt = secs(L)
        src = saw(f, L) + saw(f * 1.005, L) + 0.6 * square(f / 2, L)
        lfo = 0.5 - 0.5 * np.cos(2 * np.pi * tt * rates[bar] / s.beat)
        cut = 120 + lfo * 2600; out = np.zeros(L)
        zi = None; B = 256
        for i in range(0, L, B):
            so = sos('lowpass', cut[i], 2)
            if zi is None: zi = signal.sosfilt_zi(so) * 0
            out[i:i + B], zi = signal.sosfilt(so, src[i:i + B], zi=zi)
        wob = np.tanh(out * 2.5) * adsr(L, 0.003, 0.05, 0.9, 0.02)
        sub = np.sin(2 * np.pi * f * tt) * adsr(L, 0.003, 0.05, 0.9, 0.02)
        s.bassnote(st(wob * 0.32 + sub * 0.3), s.b(bar))
    s.mixbass(0.8, 0.2)
    s.buf = lp(np.tanh(s.buf * 1.2) * 0.92, 10000)
    return s

# ------------------------------------------------------------------ 7 · КАДР: epic orchestral, ДЕМОН comes back
def s_epic():
    s = Sec('epic', 90, 4, 'loud', 0.95, ['kadr', 'ogon'], 'КАДР · epic')
    prog = [(50, 53, 57), (46, 50, 53), (48, 52, 55), (50, 53, 57)]           # Dm Bb C Dm
    for bar, ch in enumerate(prog):
        L = N(s.b(1) + 1.5)
        strings = sum(supersaw(hz(m), L, 7, 0.1) + supersaw(hz(m + 12), L, 5, 0.1) * 0.5 for m in ch) / 4
        vib = 1 + 0.003 * np.sin(2 * np.pi * 5.5 * secs(L))
        strings = lp(strings, 3500) * adsr(L, 0.35, 0.3, 0.85, 1.2)[:, None] * 0.28
        s.note(strings, s.b(bar))
        Lv = N(s.b(1) + 1.0); src = sum(saw(hz(m), Lv) for m in ch) / 3          # choir "ah"
        ch_ = sum(bp(src, fc * 0.9, fc * 1.1) * g for fc, g in ((800, 1.0), (1150, 0.6), (2900, 0.25))) * adsr(Lv, 0.5, 0.3, 0.8, 1.0)
        s.note(st(ch_ * 0.35, 0.5), s.b(bar))
        s.hit('kick', s.b(bar, 0), timp(38 if bar != 2 else 36), 0.9)
        for bt in (1.5, 2, 3, 3.5): s.hit('snare', s.b(bar, bt), timp(45) * 0.5, 0.5)
        for bt in (0, 2.5):                                                     # brass stabs
            Lb = N(0.45); br = sum(saw(hz(m + 12), Lb) for m in ch) / 3
            cut = 400 + 3500 * env_exp(Lb, 0.12); out = np.zeros(Lb)
            for i in range(0, Lb, 512): out[i:i + 512] = lp(br[i:i + 512], cut[i])
            s.note(st(out * adsr(Lb, 0.02, 0.1, 0.7, 0.15) * 0.4), s.b(bar, bt))
    for i, m in enumerate(MOTIF[16:]):                                         # the motif, slow and wide (bars 2-3: the КАДР)
        if m is None: continue
        at = s.b(2, i / 4); L = N(s.beat * 0.6)
        v = (saw(hz(m), L) * 0.6 + saw(hz(m) * 1.003, L) * 0.4) * adsr(L, 0.03, 0.1, 0.8, 0.2)
        s.note(st(lp(v, 5000) * 0.2), at); s.vocal.append([round(at, 3), round(at + s.beat / 4, 3)])
    s.buf = reverb(s.buf, 3.5, 0.32)[:len(s.buf)]
    s.kadr = s.b(2)
    return s

# ------------------------------------------------------------------ assemble
def master(x, target_peak=0.89, norm=None):
    """gentle compression + soft clip. norm=None: scale to target_peak and return the factor too; else use that factor
    (the loops take the track's factor, so a loop plays as loud as its part of the track)."""
    x = hp(x, 28)
    env = np.sqrt(np.maximum(lp(x.mean(1) ** 2, 8), 0) + 1e-9)               # slow RMS: gentle compression
    gain = np.minimum(1.0, (0.22 / env) ** 0.35)
    x = x * gain[:, None]
    x = np.tanh(x * 1.2) / np.tanh(1.2)
    if norm is None:
        f = target_peak / (np.abs(x).max() + 1e-9); return x * f, f
    return np.clip(x * norm, -0.99, 0.99)

def seam(x, ms=2.0):
    """a 2 ms fade at both ends of a loop: no click where it wraps."""
    k = N(ms / 1000); w = np.linspace(0, 1, k)[:, None]; x = x.copy(); x[:k] *= w; x[-k:] *= w[::-1]; return x

def loop_of(s):
    body = s.buf[:N(s.dur)].copy(); tail = s.buf[N(s.dur):]
    m = min(len(tail), len(body)); body[:m] += tail[:m]                     # the tail wraps onto the start: seamless loop
    return body

def wav(path, x):
    from scipy.io import wavfile
    wavfile.write(path, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))

def build(outdir):
    os.makedirs(f'{outdir}/loops', exist_ok=True)
    s1 = s_calm(); s2 = s_build(); s3 = s_deli(); s4 = s_lure(); s5 = s_nightcore(s4); s6 = s_drop(s5); s7 = s_epic()
    s8 = s_rot()
    secs_ = [s1, s2, s3, s4, s5, s6, s7, s8]
    total = sum(s.dur for s in secs_) + 3.0
    out = np.zeros((N(total), 2)); t = 0.0
    m = dict(title='ДЕМОН & ПОДМЕНЫШ · showcase', credit='music: ШУМ × Claude, synthesized from scratch, CC BY 4.0',
             sr=SR, length=None, sections=[], segments=[], kick=[], snare=[], hat=[], vocal=[], cues=[])
    for i, s in enumerate(secs_):
        add(out, s.buf, t)
        seg = dict(n=i + 1, name=s.name, title=s.title, start=round(t, 3), end=round(t + s.dur, 3), bpm=round(s.bpm, 3),
                   bars=s.bars, kind=s.kind, level=s.level, scenes=s.scenes, loop=f'loops/{i + 1:02d}-{s.name}.wav')
        if hasattr(s, 'r'): seg['forgery_r'] = s.r
        m['segments'].append(seg)
        m['sections'].append([round(t, 3), s.kind, s.level])
        if hasattr(s, 'gap'):
            m['sections'].append([round(t + s.gap, 3), 'gap', 0.08])
        if s.kind == 'slam' and i + 1 < len(secs_):
            m['sections'].append([round(t + min(s.dur, 2 * 4 * s.beat), 3), 'loud', s.level * 0.9])
        for k in ('kick', 'snare', 'hat'): m[k] += [round(t + x, 4) for x in s.hits[k]]
        m['vocal'] += [[round(t + a, 3), round(t + b, 3)] for a, b in s.vocal]
        for j, sc in enumerate(s.scenes): m['cues'].append(dict(t=round(t + s.dur * j / len(s.scenes), 3), scene=sc))
        if hasattr(s, 'kadr'): m['cues'].append(dict(t=round(t + s.kadr, 3), scene='kadr', note='the КАДР moment'))
        t += s.dur
    out = out[:N(t + 2.5)]
    out[-N(2.5):] *= np.linspace(1, 0, N(2.5))[:, None]
    full, f = master(out); wav(f'{outdir}/track.wav', full)
    for i, s in enumerate(secs_): wav(f'{outdir}/loops/{i + 1:02d}-{s.name}.wav', seam(master(loop_of(s), norm=f)))
    m['length'] = round(len(full) / SR, 3)
    for k in ('kick', 'snare', 'hat'): m[k] = sorted(m[k])
    json.dump(m, open(f'{outdir}/map.json', 'w'), ensure_ascii=False, indent=1)
    for sg in m['segments']: print(f"{sg['n']} {sg['name']:10s} {sg['start']:6.2f}-{sg['end']:6.2f}  {sg['bpm']:6.1f} bpm  {sg['title']}")
    print(f"total {m['length']:.1f} s · kicks {len(m['kick'])} · snares {len(m['snare'])} · hats {len(m['hat'])}")

if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else 'track-out')
