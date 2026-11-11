"""v44: the real window + GTK loop: way in, Изгнать (resists once, then a ritual), every ▶ СМЕНА preview, a game on / off. 0 errors."""
import os, time
H = os.path.expanduser('~'); P = f'{H}/.local/lib/zarya/desk'
g = {'__name__': 'x', '__file__': f'{H}/.local/bin/zarya-daemon-desk'}
for f in sorted(x for x in os.listdir(P) if x.endswith('.py')): exec(compile(open(f'{P}/{f}', encoding='utf-8').read(), f, 'exec'), g)
Gtk, GLib = g['Gtk'], g['GLib']; d = g['Demon'](); d.show_all(); F = d.form
items = []
def walk(m):
    for it in m.get_children():
        lab = it.get_label() if hasattr(it, 'get_label') else None
        if lab: items.append(lab)
        if it.get_submenu(): walk(it.get_submenu())
Gtk.Menu.popup_at_pointer = lambda self, ev: walk(self)
plan = [(0.5, lambda: F.start(time.time(), 45, 'live test')), (3.0, lambda: d.exorcise('you drove it out')),
        (3.5, lambda: d.exorcise('you drove it out')), (9.0, lambda: d.menu(None))]
for i, r in enumerate(('in', 'summon', 'cult', 'pagan', 'none', 'plain')):
    plan.append((10 + i * 5.5, lambda r=r: d.morph_preview('in') if r == 'in' else d.morph_preview('out', r)))
d.fullscreen_active = lambda: (bool(getattr(d, '_fake_fs', False)), 'WM_CLASS(STRING) = "steam_app_570", "dota2"')
plan += [(44, lambda: setattr(d, '_fake_fs', True)), (44.1, d.slow), (46, lambda: F.start(time.time(), 45, 'in a game')),
         (49, lambda: setattr(d, '_fake_fs', False)), (49.1, d.slow), (51, Gtk.main_quit)]
t0 = time.time()
for at, cb in plan: GLib.timeout_add(int(at * 1000), lambda cb=cb: (cb(), False)[1])
GLib.timeout_add(33, lambda: (d.queue_draw(), True)[1])
Gtk.main()
print('menu СМЕНА items:', [i for i in items if 'СМЕНА' in i or 'way ' in i])
log = open(f'{H}/.cache/zarya-daemon-desk.log', encoding='utf-8').read().splitlines()
for l in log:
    if any(k in l for k in ('СМЕНА', 'game:', 'held on', 'left him', 'error', 'Error', 'Traceback')): print(' ', l)
assert not any(('error' in l.lower() or 'traceback' in l.lower()) for l in log), 'errors in the log'
assert sum('СМЕНА out' in l for l in log) == 1 and sum('СМЕНА in' in l for l in log) >= 2
print('LIVE OK')
