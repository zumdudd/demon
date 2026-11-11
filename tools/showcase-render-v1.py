#!/usr/bin/env python3
# ДЕМОН · concept + direction: ШУМ (shum) · built with Claude (Anthropic)
"""showcase-render v1: GIFs of ДЕМОН and ПОДМЕНЫШ, every frame from the real engine.

Runs the real window draw path (Demon.draw -> paint_frame) on a fake clock, with a scripted song
fed to the ear (kick / snare / hat / level per frame) instead of live cava. Scenes start the same way
the right-click menu starts them (▶ ДЕТОНАЦИЯ, ▶ ПРИМАНКА, ▶ ПОДДЕЛКА, ▶ ПАСТЬ, ▶ СМЕНА, ▶ КАДР ...).

    python3 tools/showcase-render-v1.py OUTDIR [scene ...]      # needs a display (Xvfb is fine)
    python3 tools/showcase-render-v1.py --list

A song map (JSON) can drive any scene later: {"bpm": 140, "sections": [[t0, kind, level], ...]}.
It runs inside a throwaway HOME that points at this repo, so it never reads or writes the live state.
"""
import os, sys, math, random, tempfile, json, shutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAKE = tempfile.mkdtemp(prefix='showcase-home-')
os.makedirs(f'{FAKE}/.local/lib', exist_ok=True); os.makedirs(f'{FAKE}/.local/bin', exist_ok=True)
os.symlink(f'{REPO}/lib/zarya', f'{FAKE}/.local/lib/zarya')
for b in os.listdir(f'{REPO}/bin'): os.symlink(f'{REPO}/bin/{b}', f'{FAKE}/.local/bin/{b}')
os.environ['HOME'] = FAKE; os.environ['XDG_CONFIG_HOME'] = f'{FAKE}/.config'; os.environ['XDG_CACHE_HOME'] = f'{FAKE}/.cache'
os.environ['XDG_DATA_HOME'] = f'{FAKE}/.local/share'

import time
class Clock:
    t = 1_800_000_000.0
CLOCK = Clock()
time.time = lambda: CLOCK.t                                  # the whole engine reads the fake clock
_mono0 = time.monotonic(); time.monotonic = lambda: CLOCK.t - 1_800_000_000.0 + _mono0

P = f'{FAKE}/.local/lib/zarya/desk'
g = {'__name__': 'showcase', '__file__': f'{FAKE}/.local/bin/zarya-daemon-desk'}
for f in sorted(x for x in os.listdir(P) if x.endswith('.py')):
    exec(compile(open(f'{P}/{f}', encoding='utf-8').read(), f'{P}/{f}', 'exec'), g)
LOGS = []
def _log(m):
    LOGS.append(f'{CLOCK.t:.2f} {m}')
    if 'error' in m and os.environ.get('SHOWCASE_LOG'):
        import traceback; traceback.print_exc()
    if os.environ.get('SHOWCASE_LOG'): print(f'   · {m}')
g['log'] = _log
cairo = g['cairo']; ZD = g['ZD']; ZH = g['ZH']; ZM = g['ZM']
try: ZH.set_logger(_log)
except Exception: pass
from PIL import Image

FPS = 25; DT = 1 / FPS
BG = (0x16, 0x12, 0x2E)                                       # night violet, the course's dark --bg
U = 8                                                         # pixels per cell in the GIF

# ------------------------------------------------------------------ the scripted song
class Song:
    """sections: [(t0, kind, level)], kind in calm / build / gap / slam / loud / dense. Hits are envelopes that decay,
    like the ear's pulses, so the engine's rising-edge detectors see each one once."""
    def __init__(self, bpm=140, sections=((0, 'loud', 0.8),), title='', artist='', length=180.0, vocal=(), chorus=(), aggr=0.8):
        self.bpm = bpm; self.per = 60 / bpm; self.sec = sorted(sections); self.title = title; self.artist = artist
        self.length = length; self.vocal = vocal; self.chorus = chorus; self.aggr = aggr
    def part(self, pos):
        cur = self.sec[0]
        for s in self.sec:
            if s[0] <= pos: cur = s
        return cur
    def snap(self, pos):
        t0, kind, lv = self.part(pos); per = self.per
        def env(step, off=0.0, every=1):
            ph = ((pos - off) / step) % every
            return math.exp(-(ph * step) / 0.07) if ph * step < 0.3 else 0.0
        level = lv; kick = snare = hat = vocal = 0.0; build = 0.0
        if kind == 'calm': hat = 0.6 * env(per, 0, 2) if lv > 0.15 else 0.0
        elif kind == 'build':
            k = min(1.0, (pos - t0) / 4.0); build = k
            step = per / (1 + 3 * k)                                         # the snare roll speeds up
            snare = env(step); hat = env(per / 2); level = lv * (0.7 + 0.3 * k)
        elif kind == 'gap': level = 0.08
        elif kind in ('slam', 'loud', 'dense'):
            kick = env(per); snare = env(per, per, 2) if per else 0; hat = env(per / 2)
            if kind == 'dense': hat = env(per / 4); snare = env(per / 2, per / 4)
        for a, b in self.vocal:
            if a <= pos < b: vocal = 0.4 + 0.6 * env(per / 2, per / 4)
        bars = [min(1.0, level * (1.2 - i / 20) + (kick if i < 3 else hat if i > 11 else 0) * 0.4) for i in range(16)]
        return dict(active=True, t=CLOCK.t, level=level, excite=level, sub=level * 0.8, bpm=self.bpm, phase=(pos / per) % 1,
                    bars=bars, quiet=False, auto=('groove', ''), build=build, drop_t=-99.0, section=int(t0), sec_energy=lv,
                    chaos=0.2, max_hold=0.0, beat=0.9, kick=kick, snare=snare, hat=hat, vocal=vocal, punch=kick,
                    kps=self.bpm / 60 if kind in ('slam', 'loud', 'dense') else 0, sps=2.0, hps=4.0, vps=1.0, pps=0.0,
                    wall=0.0, hi_mean=2000, subr=0.2, hish=0.2)
    @staticmethod
    def from_map(path):
        m = json.load(open(path))
        return Song(m.get('bpm', 140), [tuple(s) for s in m['sections']], m.get('title', ''), m.get('artist', ''),
                    m.get('length', 180.0), [tuple(v) for v in m.get('vocal', [])], [tuple(c) for c in m.get('chorus', [])], m.get('aggr', 0.8))

class FakeBrain:
    """the song map the brain would have after one play, read from the same Song: sections, drops (slam starts), choruses, voice."""
    def __init__(self, song): self.s = song
    def ctx(self, pos):
        if pos is None: return None
        s = self.s; t0, kind, lv = s.part(pos); starts = [x[0] for x in s.sec]
        drops = [x[0] for x in s.sec if x[1] == 'slam']; nxt = next((t for t in drops if t > pos - 0.15), None)
        return dict(sec=starts.index(t0), drop_in=(nxt - pos) if nxt is not None else None, drop_at=nxt, drop_power=1.0,
                    chorus=any(a <= pos < b for a, b in s.chorus), voice=0.8 if any(a <= pos < b for a, b in s.vocal) else 0.1,
                    aggr=s.aggr, new_sec=abs(pos - t0) < 0.1)
    def targets(self, n, gap=40, drops_only=False): return [x[0] for x in self.s.sec if x[1] == 'slam'][:max(0, n)]
    def __getattr__(self, k): return lambda *a, **kw: None

class FakeMusic:
    """what the window asks the player: a song that plays on the fake clock."""
    def __init__(self, real): self.real = real; self.song = None; self.start = 0.0
    def __getattr__(self, k): return getattr(self.real, k)
    def playing(self): return self.song is not None
    def active(self): return self.song is not None
    def position(self): return (CLOCK.t - self.start) if self.song else None
    def progress(self): return min(1.0, self.position() / self.song.length) if self.song else None
    def artist(self): return self.song.artist if self.song else ''
    def artists(self): return [self.artist()]
    def title(self): return self.song.title if self.song else ''
    def short_active(self): return 'showcase'
    def cmd(self, *a): pass

# ------------------------------------------------------------------ the pet
d = g['Demon'](); F = d.form
d.U = U; d.SH = ZD.H * U; d.WH = d.SH                         # paint only the pet area (no bubble room)
d.music = FakeMusic(d.music); d.brain = None; d.ear_on = True; d.journal = None
d.caption = lambda cr, now: None; d.reshape = lambda: None; d.bubble = lambda *a, **k: None
d.report = None; d.hover = False; d.pinned = False; d.mouse = None
d.get_position = lambda: (0, 0)
for k in ('reactions', 'form', 'resident'): d.cfg[k] = '1'
CANVAS = (ZD.W * U + 28 * U, ZD.H * U + 24 * U); ORG = (14 * U, 16 * U)   # room for blasts, dust and shouts

def set_song(song, at=0.0, brain=False):
    d.music.song = song; d.music.start = CLOCK.t - at; d.brain = FakeBrain(song) if (song and brain) else None
    if song: d.ear.ear.snap = song.snap(at)
    else: d.ear.ear.snap = dict(active=False)

def frame_rgb():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, *CANVAS); cr = cairo.Context(s)
    cr.translate(*ORG)
    d.draw(None, cr)                                              # the real draw: dance, ПОДМЕНЫШ, reactions, СМЕНА, paint_frame
    s.flush()                                                     # (it clears to transparent itself, like the window)
    fg = Image.frombuffer('RGBA', CANVAS, bytes(s.get_data()), 'raw', 'BGRa', 0, 1)
    out = Image.new('RGB', CANVAS, BG); out.paste(fg, (0, 0), fg); return out

def run(seconds, song=None, at=None, hook=None):
    """advance the clock frame by frame; returns the frames."""
    out = []; n = int(round(seconds * FPS))
    for i in range(n):
        CLOCK.t = round(CLOCK.t + DT, 4)
        if d.music.song: d.ear.ear.snap = d.music.song.snap(d.music.position())
        if hook: hook(i / FPS)
        out.append(frame_rgb())
    return out

def reset():
    """a clean pet between scenes: ДЕМОН, no form, no reaction, no song."""
    CLOCK.t += 600
    try:
        if d.form_on(): F.end(CLOCK.t, 'showcase')
    except Exception: pass
    F.mem.d.pop('form', None); F.arc = None; F.jaw = None; F.jaw_t = None; F.blood = []; F.act = None; F.mimic = None
    F.nc = None; F.lure_pv = 0; F.lure = False; F.line = None; F.targets = None; F.morph_req = None
    d.morph = None; d._was_form = False                           # no way-out burst for the reset itself
    d.react.cur = None
    set_song(None)

_n = [0]
def form_in(dg=False, lure=False, hard=True, mimic=False):
    """ПОДМЕНЫШ in him at once (no СМЕНА, no greeting line), the way resident leaves it."""
    _n[0] += 1; key = f'showcase-{_n[0]}'
    F.morph_skip = CLOCK.t; F.start(CLOCK.t, 0, 'showcase', song=key); F.song(CLOCK.t, key, dg=dg, lure=lure)
    try: F.set_hard(hard)
    except Exception: pass
    F.line = None; F.morph_req = None; d.morph = None; d._was_form = True
    if not mimic: F.next_mimic = CLOCK.t + 1e6

def clip(total, a, b, hook=None):
    fr = run(total, hook=hook); return fr[int(round(a * FPS)):int(round(b * FPS))]

# ------------------------------------------------------------------ output
def save_gif(frames, path, crop=None):
    if crop is None: crop = bbox(frames)
    fr = [f.crop(crop) for f in frames]
    pal = fr[0].quantize(colors=64, method=Image.Quantize.MEDIANCUT)
    big = Image.new('RGB', (fr[0].width, fr[0].height * min(len(fr), 12)))
    for i, f in enumerate(fr[::max(1, len(fr) // 12)][:12]): big.paste(f, (0, i * fr[0].height))
    pal = big.quantize(colors=96, method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in fr]
    q[0].save(path, save_all=True, append_images=q[1:], duration=int(1000 / FPS), loop=0, optimize=True, disposal=1)
    return os.path.getsize(path)

def bbox(frames, pad=2 * U):
    x0 = y0 = 10 ** 9; x1 = y1 = 0
    bgimg = Image.new('RGB', CANVAS, BG)
    from PIL import ImageChops
    for f in frames:
        b = ImageChops.difference(f, bgimg).getbbox()
        if b: x0, y0, x1, y1 = min(x0, b[0]), min(y0, b[1]), max(x1, b[2]), max(y1, b[3])
    if x1 == 0: return (0, 0) + CANVAS
    return (max(0, x0 - pad), max(0, y0 - pad), min(CANVAS[0], x1 + pad), min(CANVAS[1], y1 + pad))

SCENES = {}
def scene(name, note):
    def wrap(fn): SCENES[name] = (fn, note); return fn
    return wrap

if __name__ == '__main__':
    import importlib.util
    spec = importlib.util.spec_from_file_location('scenes', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'showcase-scenes-v1.py'))
    sc = importlib.util.module_from_spec(spec); sc.__dict__.update(dict(R=sys.modules[__name__])); spec.loader.exec_module(sc)
    if '--list' in sys.argv:
        for k, (fn, note) in SCENES.items(): print(f'{k:24s} {note}')
        sys.exit()
    outdir = sys.argv[1]; os.makedirs(outdir, exist_ok=True); want = sys.argv[2:] or list(SCENES)
    for name in want:
        fn, note = SCENES[name]; reset()
        frames = fn()
        size = save_gif(frames, f'{outdir}/{name}.gif')
        print(f'{name:24s} {len(frames):4d} frames  {size / 1e6:5.2f} MB  {frames[0].size}')
    shutil.rmtree(FAKE, ignore_errors=True)
