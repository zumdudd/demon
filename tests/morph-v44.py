"""v44: СМЕНА (way in / way out by ritual) + ИГРА (game mode), on the real desk + hurt parts."""
import os, sys, time, math
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
# ---- way in: every Form.start asks for the burst
t = 1000.0; d._demon_last = idle; d.morph = None; d._was_form = False
F.start(time.time(), 45, 'test')
check(F.morph_req is not None, 'Form.start asks for СМЕНА in')
phases, n, done_at = [], 0, None
while n < 400:
    r, ov, hide = d.morph_apply([list(x) for x in idle], [], False, t, st)
    m = d.morph
    if m is None: done_at = t; break
    ph = 'infect' if m.T1 is None else 'burst' if t - m.T1 < 0.18 else 'hang' if m.T2 is None else 'assemble'
    if not phases or phases[-1] != ph: phases.append(ph)
    assert r and finite(r), (ph, r[:3])
    t = round(t + 1 / 30, 4); n += 1
check(phases == ['infect', 'burst', 'hang', 'assemble'], f'way in phases {phases}')
check(done_at is not None and done_at - 1000 < 2.2, f'way in done in {done_at - 1000:.2f} s (no music)')

# kick-led: burst lands on the first kick after 0.40 s
from types import SimpleNamespace
mk = ZH.Morph('in', idle, *ZH.form_cells(F, idle, 0)[:1], t0=0.0, eyes=ZH.form_cells(F, idle, 0)[1], music=True)
tt = 0.0; kick = lambda x: 1.0 if abs(x - 0.52) < 0.02 else 0.0
while mk.T1 is None and tt < 1: mk.frame(tt, dict(kick=kick(tt))); tt = round(tt + 0.01, 3)
check(abs(mk.T1 - 0.51) < 0.03, f'burst on the kick (T1 {mk.T1:.2f} s, kick at 0.52)')
b, e = ZH.form_cells(F, idle, 0)
check(len(b) > 40 and len(e) >= 1, f'ПОДМЕНЫШ clean body {len(b)} cells + {len(e)} eye cells')

# ---- way out: each ritual runs to the end, cells finite, never empty for long
for rit in ('summon', 'cult', 'pagan', 'none', 'plain'):
    mo = ZH.Morph('out', b, None, 0.0, eyes=e, rit=rit, music=False, eye_col=ZD.C['G'])
    tt, empty, end = 0.0, 0, None
    while tt < 10:
        r, ov, dn = mo.frame(tt, {}, idle)
        assert finite(r), rit
        if not r: empty += 1
        if dn: end = tt; break
        tt = round(tt + 1 / 30, 4)
    lim = dict(summon=6.5, cult=4.6, pagan=6.0, none=2.6, plain=2.0)[rit]
    check(end is not None and end < lim and empty < (20 if rit == 'none' else 12), f'way out {ZH.MORPH_RU[rit]}: done in {end:.2f} s (< {lim}), empty frames {empty}')

# ---- which ritual: by the song
class M:
    def __init__(s, real, art, title='X', playing=True): s.r = real; s.a = art; s.t = title; s.p = playing
    def __getattr__(s, k): return getattr(s.r, k)
    def artist(s, r=None): return s.a
    def artists(s, r=None): return [s.a]
    def title(s, r=None): return s.t
    def playing(s): return s.p
    def position(s): return 60.0
real = d.music
def ritual_for(art, tags, why='', playing=True, hard=False, deli=False):
    d.music = M(real, art, playing=playing); d.mkey = ('spotify', art) if playing else None; d.info = dict(tags=tags); d.srule = {}
    d.cur_mode = lambda: (('mosh' if hard else 'groove'), '', ''); d.cur_weather = lambda: ('clear', '')
    d._exit_why = why; return d.exit_ritual()
check(ritual_for('Death Grips', [])[0] == 'cult', 'Death Grips (no tags) → КУЛЬТ')
check(ritual_for('Mayhem', [('black metal', 100)])[0] == 'summon', 'black metal → ПРИЗЫВ')
check(ritual_for('Slipknot', [('nu metal', 100), ('metal', 80)])[0] == 'summon', 'nu metal → ПРИЗЫВ')
check(ritual_for('Eluveitie', [('folk metal', 100)])[0] == 'pagan', 'folk metal → ЯЗЫЧЕСТВО')
check(ritual_for('Excision', [('dubstep', 100)], hard=True)[0] == 'none', 'dubstep (hard) → ЦИФРА')
check(ritual_for('Mac DeMarco', [('indie', 100)])[0] == 'plain', 'calm song, it left by itself → ГНИЛЬ')
r_ = ritual_for('Mac DeMarco', [('indie', 100)], why='you drove it out')[0]
check(r_ in ('summon', 'cult', 'pagan', 'none'), f'calm song but you drove it out → a ritual ({ZH.MORPH_RU[r_]})')
r_ = ritual_for('', [], why='you held it down', playing=False)[0]
check(r_ in ('summon', 'cult', 'pagan'), f'no song, you held it down → a ritual ({ZH.MORPH_RU[r_]})')
check(ritual_for('', [], why='the calm songs starved it', playing=False)[0] == 'plain', 'no song, starved → ГНИЛЬ')
d.music = real

# ---- Изгнать (force) starts the way out with the ritual, through draw's hook
d.morph = None; d._was_form = True; d.music = M(real, 'Death Grips'); d.mkey = ('s', 'dg'); d.info = dict(tags=[]); d.srule = {}
d.exorcise('you drove it out', force=True)
r, ov, hide = d.morph_apply([list(x) for x in idle], [], False, 2000.0, st)
check(d.morph is not None and d.morph.kind == 'out' and d.morph.rit == 'cult', 'Изгнать on Death Grips → way out КУЛЬТ starts')
d.music = real; d.morph = None

# ---- the lightning plays the burst on its final strike
Strike = ZH.EVENTS['descend']; geo = SimpleNamespace(x=0, y=0, width=1280, height=720)
pet = d.pet_geo(geo); pet['form'] = F
s = Strike(1280, 720, pet, 'test'); s.hits = [(1.5, s.src[0], 0.1), (2.4, s.src[0], 0.2), (3.3, s.src[0], 0.3)]; s.final = 4.2; s.level = 1.0
img = g['cairo'].ImageSurface(g['cairo'].FORMAT_ARGB32, 1280, 720); cr = g['cairo'].Context(img)
for el in (4.25, 4.35, 4.5, 4.8, 5.2, 5.6): s.draw(cr, el)
check(getattr(s, 'morph', None) is not None and F.morph_skip > 0, 'СОШЕСТВИЕ: final strike bursts him (morph made, desk burst skipped)')
F.start(time.time(), 45, 'lightning'); check(F.morph_req is None, 'Form.start after the lightning: no second burst')

# ---- ИГРА
calls = []
d.hide = lambda: calls.append('hide'); d.show_all = lambda: calls.append('show'); d.place = lambda: None
d.scan_windows = lambda: None; d.steam_name = lambda a: 'Dota 2'
d.fullscreen_active = lambda: (True, 'WM_CLASS(STRING) = "steam_app_570", "dota2"'); d.steam_game = 'steam_app_570'
d.hidden_fs = False; d.slow()
check(d.hidden_fs and getattr(d, 'gaming', False) and 'hide' not in calls, 'game: he stays (not hidden), gaming on')
held = []; d.hold_tick = lambda now, mask: held.append(mask)
d.tick(); check(held and held[-1] == 0, 'game: tick still runs, the hold sees no button')
d.ghost_tick(time.time()); check(not d.ghost_on, 'game: no ghost fade')
d.fullscreen_active = lambda: (False, ''); d.steam_game = None; d.slow()
check(not d.gaming and not d.hidden_fs and 'show' not in calls, 'game over: input back, no re-show needed')
d.fullscreen_active = lambda: (True, 'WM_CLASS(STRING) = "Navigator", "firefox"'); d.slow()
check('hide' in calls and not getattr(d, 'gaming', False), 'fullscreen video: hidden like before')
d.fullscreen_active = lambda: (False, ''); d.slow(); check('show' in calls, 'video gone: shown again')
print(f'MORPH OK ({ok} checks)')
