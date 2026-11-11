"""v53 d37 + m4: ДЕЛИКАТЕС by ear. Desk part in Xvfb with real reading files; zarya-mind m4 against a fake Gemini server."""
import os, sys, time, json, hashlib, subprocess, threading, http.server, importlib.machinery, importlib.util, shutil, wave
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = os.path.expanduser('~'); P = f'{H}/.local/lib/zarya/desk'
g = {'__name__': 'desk_test', '__file__': f'{H}/.local/bin/zarya-daemon-desk'}
for f in sorted(x for x in os.listdir(P) if x.endswith('.py')):
    exec(compile(open(f'{P}/{f}', encoding='utf-8').read(), f'{P}/{f}', 'exec'), g)
d = g['Demon'](); ZH = g['ZH']; ZJ = g['ZJ']; ok = []
def check(name, cond): print(('  ОК ' if cond else '  ✕  ') + name); ok.append(bool(cond))
LOG = []; g0 = g['log']; g['log'] = lambda m: (LOG.append(m), g0(m))
CLK = {'artist': 'Death Grips', 'title': 'Hacker'}
class M:
    def __init__(s, real): s.r = real
    def __getattr__(s, k): return getattr(s.r, k)
    def playing(s): return True
    def artist(s, r=None): return CLK['artist']
    def artists(s, r=None): return [CLK['artist']]
    def title(s, r=None): return CLK['title']
    def position(s): return 40.0
    def trackinfo(s, r=None): return ('t', '', 200.0)
d.music = M(d.music); d.mkey = 'k1'; d.screen_fx = None; d.morph = None; d.stand = None
def rpath(a, t): k = ZJ.key_of(a, t); return k, f'{H}/.local/share/zarya/mind/songs/{hashlib.md5(k.encode()).hexdigest()}.json'
def reading(a, t, **kw):
    k, p = rpath(a, t); os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(dict(dict(key=k, about='x', mood=['angry'], dark_core=True, sections=[], heard=True, deli=True, sound='A barked voice over blown-out noise.'), **kw), open(p, 'w'))
    d._mind_c = None; d._deli_c = None
class B:
    map = {}; CUTE_STYLES = ()
    def section(s, pos): return None
    def hard(s): return False
    def lure(s): return None, ''
d.brain = B()
CLK.update(artist='Kublai Khan TX', title='Self-Destruct')
check('no reading: not ДЕЛИКАТЕС (unmarked, not seed)', not d.dg_song())
reading('Kublai Khan TX', 'Self-Destruct')
check('heard + deli: ДЕЛИКАТЕС by ear, logged once', d.dg_song() and d.dg_song() and sum('ДЕЛИКАТЕС by ear (A barked voice' in m for m in LOG) == 1)
reading('Kublai Khan TX', 'Self-Destruct', heard=False); check('not heard (lyrics only): no', not d.dg_song())
reading('Kublai Khan TX', 'Self-Destruct', deli=False); check('heard, deli false: no', not d.dg_song())
reading('Kublai Khan TX', 'Self-Destruct'); d.brain.map = dict(delicacy=0.08); d._deli_c = None
check('song brain score 0.08 vetoes it (logged)', not d.dg_song() and any('the brain says soft' in m or 'song brain says soft' in m for m in LOG))
d.brain.map = dict(delicacy=0.21); d._deli_c = None; check('score 0.21 (like Hacker): ДЕЛИКАТЕС stands', d.dg_song())
d.cfg['deli_mind'] = '0'; d._deli_c = None; check('deli_mind=0: off', not d.dg_song()); d.cfg['deli_mind'] = '1'; d._deli_c = None
check('ПРИМАНКА from the reading blocked on a ДЕЛИКАТЕС-by-ear song', d.mind_lure()[0] is False)
check('menu line says ДЕЛИКАТЕС by ear', d.mind_menu_line().endswith('ДЕЛИКАТЕС by ear'))
F = d.form; now = time.time(); F.start(now, 0, 'test', song=ZJ.key_of('Kublai Khan TX', 'Self-Destruct')); F.song(now, ZJ.key_of('Kublai Khan TX', 'Self-Destruct'))
F.dg = False; F.det_max = 0; d._deli_t = 0; d.deli_tick(now)
check('mid-song: form turns ДЕЛИКАТЕС, up to 2 blasts', F.dg and F.det_max == 2 and F.hard)
CLK.update(artist='Death Grips', title='Hacker'); d._deli_c = None
check('seed artist still ДЕЛИКАТЕС without a reading', d.dg_song())
check('version d37 + toggle in the menu', g['VERSION'] == 'd37' and "'deli_mind'" in open(f'{P}/01-demon-1-sel-owner-paint-overlay.py', encoding='utf-8').read())

# ---- zarya-mind m4
Z = '/tmp/deli-home'; shutil.rmtree(Z, ignore_errors=True)
for x in ('.cache/zarya-daemon/songs', '.config/zarya', '.cache/zarya-brain/ears', '.local/share/zarya/mind/ears-done', '.local/share/zarya/mind/songs'): os.makedirs(f'{Z}/{x}')
open(f'{Z}/.config/zarya/gemini.key', 'w').write('K'); open(f'{Z}/.config/zarya/mind.conf', 'w').write('gap=0\n')
SEEN = []
class S(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        b = json.loads(self.rfile.read(int(self.headers['Content-Length']))); SEEN.append(b['contents'][0]['parts'][-1]['text'])
        txt = json.dumps(dict(about='A man barks threats.', sound='Barked voice over blown-out noise.', mood=['angry'], dark_core=False, deli=True, sections=[dict(at=2, feel='angry'), dict(at=40, feel='hype')]))
        self.send_response(200); self.end_headers(); self.wfile.write(json.dumps(dict(candidates=[dict(content=dict(parts=[dict(text=txt)]))])).encode())
srv = http.server.HTTPServer(('127.0.0.1', 0), S); threading.Thread(target=srv.serve_forever, daemon=True).start()
os.environ.update(HOME=Z, ZARYA_GEMINI_API=f'http://127.0.0.1:{srv.server_port}')
ld = importlib.machinery.SourceFileLoader('zm4', f'{REPO}/bin/zarya-mind'); ZM4 = importlib.util.module_from_spec(importlib.util.spec_from_loader('zm4', ld)); ld.exec_module(ZM4)
ep = f'{Z}/.cache/zarya-brain/ears/abc.json'
with wave.open(ep[:-5] + '.wav', 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(22050); w.writeframes(b'\0\0' * 22050 * 20)
json.dump(dict(artist='Death Grips', title='Hacker', dur=200, id='abc', clips=[dict(song_at=2, len=10, clip_at=0), dict(song_at=40, len=10, clip_at=10.3)]), open(ep, 'w'))
how = ZM4.hear_song(ZM4.conf(), ep, json.load(open(ep)))
r = json.load(open(ZM4.song_path(ZM4.key_of('Death Grips', 'Hacker'))))
check('m4: the ears prompt asks "deli" with the definition', '"deli"' in SEEN[-1] and 'Death Grips-grade' in SEEN[-1] and 'not plain' not in SEEN[-1] or 'plain EDM' in SEEN[-1])
check('m4: heard reading keeps deli=True + ears_id', how == 'done' and r['deli'] is True and r['ears_id'] == 'abc' and r['v'] == 'm4')
check('m4: log names ДЕЛИКАТЕС', '· ДЕЛИКАТЕС ·' in open(f'{Z}/.cache/zarya-mind.log').read())
# rehear: an m3 heard reading without deli → its marker removed once
bk = ZM4.brain_key('Slipknot', 'Spit It Out - Hyper Version'); i = hashlib.sha1(bk.encode()).hexdigest()[:16]
open(f'{Z}/.local/share/zarya/mind/ears-done/{i}', 'w').write('heard')
json.dump(dict(key='slipknot|spit it out', artist='Slipknot', title='Spit It Out - Hyper Version', about='x', heard=True, v='m3', sections=[]), open(f'{Z}/.local/share/zarya/mind/songs/s.json', 'w'))
n = ZM4.rehear_old(); n2 = ZM4.rehear_old()
check('m4: m3 heard readings get heard again once (marker removed)', n == 1 and n2 == 0 and not os.path.exists(f'{Z}/.local/share/zarya/mind/ears-done/{i}') and os.path.exists(f'{Z}/.local/share/zarya/mind/ears-done/abc'))
check('m4: text-only readings carry no deli', 'deli' not in ZM4.clean_reading(dict(about='a', mood=[], sections=[]), []))
srv.shutdown()
print(f'DELI {sum(ok)}/{len(ok)}'); sys.exit(0 if all(ok) else 1)
