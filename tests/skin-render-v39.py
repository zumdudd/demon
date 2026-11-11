"""v39: ПОДМЕНЫШ skin on messages + menu, СЛЕДЫ on his body. Writes one PNG."""
import os, sys, time
H = os.path.expanduser('~'); P = f'{H}/.local/lib/zarya/desk'
g = {'__name__': 'x', '__file__': f'{H}/.local/bin/zarya-daemon-desk'}
for f in sorted(x for x in os.listdir(P) if x.endswith('.py')): exec(compile(open(f'{P}/{f}').read(), f, 'exec'), g)
cairo, Gtk, Gdk, GLib = g['cairo'], g['Gtk'], g['Gdk'], g['GLib']
d = g['Demon'](); shots = []
def snap(label):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, d.WW, d.WH); cr = cairo.Context(s); cr.set_source_rgb(0.86, 0.86, 0.9); cr.paint()
    d.draw(None, cr); shots.append((label, s))
for form, posts in ((False, [('info', 'ЗАГРУЗКА', 'DOWNLOAD FINISHED ↗', '')]), (True, [('info', 'ЗАГРУЗКА', 'DOWNLOAD FINISHED ↗', ''), ('ok', '♥', 'SAVED TO YOUR LIKED SONGS', ''), ('warn', 'ПЕРЕРЫВ', '2H AT THE DESK\nSTAND UP · DRINK WATER', 'CLICK TO DISMISS')])):
    if form: d.form.start(time.time(), 45, 'test')
    elif d.form and d.form.state(): d.form.end(time.time(), 'test')
    for lvl, t, b, h in posts:
        d.report = [lvl, t, b, h, 5]; d.report_until = time.time() + 5; snap(f'{"ПОДМЕНЫШ" if form else "ДЕМОН"} {t}')
d.form.end(time.time(), 'test'); d.report = None
d.hurt.mem.d['residue'] = dict(day=time.strftime('%F'), cells=[[1, 1], [12, 2], [6, 9], [13, 8], [3, 5], [10, 6]])
snap('СЛЕДЫ on him')
W = max(s.get_width() for _, s in shots); Hh = sum(s.get_height() // 2 + 18 for _, s in shots)
out = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, Hh); cr = cairo.Context(out); cr.set_source_rgb(1, 1, 1); cr.paint(); y = 0
for lab, s in shots:
    cr.set_source_rgb(0, 0, 0); cr.move_to(4, y + 13); cr.show_text(lab); y += 18
    cr.save(); cr.translate(0, y - s.get_height() // 2); cr.set_source_surface(s, 0, 0); cr.rectangle(0, s.get_height() // 2, W, s.get_height() // 2); cr.clip(); cr.paint(); cr.restore(); y += s.get_height() // 2
out.write_to_png(sys.argv[1])
# the menu, for real, with ПОДМЕНЫШ in him
d.form.start(time.time(), 45, 'test')
d.move(0, 0); d.show_all()
def pop():
    ev = Gdk.Event.new(Gdk.EventType.BUTTON_PRESS); ev.button = 3; ev.window = d.get_window(); ev.x = 40; ev.y = 40
    seat = Gdk.Display.get_default().get_default_seat(); ev.set_device(seat.get_pointer())
    d.menu(ev); return False
def grab():
    w = Gdk.get_default_root_window(); pb = Gdk.pixbuf_get_from_window(w, 0, 0, 700, 700); pb.savev(sys.argv[2], 'png', [], []); Gtk.main_quit(); return False
GLib.timeout_add(600, pop); GLib.timeout_add(1800, grab); Gtk.main()
