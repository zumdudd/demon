"""v36 runtime: d28 in Xvfb: menu walks, a reaction preview lands on the bus, song_start / song_end, director skip notes."""
import os, sys, json, glob, time
H = os.path.expanduser('~'); P = f'{H}/.local/lib/zarya/desk'
g = {'__name__': 'desk_test', '__file__': f'{H}/.local/bin/zarya-daemon-desk'}
for f in sorted(x for x in os.listdir(P) if x.endswith('.py')):
    exec(compile(open(f'{P}/{f}', encoding='utf-8').read(), f'{P}/{f}', 'exec'), g)
Gtk = g['Gtk']; d = g['Demon']()
items = []
def walk(m, depth=0):
    for it in m.get_children():
        lab = it.get_label() if hasattr(it, 'get_label') else None
        if lab: items.append(lab)
        if it.get_submenu(): walk(it.get_submenu(), depth + 1)
Gtk.Menu.popup_at_pointer = lambda self, ev: walk(self)
d.menu(None)
print('menu items:', len(items), '| about:', [i for i in items if 'ОБ АВТОРЕ' in i])
d.screen_event('fire', 'preview')
# fake a playing song
class M:
    def __init__(s, real): s.r = real
    def __getattr__(s, k): return getattr(s.r, k)
    def artist(s, r=None): return 'Death Grips'
    def artists(s, r=None): return ['Death Grips']
    def title(s, r=None): return 'Guillotine'
    def position(s): return 42.0
d.music = M(d.music); d.mkey = ('spotify', 'x')
B0 = g['DIRECTOR']; B0.song(d, d.mkey)
B = g['DIRECTOR']; B.react_outer_note(d, 'ПОДМЕНЫШ is here (its own moves)'); B.react_outer_note(d, 'ПОДМЕНЫШ is here (its own moves)')
B.react_outer_note(d, 'not dancing')
print('outer gate now:', B.react_outer(d))
B0.song(d, None)
recs = [json.loads(l) for p in glob.glob(f'{H}/.cache/zarya/bus-*.jsonl') for l in open(p, encoding='utf-8')]
kinds = [r['kind'] for r in recs]
print('bus kinds:', {k: kinds.count(k) for k in dict.fromkeys(kinds)})
for r in recs:
    if r['kind'] in ('react', 'song_start', 'skip', 'song_end'): print(' ', json.dumps(r, ensure_ascii=False))
assert any(r['kind'] == 'react' and 'fire' in r['msg'] for r in recs)
assert sum(1 for r in recs if r['kind'] == 'skip') == 1
assert any(r['kind'] == 'song_start' and r.get('deli') and r.get('sec') == 42.0 for r in recs)
print('RUNTIME OK')
