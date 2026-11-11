"""v52 d36: ЧАСТИ ПЕСНИ. Real desk parts in Xvfb; a cached zarya-mind reading with calm / loud parts; a fake song clock.
Checks the part class, ПОДМЕНЫШ's blasts / hunts / acts per part, the peek out and back, the ears' veto, toggles, menu line."""
import os, sys, time, json, hashlib, random
H = os.path.expanduser('~'); P = f'{H}/.local/lib/zarya/desk'
g = {'__name__': 'desk_test', '__file__': f'{H}/.local/bin/zarya-daemon-desk'}
for f in sorted(x for x in os.listdir(P) if x.endswith('.py')):
    exec(compile(open(f'{P}/{f}', encoding='utf-8').read(), f'{P}/{f}', 'exec'), g)
d = g['Demon'](); ZH = g['ZH']; ZJ = g['ZJ']; ok = []
def check(name, cond):
    print(('  ОК ' if cond else '  ✕  ') + name); ok.append(bool(cond))
LOG = []; g0 = g['log']
def mylog(m): LOG.append(m); g0(m)
g['log'] = mylog
CLK = {'pos': 10.0, 'title': 'hand crushed by a mallet', 'artist': '100 gecs'}
class M:
    def __init__(s, real): s.r = real
    def __getattr__(s, k): return getattr(s.r, k)
    def playing(s): return True
    def artist(s, r=None): return CLK['artist']
    def artists(s, r=None): return [CLK['artist']]
    def title(s, r=None): return CLK['title']
    def position(s): return CLK['pos']
    def trackinfo(s, r=None): return ('t', '', 180.0)
d.music = M(d.music); d.mkey = 'k1'
d.screen_fx = None; d.morph = None; d.stand = None
d.res_calm = lambda: (False, True)                                 # a hard song for the resident rules
d.dg_song = lambda: False
key = ZJ.key_of(CLK['artist'], CLK['title'])
mp = f'{H}/.local/share/zarya/mind/songs/{hashlib.md5(key.encode()).hexdigest()}.json'; os.makedirs(os.path.dirname(mp), exist_ok=True)
def reading(heard=True, secs=None):
    json.dump(dict(key=key, about='Someone sings sweetly about a crushed hand.', mood=['playful', 'dark'], dark_core=False, heard=heard,
                   sections=secs or [dict(at=0, feel='hype'), dict(at=40, feel='sad'), dict(at=95, feel='angry'), dict(at=150, feel='playful')]), open(mp, 'w'))
    d._mind_c = None
reading()
now = time.time(); F = d.form
F.start(now, 0, 'test', song=key); F.song(now, key)
check('ПОДМЕНЫШ in him for the test', d.form_on())
p = d.part_now(); check('0:10 → loud (hype)', p and p[0] == 'loud' and p[1] == 'hype')
CLK['pos'] = 50; p = d.part_now(); check('0:50 → calm (sad), 45 s of calm ahead', p and p[0] == 'calm' and abs(p[3] - 45) < 1)
CLK['pos'] = 160; p = d.part_now(); check('2:40 → playful = as before (None)', p and p[0] is None)
# the tick sets F.part_feel and logs once per part
d._part_t = 0; CLK['pos'] = 20; d.part_tick(now); d._part_t = 0; d.part_tick(now + 1.5)
check('tick: part_feel loud, logged once', F.part_feel == 'loud' and sum('ЧАСТЬ 0:00 hype (heard) → loud' in m for m in LOG) == 1)
# blasts: no new arc on a calm part
F.part_feel = 'calm'; F.arc = None; F.hard = True; F.smelled = False; F.det_max = 3; F.dets = 0; F.det_t = -1e9; F.drop_only = False
F._arc_tick(now, {}, None, 60.0, True, 0.9); check('calm part: no ЧУЕТ / no arc', F.arc is None)
F.part_feel = None; F._arc_tick(now, {}, None, 60.0, True, 0.9); check('no part: the arc starts as before (ЧУЕТ)', F.arc is not None)
F.part_feel = 'calm'; a = F.arc; F._arc_tick(now + 0.1, {}, None, 60.1, True, 0.9); check('calm part: an arc already running goes on', F.arc is a or F.arc is None)
F.arc = None
# hunts
F.rng = random.Random(1); n_calm = 0; n_loud = 0; n_none = 0
for k in range(400):
    F.jaw_song = None; F.song_key = f's{k}'; F.jaw = None; F.jaw_t = None
    F.part_feel = 'calm'; n_calm += bool(F._jaw_roll(now, True)); F.jaw = None; F.jaw_t = None; F.jaw_song = None
    F.part_feel = 'loud'; n_loud += bool(F._jaw_roll(now, True)); F.jaw = None; F.jaw_t = None; F.jaw_song = None
    F.part_feel = None; n_none += bool(F._jaw_roll(now, True)); F.jaw = None; F.jaw_t = None
check(f'ПАСТЬ: calm 0 · loud ~1/2 ({n_loud}) · none ~1/3 ({n_none})', n_calm == 0 and 160 <= n_loud <= 240 and 100 <= n_none <= 170 and abs(ZH.JAW_CHANCE - 1 / 3) < 1e-9)
# acts
F.part_feel = 'calm'; names = set(); fails = 0
for k in range(120):
    a = F._act_pick(now, True); names.add(f"{a['kind']}:{a['name']}"); fails += a['fail']
check('calm part: quiet acts only, never ПРОВАЛ', names <= set(g['PART_QUIET_ACTS']) and fails == 0 and len(names) >= 5)
bag = list(F.bag) if F.bag else None
F.part_feel = None; fails = sum(F._act_pick(now, True)['fail'] for _ in range(200))
check(f'no part: ПРОВАЛ as before (~1/4: {fails}/200)', 25 <= fails <= 80)
# peek: calm part with 45 s ahead → ДЕМОН out; back on the loud part ≥ 20 s later
LOG.clear(); F.arc = None; F.jaw = None; d._part_t = 0; CLK['pos'] = 50
d.part_tick(now + 10)
check('peek: ПОДМЕНЫШ leaves on the calm part (ГНИЛЬ way out)', not d.form_on() and d._res_away[0] == 'peek' and any('peek: a calm part (sad' in m for m in LOG))
d.res_tick(now + 11); check('resident rules leave the peek alone', not d.form_on())
CLK['pos'] = 96; d._part_t = 0; d.part_tick(now + 20)
check('loud part 10 s later: stays out (≥ 20 s rule)', not d.form_on())
d._part_t = 0; d.part_tick(now + 35)
check('loud part ≥ 20 s later: it comes back (Form.start)', d.form_on() and 'back for the loud part (angry)' in F.state().get('why', ''))
CLK['pos'] = 50; d._part_t = 0; LOG.clear(); d.part_tick(now + 40)
check('once per song: no second peek', d.form_on() and not any('peek:' in m for m in LOG))
# new song while peeking → handed to the resident rules
d._peek_done = None; d.mkey = 'k2'; d._part_t = 0; d.part_tick(now + 50)
check('second song peeks too', not d.form_on())
d.mkey = 'k3'; d._part_t = 0; d.part_tick(now + 55)
check('a new song while out: resident rules take over', d._res_away and d._res_away[0] == 'calm' and d._peek is None)
d.res_tick(now + 56); d._res_since = now + 40; d.res_tick(now + 70)
check('… and bring it back on a not-calm song', d.form_on())
# short calm part: no peek
d.mkey = 'k4'; reading(secs=[dict(at=0, feel='hype'), dict(at=40, feel='tender'), dict(at=55, feel='angry')]); CLK['pos'] = 45; d._part_t = 0; d.part_tick(now + 80)
check('calm part with 10 s ahead: no peek', d.form_on())
# toggles
d.cfg['mind_peek'] = '0'; d.mkey = 'k5'; reading(); CLK['pos'] = 50; d._part_t = 0; d.part_tick(now + 90)
check('mind_peek=0: no peek, still steered calm', d.form_on() and F.part_feel == 'calm')
d.cfg['mind_parts'] = '0'; d._part_t = 0; d.part_tick(now + 92); check('mind_parts=0: no steering', F.part_feel is None and d.part_now() is None)
d.cfg['mind_parts'] = '1'; d.cfg['mind_peek'] = '1'
# the ears' veto on a lyrics-only reading
reading(heard=False)
class B:
    map = {}; CUTE_STYLES = ()
    def section(s, pos): return dict(aggressive=0.82, energy=0.9)
    def hard(s): return False
    def lure(s): return None, ''
ob = d.brain; d.brain = B(); CLK['pos'] = 50
check('lyrics-only calm part vs a loud studied section: not calm', d.part_now()[0] is None)
reading(heard=True); check('heard reading: calm stands', d.part_now()[0] == 'calm')
d.brain = ob
# under 2 parts / no reading
reading(secs=[dict(at=0, feel='sad')]); check('one part only: no steering', d.part_now() is None)
os.remove(mp); d._mind_c = None; check('no reading: None', d.part_now() is None)
# menu line
reading(); CLK['pos'] = 50; ml = d.mind_menu_line(); check(f'menu line: heard + part now ({ml[-30:]})', ml.endswith('· heard · now sad'))
# version + toggles in the menu source
src = open(f'{P}/01-demon-1-sel-owner-paint-overlay.py', encoding='utf-8').read()
check('menu toggles mind_parts + mind_peek', "'mind_parts'" in src and "'mind_peek'" in src and g['VERSION'] >= 'd36' and ZH.VERSION == 'h19')
print(f'PARTS {sum(ok)}/{len(ok)}'); sys.exit(0 if all(ok) else 1)
