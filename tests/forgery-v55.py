"""v55 d38 + h21: ПОДДЕЛКА + НЕТЕРПЕНИЕ + ПОДДЕЛКА 2 (blasts, speed, pixels, creepy kawaii). Real desk + hurt parts in Xvfb, a fake song clock (no window loop).
Detection, the original's length, РАЗГОН, the speed layer, ОРИГИНАЛ, СЛЕД, ПОДПИСЬ, ОБРЫВ + ТОН, НЕ ДОСЛУШАЛ, ВПЕРЕДИ ×r,
УКРАДЕННОЕ ВРЕМЯ, the preview, the menu, the shout lift on a real cairo surface."""
import os, sys, time, json, math, random
H = os.path.expanduser('~'); P = f'{H}/.local/lib/zarya/desk'
g = {'__name__': 'desk_test', '__file__': f'{H}/.local/bin/zarya-daemon-desk'}
for f in sorted(x for x in os.listdir(P) if x.endswith('.py')):
    exec(compile(open(f'{P}/{f}', encoding='utf-8').read(), f'{P}/{f}', 'exec'), g)
d = g['Demon'](); ZH = g['ZH']; ZM = g['ZM']; ZD = g['ZD']; ok = []
def check(name, cond):
    print(('  ОК ' if cond else '  ✕  ') + name); ok.append(bool(cond))
LOG = []; g0 = g['log']
def mylog(m): LOG.append(m); g0(m)
g['log'] = mylog; ZH.set_logger(mylog)
def finite(rs): return all(all(math.isfinite(v) for v in r[:4]) and isinstance(r[4], str) and r[4].startswith('#') for r in rs)
check(f'versions {g["VERSION"]} / {ZH.VERSION}', g['VERSION'] in ('d38', 'd39') and ZH.VERSION in ('h21', 'h22'))

# ---- 1. who is an edit
det = g['nc_detect']
c = det(['NightcoreReality'], 'Nightcore - Mili - world.execute(me);')
check(f'channel "NightcoreReality" + "Nightcore - Mili - …" → {c and (c["oartist"], c["otitle"])}', c and c['oartist'] == 'Mili' and c['otitle'] == 'world.execute(me);')
c = det(['Kanaria'], 'KING (Sped Up)'); check(f'"KING (Sped Up)" → {c and (c["oartist"], c["otitle"])}', c and c['oartist'] == 'Kanaria' and c['otitle'] == 'KING')
c = det(['Sewerslvt'], 'Pretty Cvnt - sped up version'); check(f'"- sped up version" → {c and c["otitle"]}', c and c['otitle'] == 'Pretty Cvnt')
c = det(['Excision'], 'X Rated (Nightstep)'); check('nightstep marked', c and c['nightstep'] and c['otitle'] == 'X Rated')
c = det(['Nightcore'], 'Dam Dadi Doo'); check(f'the duo itself: no original artist, title kept ({c and c["otitle"]})', c and c['oartist'] == '' and c['otitle'] == 'Dam Dadi Doo')
c = det(['DJ X'], 'Song', 'Nightcore Hits Vol. 3'); check('album "Nightcore Hits" counts', bool(c))
check('"slowed + reverb" is not one', det(['x'], 'Song (sped up + slowed + reverb)') is None)
check('a plain song is not one', det(['Mili'], 'world.execute(me);') is None and det(['Utsu-P'], 'Hi High') is None)

# ---- 2. the original's length
def fake_get(url, params=None, headers=None, timeout=7):
    if 'musicbrainz' in url:
        return dict(recordings=[dict(score=100, title='world.execute(me);', length=192000),
                                dict(score=100, title='world.execute(me); (Nightcore)', length=150000),
                                dict(score=95, title='world.execute (me);', length=194000),
                                dict(score=60, title='world.execute(me);', length=100000),
                                dict(score=100, title='world.execute(me);', length=420000)])
    return dict(track=dict(duration='0'))
_g0 = ZM._get; ZM._get = fake_get
o, src = g['nc_lookup']('Mili', 'world.execute(me);', 150.0)
check(f'MusicBrainz: median of the real ones, edits / low score / out of range skipped → {o} s ({src})', o == 193.0 and src.startswith('MusicBrainz'))
ZM._get = lambda *a, **k: dict(recordings=[])
o, src = g['nc_lookup']('Mili', 'x', 150.0); check(f'no match → None ({src})', o is None and 'no match' in src)
ZM._get = _g0

# ---- 3. a full edit through ПОДМЕНЫШ (fake clock, 30 fps)
F = d.form; now0 = 10000.0
F.start(now0, 0, 'test', song='k1'); F.song(now0, 'k1')
F.forgery(now0, dict(r=1.30, src='test', oartist='Mili', otitle='world.execute(me);', orig_len=195.0, edit_len=150.0))
st = d.state(); idle = ZD.build(dict(st, mode='idle'))
BPM = 170; per = 60 / BPM
frames = []; t = now0; outs = []; held_ids = set(); slow_changes = 0; prev_out = None
ghost_first = None; lost_at = {}; trail_n = 0; jump_n = 0; calm_diffs = 0; calm_frames = 0; shouts = []
for i in range(int(150 * 30)):
    t = round(now0 + i / 30, 4); pos = t - now0
    calm = 60 <= pos < 75
    kbeat = int(pos / per); hbeat = int(pos / (per / 2))
    kick = 1.0 if (i == 0 or int((t - 1 / 30 - now0) / per) != kbeat) and not calm else 0.0
    hat = 1.0 if (i == 0 or int((t - 1 / 30 - now0) / (per / 2)) != hbeat) and not calm else 0.0
    sn = dict(level=0.2 if calm else 0.82, kick=kick, snare=0.0, hat=hat)
    if pos in (40.0, 41.0, 42.0, 43.0): F.line = ('СЛЫШИШЬ.', t + 0.5)
    out, ov = F.frame([r[:] for r in idle], sn, t, music=True, ctx=None, pos=pos, lyr=None)
    assert finite(out), pos
    nc = F.nc
    if nc['slow'] and prev_out is not None and out is not prev_out: slow_changes += 1
    prev_out = out
    if any(c[4] == ZH.NC_GHOST for c in out) and ghost_first is None: ghost_first = pos
    lost_at[nc['lost']] = lost_at.get(nc['lost'], pos)
    trail_n += any(c[4] in ZH.NC_TRAIL[1:] for c in out)
    if calm and 62 < pos < 74:
        calm_frames += 1
        calm_diffs += outs[-1] != [tuple(c) for c in out if c[4] != ZH.NC_GHOST] if outs else 0
    outs.append([tuple(c) for c in out if c[4] != ZH.NC_GHOST]); outs = outs[-2:]
    for o_ in ov:
        if o_[0] == 'shout' and 'СЛЫШ' in o_[1][0]: shouts.append((pos, o_[1][0], o_[1][5] if len(o_[1]) > 5 else 0))
nc = F.nc
cut = next((m for m in LOG if 'РАЗГОН' in m), '')
check(f'РАЗГОН: cut on a kick after 2 bars ({cut.split("(")[-1] if cut else "none"})', '8 kicks' in cut or '9 kicks' in cut)
check(f'РАЗГОН: 4 snaps a second while slow ({slow_changes} changes in {8 / BPM * 60:.1f} s)', 0 < slow_changes <= 4 * (8 * per) + 2)
check(f'ОРИГИНАЛ appears after the cut ({ghost_first:.2f} s)', ghost_first is not None and ghost_first >= 7 * per - 0.05)
lines = [m for m in LOG if 'ОРИГИНАЛ lines up' in m]
check(f'ОРИГИНАЛ lines up {len(lines)} times, rows lost at {sorted((k, round(v)) for k, v in lost_at.items())[:11]}', len(lines) >= 6)
check(f'ОРИГИНАЛ gone by 85 % of the song (at {round(lost_at.get(10, 999))} s of 150)', lost_at.get(10, 999) <= 0.9 * 150 and any('ОРИГИНАЛ is gone' in m for m in LOG))
check(f'СЛЕД: trails in {trail_n} loud frames (3 copies at ×1.30)', trail_n > 1000)
check(f'ПРЫЖОК: {nc["jumps"]} teleports', 50 < nc['jumps'])
check(f'НЕ СТОИТ: it moves in {calm_diffs}/{calm_frames} calm frames', calm_frames and calm_diffs >= 0.3 * calm_frames)
lifts = [s[2] for s in shouts]; texts = {s[1] for s in shouts}
check(f'ОБРЫВ: «СЛЫШИШЬ.» → {sorted(texts)[:3]}', all(not x.startswith('СЛЫШИШЬ') for x in texts) and any(x.startswith('СЛЫШ') for x in texts))
check(f'ТОН: each repeat sits higher {sorted(set(lifts))}', sorted(set(lifts))[:4] == [0, 2, 4, 6])
# ВПЕРЕДИ ×r: lead before the real kick
def leads(r):
    F.song(now0, 'k2'); F.nc = None
    if r: F.forgery(now0, dict(r=r, oartist='a', otitle='b')); F.nc['slow'] = False
    F.kicks = []; F.pre = None; F.pre_for = None; F.kprev = 0; out = []; last_pre = None
    for i in range(30 * 40):
        t = now0 + i / 240; k = 1.0 if i % int(240 * 0.5) == 0 else 0.0
        F._ahead(dict(kick=k), t)
        if F.pre is not None and F.pre != last_pre:
            last_pre = F.pre; nxt = math.ceil((F.pre - now0) / 0.5) * 0.5 + now0; out.append(nxt - F.pre)
    return sum(out) / len(out) if out else 0
l0, l1 = leads(None), leads(1.3)
check(f'ВПЕРЕДИ ×1.30: {l0 * 1000:.0f} ms → {l1 * 1000:.0f} ms early', 0.03 <= l0 <= 0.10 and l1 > l0 * 1.15 and l1 <= 0.155)
# НЕ ДОСЛУШАЛ + the next act sooner
F.song(now0, 'k3'); F.forgery(now0, dict(r=1.30, oartist='a', otitle='b')); F.nc['slow'] = False; F.rng = random.Random(3)
durs = []; cuts = 0
for k in range(300):
    a = F._act_pick(now0, True, fail=False); durs.append(a['end'] - a['t0']); cuts += bool(a.get('cut'))
check(f'НЕ ДОСЛУШАЛ: acts ≤ {max(durs):.1f} s (was 4-8), {cuts}/300 dropped halfway (≈ 0.6)', max(durs) <= 8 / 1.3 + 0.01 and 140 <= cuts <= 220)
F.mimic = None; F.act = None; F.arc = None; F.next_mimic = now0 - 1; F.mimic_tick(now0, True); F.mimic_tick(F.mimic + 0.01, True)
gap = F.next_mimic - (F.mimic or now0)
check(f'the next act comes r times sooner (gap {F.next_mimic - now0:.1f} s, was 45-80 after the act)', F.next_mimic - now0 < 80 / 1.3 + 8)
# no song: nothing
F.song(now0, 'k4'); F.forgery(now0, dict(r=1.3, oartist='a', otitle='b')); F.nc['slow'] = False; F.nc['cut_t'] = now0
out, ov = F.frame([r[:] for r in idle], None, now0 + 5, music=False)
check('no music: no ghost, no trails', not any(c[4] in (ZH.NC_GHOST,) + ZH.NC_TRAIL for c in out))
# УКРАДЕННОЕ ВРЕМЯ
F.song(now0, 'k5'); F.forgery(now0, dict(r=1.3, oartist='a', otitle='b', orig_len=195.0, edit_len=150.0)); F.nc['maxpos'] = 120
h0 = F.hunger(); F.song(now0 + 150, 'k6')
check(f'УКРАДЕННОЕ ВРЕМЯ: «{F.line[0] if F.line else ""}», hunger {h0:.2f} → {F.hunger():.2f}, ПОДДЕЛКА over', F.line and F.line[0] == '−0:45.' and F.hunger() > h0 and F.nc is None)
F.forgery(now0, dict(r=1.3, oartist='a', otitle='b', orig_len=195.0, edit_len=150.0)); F.nc['maxpos'] = 40; F.line = None; F.song(now0 + 50, 'k7')
check('skipped before half: no stolen time', F.line is None)
# ПОДПИСЬ (real clock: the label reads time.time())
F.forgery(time.time(), dict(r=1.30, oartist='Mili', otitle='x')); F.nc['slow'] = False; F.nc['sig_t0'] = time.time()
seen = []
for k in range(14):
    seen.append(F.label().split(' · ')[0]); time.sleep(0.1)
check(f'ПОДПИСЬ: {seen[0]!r} → {seen[4]!r} → {seen[-1]!r}', seen[0].startswith('Ж') or seen[0].startswith('MILI') or 'ILI' in seen[0])
check('ПОДПИСЬ ends as ПОДМЕНЫШ with ×1.30', seen[-1] == 'ПОДМЕНЫШ' and F.label().endswith('×1.30'))
F.song(time.time(), 'k8')

# ---- 4. the preview (no song playing: the desk passes music=False)
LOG.clear(); tp = 20000.0; F.forgery_preview(tp, 'Mili'); pv = []
for i in range(int(23.5 * 30)):
    t = tp + i / 30
    out, ov = F.frame([r[:] for r in idle], None, t, music=False)
    assert finite(out)
    pv.append((t - tp, out, ov))
ghost_t = next((e for e, o, _ in pv if any(c[4] == ZH.NC_GHOST for c in o)), None)
sh = [(round(e, 1), a[1][0], a[1][5] if len(a[1]) > 5 else 0) for e, _, ov in pv for a in ov if a[0] == 'shout']
check(f'preview: РАЗГОН then ghost from {ghost_t:.1f} s', ghost_t is not None and 2.5 < ghost_t < 5)
PV = pv; PVLOG = list(LOG)
check(f'preview: 2 line-ups ({sum("lines up" in m for m in LOG)})', sum('lines up' in m for m in LOG) == 2)
check(f'preview: shouts cut and rising {sorted({(x[1], x[2]) for x in sh if "СЛЫШ" in x[1]})}', {x[2] for x in sh if 'СЛЫШ' in x[1]} >= {0, 2, 4})
print('   shouts seen:', sorted({x[1] for x in sh if 'СЛЫШ' not in x[1]}));
check('preview: «×1.30» at the cut and «−0:45.» at the end', any(x[1] == '×1.30' for x in sh) and any(x[1] == '−0:45.' for x in sh))
check('preview ends by itself at 22.6 s', F.nc is None and any('preview over' in m for m in LOG))


# ---- 4b. v55 (h21): the 12
cols = lambda o: {c[4] for c in o}
bl = [m for m in PVLOG if 'ДЕТОНАЦИЯ' in m and '×' in m]
check(f'preview: three blasts {[m.split("ДЕТОНАЦИЯ ")[1] for m in bl]}', [m.split('ДЕТОНАЦИЯ ')[1].split(' ')[0] for m in bl] == ['ПЕРЕМОТКА', 'КОНФЕТТИ', 'ПИТЧ'])
check('ПЕРЕМОТКА: rebuilt with a pixel in the wrong place', any('one pixel in the wrong place' in m for m in PVLOG))
ears = [e for e, o, _ in PV if 3.6 < e < 6.4 and any(c[4] == ZH.SWEET and c[2] == 1 and c[1] < ZD.OY for c in o)]
check(f'УШКИ: pink inner ears above the head in the chorus ({len(ears)} frames)', len(ears) > 40)
noear = [e for e, o, _ in PV if 6.6 < e < 8.8 and any(c[4] == ZH.SWEET and c[2] == 1 and c[1] < ZD.OY - 1.5 for c in o)]
check('УШКИ off after the chorus', len(noear) == 0)
heart = [e for e, o, _ in PV if 6.3 < e < 7.9 and sum(1 for c in o if c[4] == ZH.SWEET and ZD.OY + 3 <= c[1] < ZD.OY + 7) >= 5]
check(f'СЕРДЕЧКО: heart eye while it sings ({len(heart)} frames)', len(heart) > 20)
crack = [e for e, o, _ in PV if 8.0 <= e < 8.25 and any(c[4] == ZH.RED and c[3] == 2.0 and c[2] == 0.6 for c in o)]
check('СЕРДЕЧКО cracks on the hard hit: the slit shows', len(crack) >= 3)
sparks = sum(1 for e, o, _ in PV if any(c[4] in (ZH.SWEET, ZH.BLUSH) and c[2] == 0.5 for c in o))
check(f'ЗВЁЗДОЧКИ pop ({sparks} frames)', sparks > 30)
dust = [sum(1 for c in o if c[4] in ZH.NC2_DUST) for e, o, _ in PV if 5 < e < 8]
rain = [sum(1 for c in o if c[4] == ZH.NC2_RAIN_HEAD and c[2] == 0.5) for e, o, _ in PV if 5 < e < 8]
check(f'ПЫЛЬ: up to {max(dust)} dust pixels; СБОЙ: up to {max(rain)} drops', max(dust) >= 20 and max(rain) >= 4)
check(f'pixels reach high in his window (top {min(c[1] for e, o, _ in PV for c in o):.1f} cells)', min(c[1] for e, o, _ in PV for c in o) < ZD.OY - 8)
check('ХЛОПОК fired', any('ХЛОПОК' in m for m in PVLOG))
conf_hearts = [e for e, o, _ in PV if 13.2 < e < 15 and sum(1 for c in o if c[4] in (ZH.SWEET, ZH.BONE, ZH.BLUSH) and c[2] == 0.5) >= 20]
check(f'КОНФЕТТИ in the air ({len(conf_hearts)} frames)', len(conf_hearts) > 10)
check('ПЕРЕГРУЗ: loud frames held', any('ПЕРЕГРУЗ' in m for m in PVLOG))
check(f'ПОЛОСЫ: streaks after jumps', sum(1 for e, o, _ in PV if any(c[4] == ZH.NC2_STREAK for c in o)) > 5)
check('every preview frame finite', all(finite(o) for e, o, _ in PV))
# ПИТЧ: shards fly in strips (rows alternate sides, upper rows faster)
F.song(now0, 'p'); F.forgery(now0, dict(r=1.30, oartist='a', otitle='b')); F.nc['slow'] = False; F.nc['cut_t'] = now0
F.frame([r[:] for r in idle], dict(level=0.8, kick=1.0), now0 + 1, music=True)
F.nc['v2']['force'] = 'pitch'; F.arc = dict(ph='soul', t=now0, at=None, lead=0.6, power=2.7, pv=True, k=1.0); F._boom(now0 + 1, F.arc, 0.9)
rows = {}
for s_ in F.shards: rows.setdefault(round(s_[11] - ZD.OY), []).append(s_[6])
sides = {k: (1 if sum(v) > 0 else -1) for k, v in rows.items()}
spd = {k: sum(abs(x) for x in v) / len(v) for k, v in rows.items()}
ks = sorted(spd); check(f'ПИТЧ: rows alternate sides, the top row faster ({spd[ks[0]]:.0f} vs {spd[ks[-1]]:.0f} cells/s)', len(set(sides.values())) == 2 and spd[ks[0]] > spd[ks[-1]] * 1.5)
# БОЛЬШЕ ВЗРЫВОВ
F.song(now0, 'b'); F.set_hard(False, True); F.forgery(now0, dict(r=1.33, oartist='a', otitle='b')); F.nc['slow'] = False
F.set_hard(False, True); check(f'БОЛЬШЕ ВЗРЫВОВ: a soft-looking edit at ×1.33 → hard, ≤ {F.det_max} blasts', F.hard and F.det_max == 3 and not F.drop_only)
F.song(now0, 'b2'); F.forgery(now0, dict(r=1.2, oartist='a', otitle='b')); F.nc['slow'] = False; F.set_hard(False); check(f'×1.20 → ≤ {F.det_max}', F.det_max == 2)
F.song(now0, 'b3'); F.set_hard(False, True); check('a normal song is untouched', not F.hard and F.det_max == 0)

# ---- 5. the desk: menu, tick, cache, the shout lift on cairo
from gi.repository import Gtk, GLib
import cairo
d.form_on = lambda: True
m = Gtk.Menu(); d.anim_menu(m); labs = [k.get_label() or '' for k in m.get_children()]
ip = next(n for n, l in enumerate(labs) if l.startswith('   ▶ ПРИМАНКА'))
check('menu: ▶ ПОДДЕЛКА right after ▶ ПРИМАНКА', labs[ip + 1].startswith('   ▶ ПОДДЕЛКА'))
check('menu: the toggle in On their own', any(l.startswith('   ПОДДЕЛКА · nightcore') and '✓' in l for l in labs[-3:]))      # v56: the spread switch comes after it
CLK = dict(artist='NightcoreReality', title='Nightcore - Mili - world.execute(me);', len=150.0)
class M:
    def __init__(s, real): s.r = real
    def __getattr__(s, k): return getattr(s.r, k)
    def active(s): return True
    def playing(s): return True
    def artist(s, r=None): return CLK['artist']
    def artists(s, r=None): return [CLK['artist']]
    def title(s, r=None): return CLK['title']
    def album(s, r=None): return ''
    def trackinfo(s, r=None): return ('t', '', CLK['len'])
d.music = M(d.music)
try: os.remove(g['NC_CACHE'])
except OSError: pass
ZM._get = fake_get
F.song(time.time(), 'nc-key-1'); d._nc_t = 0; d._nc_key = None; d.nc_tick(time.time())
check(f'tick: found it, guess ×1.25 first ({F.nc and F.nc["r"]})', F.nc is not None and F.nc['r'] == 1.25 and F.nc['oartist'] == 'Mili')
t_end = time.time() + 5
while time.time() < t_end and F.nc['src'] == 'guess': GLib.MainContext.default().iteration(False); time.sleep(0.02)
check(f'lookup in the background → ×{F.nc["r"]:.2f} ({F.nc["src"]})', abs(F.nc['r'] - 193 / 150) < 1e-6 and F.nc['src'].startswith('MusicBrainz'))
cache = json.load(open(g['NC_CACHE']))
check('cached by song key', cache.get('nc-key-1', {}).get('orig') == 193.0)
ZM._get = lambda *a, **k: (_ for _ in ()).throw(AssertionError('no second lookup'))
F.song(time.time(), 'nc-key-1'); d._nc_t = 0; d._nc_key = None; d.nc_tick(time.time())
check(f'second play: from the cache, no lookup (×{F.nc["r"]:.2f})', abs(F.nc['r'] - 193 / 150) < 1e-6)
d.cfg['forgery'] = '0'; d._nc_t = 0; d.nc_tick(time.time()); check('toggle off clears it', F.nc is None)
d.cfg['forgery'] = '1'; CLK['title'] = 'world.execute(me);'; CLK['artist'] = 'Mili'
F.song(time.time(), 'plain'); d._nc_t = 0; d.nc_tick(time.time()); check('a plain song: no ПОДДЕЛКА', F.nc is None)
ZM._get = _g0
def shout_top(lift):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, d.SW, d.WH); cr = cairo.Context(s)
    d.overlay(cr, 'shout', ('СЛЫШ', 1.0, 1.0, '#E4E0EA', '#FF5C8A', lift), d.U, d.WH - d.SH, False); s.flush()
    w, hgt, st_ = s.get_width(), s.get_height(), s.get_stride(); b = s.get_data()
    rows = [y for y in range(hgt) if any(b[y * st_ + x * 4 + 3] for x in range(0, w, 2))]
    return rows[0] if rows else None
y0, y2, y99 = shout_top(0), shout_top(2), shout_top(99)
check(f'ТОН on cairo: top row {y0} → {y2} (2 cells) → {y99} (capped, ≥ 0)', y0 is not None and y2 < y0 and y99 is not None and y99 >= 0 and y99 <= y2)
print(f'FORGERY {"OK" if all(ok) else "FAIL"} {sum(ok)}/{len(ok)}')
sys.exit(0 if all(ok) else 1)
