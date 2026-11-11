"""v45: renders the 5 ПАСТЬ hunts + a ПРОВАЛ from the real Form + desk code as a GIF: python3 hunt-render-v45.py OUT.gif [SHEET.png]"""
import os, sys, math, random
H = os.path.expanduser('~'); P = f'{H}/.local/lib/zarya/desk'
g = {'__name__': 'x', '__file__': f'{H}/.local/bin/zarya-daemon-desk'}
for f in sorted(x for x in os.listdir(P) if x.endswith('.py')): exec(compile(open(f'{P}/{f}', encoding='utf-8').read(), f, 'exec'), g)
from PIL import Image
cairo = g['cairo']; d = g['Demon'](); ZD = g['ZD']; ZH = g['ZH']; F = d.form
d.form_on = lambda: True
st = d.state()
U = 6; W, Hh = 24 * U, 18 * U
def rgb(c, a): return (int(c[1:3], 16) / 255, int(c[3:5], 16) / 255, int(c[5:7], 16) / 255, a)
def paint(rects, label):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, Hh + 16); cr = cairo.Context(s)
    cr.set_source_rgb(0.12, 0.10, 0.16); cr.paint(); gx, gy = 2 * U, 2 * U
    for x, y, w, h, c, al in rects:
        cr.set_source_rgba(*rgb(c, al)); cr.rectangle(round(gx + x * U), round(gy + y * U), max(1, round(w * U)), max(1, round(h * U))); cr.fill()
    cr.set_source_rgb(0.9, 0.9, 0.9); cr.select_font_face('DejaVu Sans', 0, 0); cr.set_font_size(11); cr.move_to(4, Hh + 12); cr.show_text(label)
    return Image.frombuffer('RGBA', (W, Hh + 16), bytes(s.get_data()), 'raw', 'BGRA', 0, 1).convert('RGB')
per = 0.5
def snap(t): return dict(level=0.7, kick=1.0 if (t % per) < 0.034 else 0.0, snare=0.0, hat=0.3, progress=0.5)
def dance_frame(mode, t, sn):
    r, ov, hide = d.dance.draw(ZD.build(dict(st, mode='idle')), mode, 'base' if mode == 'kendrick' else '', sn, t, ZD.C['G'], {})
    return r
clips = []
def hunt(kind):
    F.jaw = None; F.jaw_t = None; F.blood = []; F.act = None; F.arc = None; F.buf = []
    t0 = 1000.0; F.mimic = t0 + 20; F._jaw_start(t0 + 0.7, True, kind); fr = []; t = t0
    while t < t0 + 9:
        sn = snap(t - t0); dn = dance_frame('groove', t, sn)
        r, ov = F.frame(ZD.build(dict(st, mode='idle')), sn, t, music=True, dance=dn)
        fr.append(paint(r, f'ПАСТЬ · {ZH.HUNT_RU[kind]}  {t - t0:.1f}s'))
        j = F.jaw
        if j['end'] is not None and t > j['end'] + 0.6 and not F.blood: break
        if j['end'] is not None and t > j['end'] + 4.2: break
        t = round(t + 1 / 30, 4)
    clips.append(fr)
for k in ('hunt', 'stalk', 'fear', 'miss', 'slaughter'): hunt(k)
# ПРОВАЛ: a calm sway on a hard song, then the disguise breaks
F.jaw = None; F.jaw_t = None; F.blood = []; F.hard = True; F.rng = random.Random(3)
a = F._act_pick(2000.0, True, fail=True); a.update(kind='d', name='bolero', end=2004.0); F.mimic = 2004.0; fr = []; t = 2000.0
while t < 2004.0:
    mode, var, sn = d.mimic_mode('mosh', '', snap(t - 2000), t)
    dn = dance_frame(mode, t, sn); dn, _, _ = d.mimic_after(dn, [], False, t, st, sn)
    r, ov = F.frame(ZD.build(dict(st, mode='idle')), snap(t - 2000), t, music=True, dance=dn)
    fr.append(paint(r, f'ПРОВАЛ · БОЛЕРО on a hard song  {t - 2000:.1f}s')); t = round(t + 1 / 30, 4)
clips.append(fr)
cols, rows = 3, 2; n = max(len(f) for f in clips); frames = []
for i in range(0, n, 2):
    cv = Image.new('RGB', (W * cols, (Hh + 16) * rows), (20, 18, 26))
    for k, fr in enumerate(clips): cv.paste(fr[min(i, len(fr) - 1)], ((k % cols) * W, (k // cols) * (Hh + 16)))
    frames.append(cv)
frames[0].save(sys.argv[1], save_all=True, append_images=frames[1:], duration=66, loop=0, optimize=True)
if len(sys.argv) > 2:
    sh = Image.new('RGB', (W * 6, (Hh + 16) * len(clips)), (20, 18, 26))
    for r_, fr in enumerate(clips):
        for c_, q in enumerate((0.1, 0.3, 0.45, 0.6, 0.75, 0.95)): sh.paste(fr[min(len(fr) - 1, int(len(fr) * q))], (c_ * W, r_ * (Hh + 16)))
    sh.save(sys.argv[2])
print('frames', len(frames), [len(f) for f in clips])
