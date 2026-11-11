"""v42: ПАСТЬ frames in order (its own rhythm), drawn from the real cells at unit 6."""
import os, sys
H = os.path.expanduser('~'); P = f'{H}/.local/lib/zarya/desk'
g = {'__name__': 'x', '__file__': f'{H}/.local/bin/zarya-daemon-desk'}
for f in sorted(x for x in os.listdir(P) if x.endswith('.py')): exec(compile(open(f'{P}/{f}').read(), f, 'exec'), g)
import time; cairo = g['cairo']; d = g['Demon'](); F = d.form; F.start(time.time(), 45, 'test')
ZD = g['ZD']; idle = ZD.build(dict(d.state(), mode='idle'))
F._jaw_start(0.0, False); F.jaw_t = 0.0
want = [0.10, 0.34, 0.42, 0.48, 0.9, 1.08, 1.25, 1.5, 1.64, 1.9]; shots = []; t = 0.0; i = 0
while i < len(want):
    out, ov = F._jaw(idle, [], t, idle)
    if t >= want[i] - 1e-9: shots.append((want[i], out, F.jaw['bites'])); i += 1
    t = round(t + 1 / 60, 5)
U = 6; W = 24 * U; Hh = 18 * U
img = cairo.ImageSurface(cairo.FORMAT_ARGB32, W * len(shots), Hh + 16); cr = cairo.Context(img); cr.set_source_rgb(0.86, 0.86, 0.9); cr.paint()
for k, (tt, rs, n) in enumerate(shots):
    cr.save(); cr.rectangle(k * W + 2 * U, 0, 20 * U, Hh); cr.clip(); cr.set_source_rgb(0.80, 0.80, 0.85); cr.paint()
    for x, y, w, h, c, a in rs:
        r, gg, b = (int(c[i:i + 2], 16) / 255 for i in (1, 3, 5)); cr.set_source_rgba(r, gg, b, a)
        cr.rectangle(k * W + (x + 2) * U, (y + 1) * U, w * U, h * U); cr.fill()
    cr.restore()
    cr.set_source_rgb(0.2, 0.2, 0.2); cr.move_to(k * W + 4, Hh + 12); cr.show_text(f'{tt:.2f}s  bites {n}')
img.write_to_png(sys.argv[1])
