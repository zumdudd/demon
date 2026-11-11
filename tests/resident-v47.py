"""v47 d34: ПОДМЕНЫШ ЖИВЁТ ЗДЕСЬ. Real desk parts in Xvfb; drives res_tick with a fake song clock."""
import os, sys, time
H = os.path.expanduser('~'); P = f'{H}/.local/lib/zarya/desk'
g = {'__name__': 'desk_test', '__file__': f'{H}/.local/bin/zarya-daemon-desk'}
for f in sorted(x for x in os.listdir(P) if x.endswith('.py')):
    exec(compile(open(f'{P}/{f}', encoding='utf-8').read(), f'{P}/{f}', 'exec'), g)
d = g['Demon'](); ZH = g['ZH']; ok = []
def check(name, cond):
    print(('  ОК ' if cond else '  ✕  ') + name); ok.append(bool(cond))
class M:
    def __init__(s, real): s.r = real; s.on = False; s.t = 'x'
    def __getattr__(s, k): return getattr(s.r, k)
    def playing(s): return s.on
    def artist(s, r=None): return 'Someone'
    def artists(s, r=None): return ['Someone']
    def title(s, r=None): return s.t
    def position(s): return 30.0
d.music = M(d.music); calm = [None]
d.res_calm = lambda: (calm[0], None if calm[0] is None else not calm[0])
d.screen_fx = None; d.morph = None; d.stand = None
T = time.time()
def song(key, c): d.music.on = key is not None; d.mkey = key; calm[0] = c; d.music.t = str(key)
check('resident on by default', d.res_on())
check('skin on while resident (even before it is in him)', g['skin_on'](d))
song(None, None); d.res_tick(T + 1); check('waits a moment after start', not d.form_on())
d.res_tick(T + 4); check('it comes in at start (no song)', d.form_on())
check('open-ended stay (until 0)', d.form.state().get('until') == 0)
song('calm1', True); d.res_tick(T + 10); d.res_tick(T + 25); check('still in it at 15 s of a calm song', d.form_on())
d.res_tick(T + 31); check('calm song 21 s: it leaves, ДЕМОН shows', not d.form_on())
d.res_tick(T + 200); check('stays away for the rest of the calm song', not d.form_on())
song('calm2', True); d.res_tick(T + 210); d.res_tick(T + 260); check('next calm song: still ДЕМОН', not d.form_on())
song('hard1', False); d.res_tick(T + 300); check('hard song at 0 s: waits 8 s', not d.form_on())
d.res_tick(T + 309); check('hard song 9 s: it comes back', d.form_on())
d.exorcise('the calm songs starved it', force=True); check('starved: gone', not d.form_on())
d.res_tick(T + 310); d.res_tick(T + 310 + 19 * 60); check('starved: away 19 min', not d.form_on())
d.res_tick(T + 310 + 21 * 60); d.res_tick(T + 310 + 21 * 60 + 9); check('starved: back after 20 min', d.form_on())
d.exorcise('you drove it out'); r1 = d.form_on(); n = 1
while d.form_on() and n < 4: d.exorcise('you drove it out'); n += 1
check(f'Изгнать: it holds on (night rule: up to 2), then goes after {n} tries', r1 and not d.form_on() and n == (3 if ZH.night(time.time()) else 2))
t0 = T + 4000; d.res_tick(t0); d.res_tick(t0 + 29 * 60 + 9); check('Изгнать: away 29 min', not d.form_on())
d.res_tick(t0 + 31 * 60); d.res_tick(t0 + 31 * 60 + 9); check('Изгнать: back after 30 min', d.form_on())
d.exorcise('test', force=True); d.form.start(time.time(), 45, 'ДЕЛИКАТЕС'); check('ДЕЛИКАТЕС start while resident: no time limit', d.form.state().get('until') == 0)
d.exorcise('test', force=True); d.cfg['resident'] = '0'
d.res_tick(T + 9000); d.res_tick(T + 9100); check('resident=0: never comes back by itself', not d.form_on())
d.form.start(time.time(), 45, 'ДЕЛИКАТЕС'); check('resident=0: 45-min stay as before', d.form.state().get('until', 0) > time.time() + 40 * 60)
d.exorcise('test', force=True); check('resident=0: skin off when it is not in him', not g['skin_on'](d))
items = []
def walk(m):
    for it in m.get_children():
        lab = it.get_label() if hasattr(it, 'get_label') else None
        if lab: items.append(lab)
        if it.get_submenu(): walk(it.get_submenu())
g['Gtk'].Menu.popup_at_pointer = lambda self, ev: walk(self)
d.menu(None); check('menu toggle present', any('ПОДМЕНЫШ ЖИВЁТ ЗДЕСЬ' in i for i in items))
log = open(f'{H}/.cache/zarya-daemon-desk.log', encoding='utf-8').read()
check('no resident errors in the log', 'resident tick error' not in log and 'resident calm check error' not in log and 'resident start error' not in log)
print('\n'.join(l for l in log.splitlines() if 'resident' in l or 'is here' in l or 'left him' in l)[-2500:])
print(f'RESIDENT {sum(ok)}/{len(ok)}'); sys.exit(0 if all(ok) else 1)
