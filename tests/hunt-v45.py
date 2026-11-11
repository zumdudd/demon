"""v45: ПАСТЬ hunts + blood, МИМИКРИЯ pool, ПРОВАЛ, on the real desk + hurt parts (logic, no window loop)."""
import os, sys, time, math, random
H = os.path.expanduser('~'); P = f'{H}/.local/lib/zarya/desk'
g = {'__name__': 'x', '__file__': f'{H}/.local/bin/zarya-daemon-desk'}
for f in sorted(x for x in os.listdir(P) if x.endswith('.py')): exec(compile(open(f'{P}/{f}', encoding='utf-8').read(), f, 'exec'), g)
d = g['Demon'](); F = d.form; ZD = g['ZD']; ZH = g['ZH']; ZM = g['ZM']
ok = 0
def check(cond, what):
    global ok
    print(('  ОК  ' if cond else '  ✕   ') + what); assert cond, what; ok += 1
def finite(rs): return all(all(math.isfinite(v) for v in r[:4]) and isinstance(r[4], str) and r[4].startswith('#') for r in rs)
st = d.state(); idle = ZD.build(dict(st, mode='idle'))
check(g['VERSION'] in ('d32', 'd33', 'd34', 'd36', 'd37') and ZH.VERSION == 'h19', f'versions {g["VERSION"]} / {ZH.VERSION}')

def run_hunt(kind, music, bpm=120):
    F.jaw = None; F.jaw_t = None; F.blood = []; F.act = None
    t0 = 5000.0; F._jaw_start(t0, music, kind); per = 60 / bpm
    t = t0; bites = []; frames = 0; empty = 0; ends = None; minx = []
    while t < t0 + 8:
        F.kick_now = music and ((t - t0) % per) < 1 / 30
        out, ov = F._jaw([list(r) for r in idle], [], t, idle)
        out = out + F._blood_cells(t)
        assert finite(out), kind
        if not out: empty += 1
        j = F.jaw
        if j['bites'] > len(bites): bites.append(round(t - t0, 2))
        if j['end'] is not None and ends is None: ends = t - t0
        if j['end'] is not None and t > j['end']: break
        frames += 1; t = round(t + 1 / 30, 4)
    return bites, ends, empty, F.jaw
want = dict(hunt=4, stalk=4, fear=4, miss=1, slaughter=6)
times = {}
for k in ('hunt', 'stalk', 'fear', 'miss', 'slaughter'):
    for music in (False, True):
        b, e, empty, j = run_hunt(k, music)
        check(len(b) == want[k] and e is not None and empty == 0, f'{ZH.HUNT_RU[k]:13} music={music!s:5}: {len(b)} bites at {b}, done {e:.2f} s, never empty')
        times[(k, music)] = b
check(times[('stalk', False)][0] > times[('hunt', False)][0] + 1.0, 'ВЫСЛЕЖИВАНИЕ waits > 1 s longer than ОХОТА')
check(times[('slaughter', True)][-1] < times[('hunt', True)][-1], 'БОЙНЯ finishes before ОХОТА on the same beat')
# miss: after the bite he is still whole and to the right
F._jaw_start(0.0, False, 'miss'); F.jaw['bites'] = 1; F.jaw['last'] = 0.0; F.jaw['end'] = 0.75
out, _ = F._jaw([list(r) for r in idle], [], 0.1, idle)
mine = [r for r in out if r[4] in [c[4] for c in idle]]
check(len(out) >= len(idle), f'ПРОМАХ: he keeps every cell ({len(out)} drawn)')
# blood: appears, falls, gone by 4.1 s
F.blood = []; F.jaw = dict(bx=(4.0,), bites=1, kind='slaughter', blood=8); F._blood_bite(F.jaw, 100.0)
n0 = len(F._blood_cells(100.0)); ys = []
for k in range(1, 100): bl = F._blood_cells(100.0 + k / 30); ys.append(max([c[1] for c in bl], default=0))
n35 = len(F._blood_cells(102.0)); n41 = len(F._blood_cells(104.1))
check(n0 == 8 and n35 > 0 and n41 == 0, f'blood: 8 drops, still there at 2 s ({n35}), gone by 4.1 s')
check(max(ys) <= ZH.OY + 10.01, 'blood stops at the floor')
cols = {c[4] for k in range(0, 120, 6) for c in (F.blood.clear() or F._blood_bite(dict(bx=(4.0,), bites=1, kind='hunt', blood=3), 0) or F._blood_cells(k / 30))}
# pool: shuffle bag covers everything before repeating
F.bag = None; F.hard = False; F.rng = random.Random(7)
seen = [F._act_pick(1000 + i, True, fail=False)['name'] for i in range(len(ZH.ACT_POOL))]
check(len(set(seen)) == len(ZH.ACT_POOL) == 23, f'МИМИКРИЯ: {len(set(seen))} different acts before any repeat (pool 23)')
# fail: misfits by song
F.hard = True; fh = {F._act_pick(0, True, fail=True)['name'] for _ in range(60)}
F.hard = False; fc = {F._act_pick(0, True, fail=True)['name'] for _ in range(60)}
check(fh <= {'bolero', 'rest', 'hum', 'memory', 'sleep', 'tear'} and fc <= {'mosh', 'break', 'grips', 'fire', 'blown', 'alert'}, f'ПРОВАЛ picks the wrong act: hard → {sorted(fh)}, calm → {sorted(fc)}')
F.rng = random.Random(1); nf = sum(F._act_pick(0, True)['fail'] for _ in range(2000))
check(300 < nf < 700, f'ПРОВАЛ rate {nf / 2000:.2f} (≈ 0.25)')
check(not any(F._act_pick(0, False)['fail'] for _ in range(200)), 'no ПРОВАЛ without music')
# disguise break: last 1.2 s only
F.jaw_t = None; a = F._act_pick(0.0, True, fail=True); a['end'] = 5.0
early = F._break_disguise([list(r) for r in idle], 2.0); late = F._break_disguise([list(r) for r in idle], 4.7)
red = lambda rs: sum(1 for r in rs if r[4] == ZH.RED)
check(early == [list(r) for r in idle] and red(late) > 3, f'disguise breaks only at the end ({red(late)} red cells in the last 0.3 s)')
# end of a failed act: eaten about half the time, never twice inside 90 s
eat = 0
for i in range(400):
    F.jaw_t = None; F.jaw = None; F.fail_eat_t = -1e9; F.act = dict(fail=True); eat += F._act_end(10.0, True)
check(140 < eat < 260, f'ПРОВАЛ → ПАСТЬ {eat / 400:.2f} of the time (≈ 0.5)')
F.jaw_t = None; F.fail_eat_t = 5.0; F.act = dict(fail=True); F.rng = random.Random(0)
check(not any((setattr(F, 'act', dict(fail=True)), setattr(F, 'jaw_t', None), F._act_end(20.0, True))[2] for _ in range(50)), 'no second eat inside 90 s')
# mimic_tick end-to-end: start → act → end
F.jaw_t = None; F.jaw = None; F.act = None; F.mimic = None; F.next_mimic = 0; F.arc = None
F.mimic_tick(100.0, True); check(F.act is not None and F.mimic_on(100.1), f'mimic_tick starts an act ({F.act["name"]})')
# desk side: every act drawn, failed acts ignore the beat
d.form_on = lambda: True; sn = dict(level=0.5, kick=0.9, snare=0, hat=0)
bad = []
for pick in ZH.ACT_POOL:
    kind, name = pick.split(':')
    for fail in (False, True):
        F.act = dict(kind=kind, name=name, fail=fail, t0=0.0, end=6.0, seed=0.3)
        mode, var, sn2 = d.mimic_mode('groove', '', sn, 1.0)
        if kind == 'd' and mode != name: bad.append(pick)
        for tt in (0.2, 1.5, 3.0, 5.5):
            r, ov, hide = d.dance.draw(ZD.build(st), mode, var, dict(sn2, progress=0.5), 100 + tt, ZD.C['G'], {})
            r, ov, hide = d.mimic_after(r, ov, hide, tt, st, sn2)
            if not hide and (not r or not finite(r)): bad.append((pick, tt))
check(not bad, f'desk draws all 23 acts × fail / not × 4 moments ({bad[:3]})')
F.act = dict(kind='d', name='bolero', fail=True, t0=0, end=6, seed=0.1); _, _, s1 = d.mimic_mode('mosh', '', dict(sn, kick=0.95), 2.0)
check(s1['level'] == 0.2 and s1['kick'] < 0.5, 'ПРОВАЛ on a hard song: it hears a calm beat')
print(f'HUNT OK {ok}')
