"""v46: a real window manager (xfwm4, compositing on) + a fake fullscreen game that has focus. Screenshots his corner:
he must be visible over the game (d33 layer) and clicks must reach the game. argv[1] = 0 to run with game_layer=0 (old d31)."""
import os, sys, time, subprocess
H = os.path.expanduser('~'); P = f'{H}/.local/lib/zarya/desk'
g = {'__name__': 'x', '__file__': f'{H}/.local/bin/zarya-daemon-desk'}
for f in sorted(x for x in os.listdir(P) if x.endswith('.py')): exec(compile(open(f'{P}/{f}', encoding='utf-8').read(), f, 'exec'), g)
Gtk, GLib, Gdk = g['Gtk'], g['GLib'], g['Gdk']
d = g['Demon'](); d.cfg['game_layer'] = sys.argv[1] if len(sys.argv) > 1 else '1'; d.show_all()
game = Gtk.Window(title='Dota 2'); game.set_wmclass('dota2', 'dota2')
clicks = []
eb = Gtk.EventBox(); eb.connect('button-press-event', lambda *a: clicks.append(1)); game.add(eb)
game.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.0, 0.6, 0.0, 1.0))
res = {}
def shot(tag):
    x, y = d.get_position(); x0 = x + 3 * d.U; y0 = y + d.WH - d.SH
    out = subprocess.run(['import', '-window', 'root', '-crop', f'{d.SW}x{d.SH}+{x0}+{y0}', '-depth', '8', 'rgb:-'], capture_output=True).stdout
    px = [out[i:i + 3] for i in range(0, len(out), 3)]
    green = sum(1 for p in px if len(p) == 3 and p[1] > 120 and p[0] < 40 and p[2] < 40)
    res[tag] = 1 - green / max(1, len(px)); print(f'{tag}: {res[tag] * 100:.1f} % of his corner is not the game')
    subprocess.run(['import', '-window', 'root', f'/root/out/gamelayer-{tag}.png'])
def start_game(): game.show_all(); game.fullscreen(); game.present()
def click():
    x, y = d.get_position(); subprocess.run(['xdotool', 'mousemove', str(x + (3 + 7) * d.U), str(y + d.WH - d.SH + 6 * d.U), 'click', '1'])
plan = [(1.5, lambda: shot('before')), (2.0, start_game), (4.0, d.slow), (5.0, lambda: print('active:', subprocess.run(['xprop','-root','_NET_ACTIVE_WINDOW'],capture_output=True,text=True).stdout.strip(), d.fullscreen_active()[0])), (5.5, lambda: shot('in-game')), (6.0, click),
        (7.0, lambda: print('game got the click:', bool(clicks), '· gaming:', getattr(d, 'gaming', None), '· layer:', getattr(d, 'glayer', None) is not None)),
        (7.5, game.unfullscreen), (7.6, game.hide), (8.5, d.slow), (10.0, lambda: shot('after')), (10.5, Gtk.main_quit)]
for at, cb in plan: GLib.timeout_add(int(at * 1000), lambda cb=cb: (cb(), False)[1])
GLib.timeout_add(100, lambda: (d.queue_draw(), True)[1])
Gtk.main()
log = open(f'{H}/.cache/zarya-daemon-desk.log', encoding='utf-8').read().splitlines()
for l in log:
    if 'game:' in l or 'rror' in l: print(' ', l[11:])
print('RESULT', 'ON TOP' if res['in-game'] > 0.15 else 'HIDDEN', 'clicks reach the game:', bool(clicks), 'visible after:', res['after'] > 0.15 or res['before'] < 0.2)
