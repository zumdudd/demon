"""v45: the real window + GTK loop with a fake song playing: ПОДМЕНЫШ in, mimicry acts, every ▶ ПАСТЬ hunt, ▶ ПРОВАЛ, menu. 0 errors."""
import os, time
H = os.path.expanduser('~'); P = f'{H}/.local/lib/zarya/desk'
g = {'__name__': 'x', '__file__': f'{H}/.local/bin/zarya-daemon-desk'}
for f in sorted(x for x in os.listdir(P) if x.endswith('.py')): exec(compile(open(f'{P}/{f}', encoding='utf-8').read(), f, 'exec'), g)
Gtk, GLib = g['Gtk'], g['GLib']; d = g['Demon'](); d.show_all(); F = d.form
d.dancing = lambda: True; d.music.playing = lambda: True; d.ear_on = True
t0 = time.time()
def beat():
    e = time.time() - t0; k = 1.0 if (e % 0.5) < 0.06 else 0.0
    d.ear.ear.snap.update(level=0.7, kick=k, snare=0.0, hat=0.3); return True
items = []
def walk(m):
    for it in m.get_children():
        lab = it.get_label() if hasattr(it, 'get_label') else None
        if lab: items.append(lab)
        if it.get_submenu(): walk(it.get_submenu())
Gtk.Menu.popup_at_pointer = lambda self, ev: walk(self)
plan = [(0.5, lambda: F.start(time.time(), 45, 'live test')), (3.0, lambda: setattr(F, 'next_mimic', 0)), (4.0, lambda: d.menu(None))]
for i, k in enumerate(('hunt', 'stalk', 'fear', 'miss', 'slaughter')):
    plan.append((11 + i * 7, lambda k=k: F.jaw_preview(time.time(), True, k)))
plan += [(47, lambda: F.fail_preview(time.time(), True)), (53, lambda: (setattr(F, 'next_mimic', 0), setattr(F, 'hard', True))), (60, Gtk.main_quit)]
for at, cb in plan: GLib.timeout_add(int(at * 1000), lambda cb=cb: (cb(), False)[1])
GLib.timeout_add(33, lambda: (beat(), d.queue_draw(), True)[1])
Gtk.main()
print('menu items:', [i for i in items if any(w in i for w in ('ПАСТЬ', 'ОХОТА', 'ВЫСЛЕЖ', 'СТРАХ', 'ПРОМАХ', 'БОЙНЯ', 'ПРОВАЛ'))])
log = open(f'{H}/.cache/zarya-daemon-desk.log', encoding='utf-8').read().splitlines()
for l in log:
    if any(k in l for k in ('ПАСТЬ', 'pretends', 'ПРОВАЛ', 'СМЕНА', 'error', 'Error', 'Traceback')): print(' ', l[11:])
assert not any(('error' in l.lower() or 'traceback' in l.lower()) for l in log), 'errors in the log'
assert sum('ПАСТЬ preview' in l for l in log) == 5
print('LIVE OK')
