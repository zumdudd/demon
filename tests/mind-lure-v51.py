"""v51 d35: ПРИМАНКА from zarya-mind's reading. Real desk parts in Xvfb, fake song + fake brain map, real reading files."""
import os, sys, time, json, hashlib, shutil
H = os.path.expanduser('~'); P = f'{H}/.local/lib/zarya/desk'
g = {'__name__': 'desk_test', '__file__': f'{H}/.local/bin/zarya-daemon-desk'}
for f in sorted(x for x in os.listdir(P) if x.endswith('.py')):
    exec(compile(open(f'{P}/{f}', encoding='utf-8').read(), f'{P}/{f}', 'exec'), g)
d = g['Demon'](); ZH = g['ZH']; ZJ = g['ZJ']; S = g['MIND_SONGS']; ok = []
LOG = f'{H}/.cache/zarya-daemon-desk.log'
def check(name, cond):
    print(('  ОК ' if cond else '  ✕  ') + name); ok.append(bool(cond))
class M:
    def __init__(s, real): s.r = real; s.on = True; s.a = 'x'; s.t = 'x'
    def __getattr__(s, k): return getattr(s.r, k)
    def playing(s): return s.on
    def active(s): return True
    def artist(s, r=None): return s.a
    def artists(s, r=None): return [s.a]
    def title(s, r=None): return s.t
    def position(s): return 40.0
    def short_active(s): return 'spotify'
class B:
    CUTE_STYLES = ('j-pop', 'k-pop', 'vocaloid', 'idol', 'anime', 'bubblegum', 'kawaii', 'j-core', 'nightcore')
    map = None; key = 'k'
    def learning(s): return False
    def lure(s): return None, ''
    def hard(s): return False
    def weight(s, *a): return 1.0
    def track(s, *a): pass
d.music = M(d.music); d.brain = B()
os.makedirs(S, exist_ok=True)
def reading(a, t, dark, about='Sweet words over something rotten. It smiles while it hurts.', mood=('dark', 'tender')):
    k = ZJ.key_of(a, t)
    json.dump(dict(about=about, mood=list(mood), dark_core=dark, sections=[], key=k, artist=a, title=t, v='m2'),
              open(f'{S}/{hashlib.md5(k.encode()).hexdigest()}.json', 'w', encoding='utf-8'))
def song(a, t, mp=None):
    d.music.a, d.music.t = a, t; d.mkey = ZJ.key_of(a, t); d.brain.map = mp
    d.form.song(time.time(), ZJ.key_of(a, t), dg=d.dg_song(), lure=d.lure_song())
def tail(): return open(LOG, encoding='utf-8').read()

# the real 100 gecs reading from the PC (copied into the sandbox): its file name must match the desk's key
real = os.path.expanduser('~/.local/share/zarya/mind/songs/022cba1abdd93a48795c62a3dc3dc06c.json')   # optional: your own reading
if os.path.exists(real):
    shutil.copy(real, S); song('100 gecs', 'hand crushed by a mallet')
    check('real reading (100 gecs, dark core) found by the desk key, no map → ПРИМАНКА', d.form.lure)
song('Nobody', 'Unread Song'); check('no reading → no mask', not d.form.lure)
reading('Plain', 'Dark Words', False); song('Plain', 'Dark Words'); check('reading without dark core → no mask', not d.form.lure)
reading('Cute', 'Rotten', True); song('Cute', 'Rotten'); check('dark core, no map → ПРИМАНКА at song start', d.form.lure)
song('Cute', 'Rotten', dict(mood=dict(aggressive=0.9, happy=0.1, party=0.2), genre=[('metalcore', 0.6)]))
check('dark core but the ears heard a hard song with no cute side → no mask', not d.form.lure)
check('the veto is logged', 'the sound says no' in tail())
song('Cute', 'Rotten', dict(mood=dict(aggressive=0.9, happy=0.5, party=0.2), genre=[]))
check('hard but a cute side (happy 0.5) → ПРИМАНКА', d.form.lure)
song('Cute', 'Rotten', dict(mood=dict(aggressive=0.8, happy=0.1, party=0.1), genre=[('j-core', 0.4)]))
check('hard but a cute style (j-core) → ПРИМАНКА', d.form.lure)
song('Cute', 'Rotten', dict(mood=dict(aggressive=0.3, happy=0.1, party=0.1), genre=[]))
check('soft map, no cute side → the reading wins (not hard) → ПРИМАНКА', d.form.lure)
reading('Death Grips', 'Sweet Thing', True); song('Death Grips', 'Sweet Thing'); check('ДЕЛИКАТЕС song → no mask', not d.form.lure)
d.cfg['lure_mind'] = '0'; song('Cute', 'Rotten'); check('lure_mind=0 → no mask', not d.form.lure); d.cfg['lure_mind'] = '1'
reading('Sewerslvt', 'Anything', False); song('Sewerslvt', 'Anything'); check('seed / marks still work without a dark core', d.form.lure)
n0 = tail().count('ПРИМАНКА by the reading (Sweet words')
song('Cute', 'Rotten'); d.lure_song(); d.lure_song()
check('one verdict line per song (not every call)', tail().count('ПРИМАНКА by the reading (Sweet words') == n0 + 1)
# mid-song: the reading lands 30 s in
song('Late', 'Arrival'); check('mid-song: nothing before the reading', not d.form.lure)
T = time.time() + 100; d.mind_tick(T); check('mid-song: still nothing (no file yet)', not d.form.lure)
reading('Late', 'Arrival', True); d.mind_tick(T + 2); check('mid-song: waits for the 5 s poll', not d.form.lure)
d.mind_tick(T + 6); check('mid-song: reading arrives → the mask goes on', d.form.lure)
check('mid-song is logged', 'the reading came in mid-song, the mask goes on' in tail())
d.form.lure = False; d.mind_tick(T + 12); check('mid-song: the same reading is not judged twice', not d.form.lure)
song('Late2', 'Veto', dict(mood=dict(aggressive=0.95, happy=0.0, party=0.0), genre=[])); reading('Late2', 'Veto', True)
d.mind_tick(T + 20); check('mid-song: the ears veto a late reading too', not d.form.lure)
song('Other', 'Song'); reading('Late3', 'Wrong', True); d.music.t = 'Wrong'; d.music.a = 'Late3'; d.mind_tick(T + 30)
check('mid-song: a reading for another song than the one it heard → nothing', not d.form.lure)
d.music.on = False; d.mind_tick(T + 40); check('music stopped → no errors, nothing', not d.form.lure)
d.music.on = True
open(f'{S}/{hashlib.md5(ZJ.key_of("Broken", "File").encode()).hexdigest()}.json', 'w').write('{not json')
song('Broken', 'File'); check('broken reading file → no mask, no crash', not d.form.lure)
# event_tick chain still runs the resident tick and ours
calls = []; d.res_tick = lambda now: calls.append('res')
d.event_tick(time.time()); check('event_tick runs (resident + mind wrappers chained)', calls == ['res'])
# menu
items = []
def walk(m):
    for it in m.get_children():
        lab = it.get_label() if hasattr(it, 'get_label') else None
        if lab: items.append(lab)
        if it.get_submenu(): walk(it.get_submenu())
g['Gtk'].Menu.popup_at_pointer = lambda self, ev: walk(self)
song('Cute', 'Rotten'); d.menu(None)
check('This song… shows the reading (greyed)', any(i.startswith('ЧТЕНИЕ') and 'Sweet words over something rotten' in i and 'dark core' in i for i in items))
check('Settings toggle «ПРИМАНКА из чтения»', any('ПРИМАНКА из чтения' in i for i in items))
lg = tail()
check('no mind errors in the log', 'mind lure error' not in lg and 'mind tick error' not in lg and 'song error' not in lg)
check('version d35+', g['VERSION'] >= 'd35')
print('\n'.join(l for l in lg.splitlines() if 'ПРИМАНКА' in l)[-1800:])
print(f'MIND-LURE {sum(ok)}/{len(ok)}'); sys.exit(0 if all(ok) else 1)
