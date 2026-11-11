"""v56 d39 + h22: ПОДДЕЛКА's pieces on other songs. Real desk + hurt parts in Xvfb, fake clock.
Blast styles in turns on hard songs (no КОНФЕТТИ on ДЕЛИКАТЕС), ears / sparkles / heart on ПРИМАНКА songs, light dust + rain on
loud parts, nothing doubled on an edit, the switch, the menu."""
import os, sys, time, math, random
H = os.path.expanduser('~'); P = f'{H}/.local/lib/zarya/desk'
g = {'__name__': 'desk_test', '__file__': f'{H}/.local/bin/zarya-daemon-desk'}
for f in sorted(x for x in os.listdir(P) if x.endswith('.py')):
    exec(compile(open(f'{P}/{f}', encoding='utf-8').read(), f'{P}/{f}', 'exec'), g)
d = g['Demon'](); ZH = g['ZH']; ZD = g['ZD']; ok = []
def check(name, cond):
    print(('  ОК ' if cond else '  ✕  ') + name); ok.append(bool(cond))
LOG = []; g0 = g['log']
def mylog(m): LOG.append(m); g0(m)
g['log'] = mylog; ZH.set_logger(mylog)
def finite(rs): return all(all(math.isfinite(v) for v in r[:4]) and isinstance(r[4], str) and r[4].startswith('#') for r in rs)
check(f'versions {g["VERSION"]} / {ZH.VERSION}', g['VERSION'] == 'd39' and ZH.VERSION == 'h22')
F = d.form; st = d.state(); idle = ZD.build(dict(st, mode='idle')); now0 = 50000.0
F.start(now0, 0, 'test', song='x')
SW, BL, BO = ZH.SWEET, ZH.BLUSH, ZH.BONE

def blasts(n, t0, **song):
    F.song(t0, 'hard-' + str(t0), **song); F.set_hard(True); kinds = []; frames = []
    t = t0
    for b in range(n):
        F.arc = None; F.preview(t); LOG.clear()
        for i in range(int(6.5 * 30)):
            t += 1 / 30; out, ov = F.frame([r[:] for r in idle], None, t, music=False); assert finite(out); frames.append((F.arc and F.arc['ph'], out))
            if F.arc is None: break
        kinds += [m.split('style: ')[1] for m in LOG if 'style:' in m]
    return kinds, frames
k, fr = blasts(8, now0)
check(f'hard song: blast styles in turns {k}', len(set(k[:4])) == 4 and k[:4] == k[4:8])
check('КОНФЕТТИ pieces fly on a hard song', any(sum(1 for c in o if c[4] in (SW, BO, BL) and c[2] == 0.5) >= 15 for ph, o in fr))
check('ПЕРЕМОТКА leaves a wrong pixel', len(F.sp['wrong']) >= 1)
k2, _ = blasts(6, now0 + 1000, dg=True)
check(f'ДЕЛИКАТЕС: no КОНФЕТТИ {k2}', 'КОНФЕТТИ' not in k2 and len(set(k2)) == 3)

# ПРИМАНКА: ears in the chorus, sparkles, the heart when the mask is off
SEEN = set(); NP = dict(dust=0, rain=0)
def play(t0, secs, ctx, lure=False, level=0.8, key='s'):
    F.song(t0, key + str(t0), lure=lure); F.arc = None; F.det_max = 0; F.hard = False; res = []; SEEN.clear(); NP.update(dust=0, rain=0)
    for i in range(int(secs * 30)):
        t = t0 + i / 30; per = 0.4
        sn = dict(level=level, kick=1.0 if i % 12 == 0 else 0.0, hat=1.0 if i % 6 == 3 else 0.0, snare=0.0)
        out, ov = F.frame([r[:] for r in idle], sn, t, music=True, ctx=ctx, pos=30 + i / 30, lyr=None); assert finite(out); res.append(out)
        sp_ = getattr(F, 'sp', None) or {}
        for z in sp_.get('spark', []): SEEN.add((z['t'], z['x'], z['y']))
        NP['dust'] = max(NP['dust'], len(sp_.get('dust', []))); NP['rain'] = max(NP['rain'], len(sp_.get('rain', [])))     # the particle lists, not colours (ПАУК feet are red half-cells too)
    return res
dark = dict(chorus=True, voice=0.7, aggr=0.8)
fr = play(now0 + 2000, 6, dark, lure=True)
ears = sum(1 for o in fr if any(c[4] == SW and c[2] == 1 and c[1] < ZD.OY for c in o))
heart = sum(1 for o in fr if sum(1 for c in o if c[4] == SW and c[2] == 0.7) >= 5)       # heart cells are 0.7 wide; ТИК moves it
spark = len(SEEN)
check(f'ПРИМАНКА dark chorus: ears {ears} / heart {heart} of {len(fr)} frames, {spark} sparkles from 30 hats', ears > 150 and heart > 100 and 3 <= spark <= 20)
cute = dict(chorus=True, voice=0.7, aggr=0.2)
fr = play(now0 + 3000, 4, cute, lure=True, level=0.5)
heart_c = sum(1 for o in fr if sum(1 for c in o if c[4] == SW and ZD.OY + 3 <= c[1] < ZD.OY + 6.5 and c[2] == 0.7) >= 5)
check(f'ПРИМАНКА cute part: the mask wins, no heart ({heart_c} frames)', heart_c == 0)
fr = play(now0 + 4000, 4, dark, lure=False, level=0.5)
check('a plain song: no ears, no heart, no sparkles', not any(c[4] in (SW, BL) for o in fr for c in o))
# ПЫЛЬ / СБОЙ
fr = play(now0 + 5000, 5, None, level=0.85)
isd = lambda c: c[4] in ZH.NC2_DUST and c[2] in (0.4, 0.6); isr = lambda c: c[4] == ZH.NC2_RAIN_HEAD and c[2] == 0.5
dmax, rmax = NP['dust'], NP['rain']
check(f'loud part of any song: dust up to {dmax}, rain up to {rmax}', dmax >= 8 and rmax >= 3)
fr = play(now0 + 6000, 9, None, level=0.3)
check(f'calm part: no dust left after 7 s ({len(F.sp["dust"])})', len(F.sp['dust']) == 0)
# lighter than an edit at the same loudness
F.song(now0 + 7000, 'nc'); F.forgery(now0 + 7000, dict(r=1.3, oartist='a', otitle='b')); F.nc['slow'] = False; F.nc['cut_t'] = now0 + 7000
nmax = 0; sp_before = id(getattr(F, 'sp', None))
for i in range(150):
    t = now0 + 7000 + i / 30; sn = dict(level=0.85, kick=1.0 if i % 12 == 0 else 0.0, hat=0.0, snare=0.0)
    out, ov = F.frame([r[:] for r in idle], sn, t, music=True, ctx=None, pos=40 + i / 30, lyr=None)
    nmax = max(nmax, len(F.nc['v2']['dust']) if F.nc.get('v2') else 0)
check(f'lighter than an edit at the same loudness: dust {dmax} (cap 30) vs {nmax} (cap 70), rain {rmax} (cap 5); the spread layer stays out of edits', dmax <= 30 and rmax <= 5 and nmax > 2 * dmax and id(getattr(F, 'sp', None)) == sp_before)
F.song(now0 + 8000, 'off')
# the switch through the desk tick
d.cfg['nc_spread'] = '0'; d.event_tick(time.time()); check('switch off: Form.spread False', F.spread is False)
fr = play(now0 + 9000, 3, None, level=0.85); check('switched off: no dust on a loud song', NP['dust'] == 0)
d.cfg['nc_spread'] = '1'; d.event_tick(time.time()); check('switch on again', F.spread is True)
from gi.repository import Gtk
d.form_on = lambda: True; m = Gtk.Menu(); d.anim_menu(m); labs = [x.get_label() or '' for x in m.get_children()]
check('menu: «ПОДДЕЛКА · its pieces on other songs ✓» at the end', labs[-1].startswith('   ПОДДЕЛКА · its pieces on other songs') and '✓' in labs[-1])
# the ▶ ПРИМАНКА preview gets ears + sparkles, no music
F.song(now0 + 9500, None); t0 = now0 + 9500; F.lure_preview(t0); n_e = n_s = 0
for i in range(int(14 * 30)):
    t = t0 + i / 30; out, ov = F.frame([r[:] for r in idle], None, t, music=False); assert finite(out)
    n_e += any(c[4] == SW and c[2] == 1 and c[1] < ZD.OY for c in out); n_s += any(c[4] in (SW, BL) and c[2] == 0.5 for c in out)
check(f'▶ ПРИМАНКА preview: ears {n_e}, sparkles {n_s} frames', n_e > 300 and n_s > 30)
print(f'SPREAD {"OK" if all(ok) else "FAIL"} {sum(ok)}/{len(ok)}')
sys.exit(0 if all(ok) else 1)
