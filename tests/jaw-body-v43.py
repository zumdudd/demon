"""v43: the eater is its full body even if its last live frame was vanished / glyph / faded."""
import os, time
H = os.path.expanduser('~'); P = f'{H}/.local/lib/zarya/desk'
g = {'__name__': 'x', '__file__': f'{H}/.local/bin/zarya-daemon-desk'}
for f in sorted(x for x in os.listdir(P) if x.endswith('.py')): exec(compile(open(f'{P}/{f}').read(), f, 'exec'), g)
d = g['Demon'](); F = d.form; F.start(time.time(), 45, 'test'); ZD = g['ZD']; idle = ZD.build(dict(d.state(), mode='idle'))
F._frame(idle, {}, 0.0); good = len(F._parts[0]) + len(F._parts[2]) + len(F._parts[3])
for name, parts in (('vanished (empty)', ([], [], [], [])), ('glyph form (faded shards)', ([[5, 5, 0.4, 0.4, '#FF2244', 0.3]], [[6, 6, 1, 1, '#E4E0EA', 0.5]], [], []))):
    F._parts = parts; F.vanish = True; before = dict(F.__dict__)
    F._jaw_start(0.0, False); F.jaw_t = 0.0
    out, _ = F._jaw(idle, [], 2.0, idle)
    solid = [r for r in out if r[5] >= 1.0]
    print(f'{name}: eater cells {len(F.jaw["body"])} (clean body {good}), all solid {all(r[5] == 1.0 for r in F.jaw["body"])}, state kept {F.vanish is True and F._parts is parts}')
    assert len(F.jaw['body']) == good and F.vanish is True and F._parts is parts
print('BODY OK')
