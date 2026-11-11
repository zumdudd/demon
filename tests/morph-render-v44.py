"""v44: renders СМЕНА from the real Morph (way in + the 5 ways out) as a GIF: python3 morph-render-v44.py OUT.gif [OUT_sheet.png]"""
import os, sys, math
H = os.path.expanduser('~'); P = f'{H}/.local/lib/zarya/desk'
g = {'__name__': 'x', '__file__': f'{H}/.local/bin/zarya-daemon-desk'}
for f in sorted(x for x in os.listdir(P) if x.endswith('.py')): exec(compile(open(f'{P}/{f}', encoding='utf-8').read(), f, 'exec'), g)
import time
from PIL import Image
cairo = g['cairo']; d = g['Demon'](); ZD = g['ZD']; ZH = g['ZH']; F = d.form
st = d.state(); idle = ZD.build(dict(st, mode='idle')); body, eyes = ZH.form_cells(F, idle, 0)
U = 6; W, Hh = 22 * U, 30 * U; TOP = 12                                       # 12 rows above his area for the moon / shadow
def rgb(c, a): return (int(c[1:3], 16) / 255, int(c[3:5], 16) / 255, int(c[5:7], 16) / 255, a)
def paint(rects, ov, label):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, Hh + 16); cr = cairo.Context(s)
    cr.set_source_rgb(0.12, 0.10, 0.16); cr.paint()
    gx, gy = U, TOP * U
    for k, a in ov:
        if k == 'under':
            for x, y, w, h, c, al in a: cr.set_source_rgba(*rgb(c, al)); cr.rectangle(round(gx + x * U), round(gy + y * U), max(1, round(w * U)), max(1, round(h * U))); cr.fill()
    for x, y, w, h, c, al in rects:
        cr.set_source_rgba(*rgb(c, al)); cr.rectangle(round(gx + x * U), round(gy + y * U), max(1, round(w * U)), max(1, round(h * U))); cr.fill()
    for k, a in ov:
        if k == 'glyphs':
            cr.select_font_face('DejaVu Sans Mono', 0, 1); cr.set_font_size(1.6 * U)
            for x, y, ch, al, c in a: cr.set_source_rgba(*rgb(c, al)); cr.move_to(gx + x * U, gy + y * U + U); cr.show_text(ch)
        elif k == 'flash':
            c, al = a; pat = cairo.RadialGradient(gx + (ZH.OX + 7) * U, gy + (ZH.OY + 5) * U, 4, gx + (ZH.OX + 7) * U, gy + (ZH.OY + 5) * U, 13 * U)
            r_, g_, b_, _ = rgb(c, 1); pat.add_color_stop_rgba(0, r_, g_, b_, al); pat.add_color_stop_rgba(1, r_, g_, b_, 0); cr.set_source(pat); cr.paint()
    cr.set_source_rgb(0.9, 0.9, 0.9); cr.select_font_face('DejaVu Sans', 0, 0); cr.set_font_size(11); cr.move_to(4, Hh + 12); cr.show_text(label)
    return Image.frombuffer('RGBA', (W, Hh + 16), bytes(s.get_data()), 'raw', 'BGRA', 0, 1).convert('RGB')

clips = []
def run(label, m, live, kicks=()):
    fr, t = [], 0.0
    for _ in range(12): fr.append(paint(live if m.kind == 'in' else body + eyes, [], label + ' · before'))
    while t < 10:
        sn = dict(kick=1.0 if any(abs(t - k) < 0.02 for k in kicks) else 0.0)
        r, ov, dn = m.frame(t, sn, live)
        fr.append(paint(r, ov, f'{label} · {t:.2f}s'))
        if dn: break
        t = round(t + 1 / 30, 4)
    end = body + eyes if m.kind == 'in' else live
    for _ in range(18): fr.append(paint(end, [], label + ' · after'))
    clips.append((label, fr))

kicks = [0.47 + 0.43 * i for i in range(30)]
run('ЗАРАЖЕНИЕ → ПОДМЕНЫШ (kick 140 bpm)', ZH.Morph('in', idle, body, 0.0, eyes=eyes, music=True), idle, kicks)
for rit in ('summon', 'cult', 'pagan', 'none', 'plain'):
    run(f'way out · {ZH.MORPH_RU[rit]}', ZH.Morph('out', body, None, 0.0, eyes=eyes, rit=rit, music=True, eye_col=ZD.C['G']), idle, kicks)
cols = 3; rows = 2; n = max(len(f) for _, f in clips)
frames = []
for i in range(n):
    canvas = Image.new('RGB', (W * cols, (Hh + 16) * rows), (20, 18, 26))
    for k, (_, fr) in enumerate(clips): canvas.paste(fr[min(i, len(fr) - 1)], ((k % cols) * W, (k // cols) * (Hh + 16)))
    frames.append(canvas)
frames[0].save(sys.argv[1], save_all=True, append_images=frames[1:], duration=33, loop=0, optimize=True)
if len(sys.argv) > 2:                                                           # a contact sheet of key moments
    pick = []
    for lab, fr in clips: pick.append([fr[min(len(fr) - 1, int(len(fr) * q))] for q in (0.12, 0.3, 0.45, 0.6, 0.75, 0.97)])
    sh = Image.new('RGB', (W * 6, (Hh + 16) * len(pick)), (20, 18, 26))
    for r_, row in enumerate(pick):
        for c_, im in enumerate(row): sh.paste(im, (c_ * W, r_ * (Hh + 16)))
    sh.save(sys.argv[2])
print('frames', n, 'clips', [(l, len(f)) for l, f in clips])
