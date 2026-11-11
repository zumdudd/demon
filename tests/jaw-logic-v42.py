"""v42: ПАСТЬ bites: on the kick (a hair early once it has the beat), its own rhythm without music, 4 bites, left to right."""
import os, time
H = os.path.expanduser('~'); P = f'{H}/.local/lib/zarya/desk'
g = {'__name__': 'x', '__file__': f'{H}/.local/bin/zarya-daemon-desk'}
for f in sorted(x for x in os.listdir(P) if x.endswith('.py')): exec(compile(open(f'{P}/{f}').read(), f, 'exec'), g)
d = g['Demon'](); F = d.form; F.start(time.time(), 45, 'test'); F.song_key = 'a'
ZD = g['ZD']; idle = ZD.build(dict(d.state(), mode='idle'))
def run(music, beat=None, dur=6.5, fps=30):
    t0 = 1000.0; F._jaw_start(t0, music); F.jaw_t = t0; bites = []; n = 0; fronts = []
    for i in range(int(dur * fps)):
        now = t0 + i / fps
        F.kick_now = bool(beat) and ((now - t0) % beat) < 1 / fps
        out, ov = F._jaw(idle, [], now, idle)
        if F.jaw['bites'] != n:
            n = F.jaw['bites']; bites.append(round(now - t0, 2))
            fronts.append(min(x for x, y, w, h, c, a in out if c not in ('#14060C',)) if out else None)
        if F.jaw['end'] and now > F.jaw['end']: break
    return bites
b = run(True, beat=0.5)
print('on a 120 bpm kick (every 0.50 s):', b)
assert len(b) == 4 and all(abs(((x % 0.5) + 0.06) % 0.5 - 0.0) < 0.07 or abs((x % 0.5)) < 0.04 for x in b[2:]), 'later bites should land on / a hair before the kick'
b2 = run(False); print('no music (own rhythm):', b2); assert len(b2) == 4 and b2[1] - b2[0] < 0.25 and b2[2] - b2[1] > 0.4
b3 = run(True, beat=None); print('music but no kick heard:', b3); assert len(b3) == 4
# left to right: what is left of him shrinks from the left
F._jaw_start(0.0, False); F.jaw_t = 0.0; lefts = []
for k in range(4):
    F.jaw['bites'] = k; F.jaw['last'] = -1
    out, _ = F._jaw(idle, [], 0.5, idle); dem = [r for r in out if r[4] not in [c[4] for c in F._jaw_body(idle, 0)]]
    lefts.append(round(min((r[0] for r in dem), default=99), 1))
print('his left edge after 0-3 bites:', lefts); assert lefts == sorted(lefts) and lefts[0] < lefts[-1]
print('JAW LOGIC OK')
