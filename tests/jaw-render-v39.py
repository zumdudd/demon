"""v39: render ПАСТЬ frames from the real desk + hurt code (Xvfb), stitched into one strip."""
import os, sys, time
H = os.path.expanduser('~'); P = f'{H}/.local/lib/zarya/desk'
g = {'__name__': 'x', '__file__': f'{H}/.local/bin/zarya-daemon-desk'}
for f in sorted(x for x in os.listdir(P) if x.endswith('.py')): exec(compile(open(f'{P}/{f}').read(), f, 'exec'), g)
cairo = g['cairo']; d = g['Demon']()
d.form.start(time.time(), 45, 'test')
print('form on:', d.form_on(), 'jaw_preview:', hasattr(d.form, 'jaw_preview'))
times = [0.6, 1.1, 1.3, 1.39, 1.45, 1.6, 1.75, 2.15, 2.42, 2.65]
frames = []
for k in times:
    d.form.jaw_preview(time.time() - k); d.report = None; d.reports = []
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, d.SW + 40, d.WH); cr = cairo.Context(s)
    d.draw(None, cr); frames.append(s)
W = d.SW + 40; UPX = 70; out = cairo.ImageSurface(cairo.FORMAT_ARGB32, W * len(frames), d.SH + 30 + UPX); cr = cairo.Context(out)
cr.set_source_rgb(0.85, 0.85, 0.88); cr.paint()
for i, s in enumerate(frames):
    cr.set_source_surface(s, i * W, -(d.WH - d.SH) + 10 + UPX); cr.paint()
    cr.set_source_rgb(0.2, 0.2, 0.2); cr.move_to(i * W + 6, d.SH + 24 + UPX); cr.show_text(f'{times[i] - 0.9:+.2f}s')
big = cairo.ImageSurface(cairo.FORMAT_ARGB32, out.get_width() * 2, out.get_height() * 2); c2 = cairo.Context(big); c2.scale(2, 2)
c2.set_source_surface(out, 0, 0); c2.get_source().set_filter(cairo.FILTER_NEAREST); c2.paint(); big.write_to_png(sys.argv[1]); print('sprite', d.SW, d.SH, 'win', d.WW, d.WH)
