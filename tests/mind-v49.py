"""v49 zarya-mind m1 + journal j4: fake home, fake Gemini server (good / 429 / 404 / 400 JSON / garbage), budget, games, ДНЕВНИК."""
import os, sys, json, time, threading, subprocess, http.server, shutil, re
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = '/tmp/mind-home'; shutil.rmtree(H, ignore_errors=True)
for d in ('.cache/zarya-daemon/songs', '.cache/zarya', '.config/zarya', '.local/share/zarya/listening'): os.makedirs(f'{H}/{d}')
KEY = 'AQ.TESTKEY-never-in-logs-1234dtRg'
open(f'{H}/.config/zarya/gemini.key', 'w').write(KEY)
songs = [('Death Grips', 'Hacker'), ('Sewerslvt', 'Cyberia lyr1'), ('Deftones', 'My Own Summer (Shove It)'), ('A$AP Rocky', 'NO TRESPASSING')]
for i, (a, t) in enumerate(songs):
    json.dump(dict(ts=time.time(), key=f'{a}|{t}', artist=a, title=t, lyrics=[[5 + 9 * j, f'line {j} of {t}'] for j in range(12)]), open(f'{H}/.cache/zarya-daemon/songs/s{i}.json', 'w'))
now = time.time()
with open(f'{H}/.local/share/zarya/listening/plays-{time.strftime("%Y%m")}.jsonl', 'w') as f:
    for i in range(30):
        a, t = songs[i % 4]; f.write(json.dumps(dict(ts=now - i * 3600, artist=a, title=t, heard=180, outcome='finish', mode='grips', key=f'{a.lower()}|{t.lower()}')) + '\n')
json.dump(dict(ts=time.time(), playing=True, title='Hacker', artists=['Death Grips'], position=45), open(f'{H}/.cache/zarya-daemon/music.json', 'w'))
MODE = {'next': []}; SEEN = []
class S(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        SEEN.append(dict(path=self.path, key=self.headers.get('x-goog-api-key'), mime=body['generationConfig'].get('responseMimeType'), text=body['contents'][0]['parts'][0]['text']))
        m = MODE['next'].pop(0) if MODE['next'] else 'good'
        if m == '429': self.send_response(429); self.end_headers(); self.wfile.write(b'{"error":{"details":[{"retryDelay":"30s"}]}}'); return
        if m == '404' and 'gemini-3.5' in self.path: self.send_response(404); self.end_headers(); self.wfile.write(b'{}'); return
        if m == '400json' and body['generationConfig'].get('responseMimeType'): self.send_response(400); self.end_headers(); self.wfile.write(b'{}'); MODE['next'].insert(0, 'good'); return
        txt = 'not json at all' if m == 'garbage' else json.dumps(dict(about='A hacker taunts a world that cannot keep up. It is a boast and a threat.', mood=['hype', 'defiant', 'bogus'],
              dark_core=False, sections=[dict(at=5, feel='hype'), dict(at=50, feel='angry'), dict(at=9999, feel='hype')], language='English', read='You lived in Death Grips this week.', headline='A loud week'))
        self.send_response(200); self.send_header('Content-Type', 'application/json'); self.end_headers()
        self.wfile.write(json.dumps(dict(candidates=[dict(content=dict(parts=[dict(text=txt)]))])).encode())
srv = http.server.HTTPServer(('127.0.0.1', 0), S); threading.Thread(target=srv.serve_forever, daemon=True).start()
env = dict(os.environ, HOME=H, ZARYA_GEMINI_API=f'http://127.0.0.1:{srv.server_port}')
open(f'{H}/.config/zarya/mind.conf', 'w').write('gap=0\ndaily_cap=8\n')
def mind(*a): return subprocess.run(['python3.12', f'{REPO}/bin/zarya-mind', *a], env=env, capture_output=True, text=True, timeout=30).stdout
ok = []
def check(n, c): print(('  ОК ' if c else '  ✕  ') + n); ok.append(bool(c))
check('test call works', 'OK' in mind('test'))
out = mind('now'); check('now: reads the playing song', out.startswith('done') and 'hacker taunts' in out.lower())
r = json.load(open([os.path.join(dp, f) for dp, _, fs in os.walk(f'{H}/.local/share/zarya/mind/songs') for f in fs][0]))
check('bogus mood + out-of-range section dropped', r['mood'] == ['hype', 'defiant'] and all(s['at'] < 200 for s in r['sections']))
check('second now = cached (no new call)', mind('now').startswith('cached') and len(SEEN) == 2)
check('key sent in the header, JSON mode on', SEEN[-1]['key'] == KEY and SEEN[-1]['mime'] == 'application/json' and ':generateContent' in SEEN[-1]['path'])
check('prompt carries only artist, title, lyric lines', 'Death Grips - Hacker' in SEEN[1]['text'] and 'line 0 of Hacker' in SEEN[1]['text'] and KEY not in SEEN[1]['text'])
MODE['next'] = ['404']; out = mind('song', 'Sewerslvt - Cyberia lyr1'); check('404 on the main model → fallback answers', out.startswith('done') and 'gemini-3.1-flash-lite' in SEEN[-1]['path'])
MODE['next'] = ['400json']; out = mind('song', 'Deftones - My Own Summer (Shove It)'); check('400 in JSON mode → retried without it', out.startswith('done') and SEEN[-1]['mime'] is None)
MODE['next'] = ['garbage']; out = mind('song', 'A$AP Rocky - NO TRESPASSING'); check('garbage answer → not cached', 'bad answer' in out and 'none' in mind('show', 'trespassing'))
MODE['next'] = ['429']; out = mind('song', 'A$AP Rocky - NO TRESPASSING'); st = json.load(open(f'{H}/.local/share/zarya/mind/state.json'))
check('429 → backoff with retryDelay (~35 s)', 'backoff' in out and 25 < st['backoff_until'] - time.time() < 40)
nb = len(SEEN); check('during backoff: no call', 'backing off' in mind('song', 'A$AP Rocky - NO TRESPASSING', '--force') and len(SEEN) == nb)
st['backoff_until'] = 0; json.dump(st, open(f'{H}/.local/share/zarya/mind/state.json', 'w'))
n0 = len(SEEN); out = mind('week'); check('week read written', out.startswith('done') and 'Death Grips this week' in out)
check('week facts are numbers only (no lyrics)', 'line 0' not in SEEN[-1]['text'] and 'top artists' in SEEN[-1]['text'])
st = json.load(open(f'{H}/.local/share/zarya/mind/state.json')); st['calls'] = {time.strftime('%F'): 8}; json.dump(st, open(f'{H}/.local/share/zarya/mind/state.json', 'w'))
check('daily cap stops calls', 'daily cap' in mind('song', 'A$AP Rocky - NO TRESPASSING') and len(SEEN) == n0 + 1)
with open(f'{H}/.cache/zarya/bus-{time.strftime("%Y%m%d")}.jsonl', 'w') as f: f.write(json.dumps(dict(kind='game', msg='game: he stays, hands off (dota2 · dota2)'), ensure_ascii=False) + '\n')
check('game on the bus → in a game', 'in a game now: True' in mind('status'))
with open(f'{H}/.cache/zarya/bus-{time.strftime("%Y%m%d")}.jsonl', 'a') as f: f.write(json.dumps(dict(kind='game', msg='game: over, he takes input again'), ensure_ascii=False) + '\n')
check('game over on the bus → not in a game', 'in a game now: False' in mind('status'))
logt = open(f'{H}/.cache/zarya-mind.log').read()
check('key never in the log or state', KEY not in logt and KEY not in open(f'{H}/.local/share/zarya/mind/state.json').read())
st = json.load(open(f'{H}/.local/share/zarya/mind/state.json')); st['calls'] = {}; json.dump(st, open(f'{H}/.local/share/zarya/mind/state.json', 'w'))
# service loop: game → paused, no calls; then reads the playing song
for p in os.listdir(f'{H}/.local/share/zarya/mind/songs'): os.remove(f'{H}/.local/share/zarya/mind/songs/{p}')
with open(f'{H}/.cache/zarya/bus-{time.strftime("%Y%m%d")}.jsonl', 'a') as f: f.write(json.dumps(dict(kind='game', msg='game: he is drawn on top of it (layer)'), ensure_ascii=False) + '\n')
json.dump(dict(ts=time.time(), playing=True, title='Hacker', artists=['Death Grips'], position=45), open(f'{H}/.cache/zarya-daemon/music.json', 'w'))
n0 = len(SEEN); pr = subprocess.Popen(['python3.12', f'{REPO}/bin/zarya-mind', 'run'], env=env); time.sleep(4)
check('service: in a game → no calls', len(SEEN) == n0)
with open(f'{H}/.cache/zarya/bus-{time.strftime("%Y%m%d")}.jsonl', 'a') as f: f.write(json.dumps(dict(kind='game', msg='game: layer off, back in his window'), ensure_ascii=False) + '\n')
json.dump(dict(ts=time.time(), playing=True, title='Hacker', artists=['Death Grips'], position=45), open(f'{H}/.cache/zarya-daemon/music.json', 'w'))
time.sleep(18); pr.terminate()
check('service: game over → reads the playing song', os.listdir(f'{H}/.local/share/zarya/mind/songs'))
print(open(f'{H}/.cache/zarya-mind.log').read()[-700:])
# ДНЕВНИК j4
mind('song', 'Sewerslvt - Cyberia lyr1')
env2 = dict(env); res = subprocess.run(['python3.12', f'{REPO}/bin/zarya-journal', 'diary', '--no-open'], env=env2, capture_output=True, text=True, timeout=60)
html = open(f'{H}/.local/share/zarya/listening/dnevnik.html', encoding='utf-8').read()
check('ДНЕВНИК carries the readings + the week', 'hacker taunts' in html.lower() and 'Death Grips this week' in html and '__MIND__' not in html)
print(f'MIND {sum(ok)}/{len(ok)}'); srv.shutdown(); sys.exit(0 if all(ok) else 1)
