"""v36: old Reactions (d27) vs new (d28, director gate) on scripted ear input, same dice. Decisions must match exactly."""
import math, random, sys, re, json
def reactions_src(path):
    s = open(path + '/07-reactions-main.py', encoding='utf-8').read(); return s[:s.index('# <<< d16 reactions')]
def load(path, extra=''):
    starts = []
    ns = dict(math=math, random=random, REACT_GAP=75, OX=3, OY=4, FLAME=['#000']*5, CHAR='#111', time=__import__('time'),
              log=lambda m: starts.append(m) if m.startswith('react:') else None)
    if extra: exec(extra, ns)
    exec(reactions_src(path), ns); return ns, starts
BASE = sys.argv[1]; NEW = sys.argv[2]
bus_src = open(f'{NEW}/00a-bus-director.py', encoding='utf-8').read()
bus_src = bus_src[bus_src.index('class Director'):bus_src.index('DIRECTOR = Director()')] + 'DIRECTOR = Director()\n'
skips = []
pre = ('BUS = type("B", (), {"emit": lambda self, *a, **k: SKIPS.append((a, k))})()\n_log_file = lambda m: None\n' + bus_src)
def scenario(seed):
    r = random.Random(seed); t = 1000.0; out = []
    for song in range(6):
        epic = r.random() < 0.4; soft = (not epic) and r.random() < 0.3; L = r.uniform(120, 300); w = r.choice([1.0, 0.5, 2.0])
        for i in range(int(L * 10)):
            t += 0.1; p = i / (L * 10)
            sec = i / 10; lvl = 0.3 + 0.6 * abs(math.sin(sec / 7)) + r.uniform(-0.1, 0.1)
            drop_t = t if r.random() < 0.004 else -99
            sn = dict(level=lvl, hat=r.random(), drop_t=drop_t, max_hold=max(0, (lvl - 0.8) * 20 + r.uniform(-1, 1)),
                      excite=r.random(), build=r.random())
            vol = r.random() < 0.002
            out.append((song, epic, soft, w, t, sn, p, vol))
    return out
bad = 0; total = 0
for seed in range(40):
    sc = scenario(seed)
    res = []
    for path, extra in ((BASE, ''), (NEW, pre)):
        S = []; ns, starts = load(path, extra); ns['SKIPS'] = S
        R = ns['Reactions'](); R.rng = random.Random(seed * 7); R.gap_mult = 1.0
        rets = []; key = None
        for song, epic, soft, w, t, sn, p, vol in sc:
            if song != key: key = song; R.track_change(t, key); R.gap_mult = w
            if vol: R.vol_up = t
            rets.append(R.tick(t, sn, epic, soft, p))
        res.append((starts, [x for x in rets if x], len(S)))
    total += len(res[0][0])
    if res[0][:2] != res[1][:2]: bad += 1; print('MISMATCH seed', seed)
print(f'seeds 40, reactions fired {total}, skips noted by d28 {res[1][2]} (last seed), mismatches {bad}')
sys.exit(1 if bad else 0)
