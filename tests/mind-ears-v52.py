"""v52 zarya-brain b6 ears + zarya-mind m3: clips cut from the brain's recording, sent as inline audio, the reading marked heard,
the clip deleted; refusals, instrumentals, cap, the brain's capture rules. Fake home + fake Gemini server."""
import os, sys, json, time, threading, subprocess, http.server, shutil, base64, wave, io, hashlib, importlib.machinery, importlib.util
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = '/tmp/ears-home'; shutil.rmtree(H, ignore_errors=True)
for d in ('.cache/zarya-daemon/songs', '.cache/zarya', '.config/zarya', '.local/share/zarya/listening', '.local/share/zarya/brain/maps', '.cache/zarya-brain'):
    os.makedirs(f'{H}/{d}')
open(f'{H}/.config/zarya/gemini.key', 'w').write('AQ.TESTKEY-x')
open(f'{H}/.config/zarya/mind.conf', 'w').write('gap=0\ndaily_cap=20\nbackfill_per_hour=0\n')
os.environ['HOME'] = H
ld = importlib.machinery.SourceFileLoader('zb', f'{REPO}/bin/zarya-brain'); ZB = importlib.util.module_from_spec(importlib.util.spec_from_loader('zb', ld)); ld.exec_module(ZB)
ok = []
def check(n, c): print(('  ОК ' if c else '  ✕  ') + n); ok.append(bool(c))

# --- a known song (map with 10 sections) recorded once more
art, tit = '100 gecs', 'hand crushed by a mallet'; bkey = ZB.song_key(art, tit); dur = 120.0; sr = ZB.SR
secs = [dict(t0=k * 12.0, t1=(k + 1) * 12.0, kind='verse', label='КУПЛЕТ') for k in range(10)]
json.dump(dict(artist=art, title=tit, sections=secs, mood=dict(happy=0.5)), open(ZB.map_path(bkey), 'w'))
raw = f'{H}/.cache/zarya-brain/x.raw'; open(raw, 'wb').write(b'\x10\x00' * int(dur * sr))
mp = raw[:-4] + '.json'; json.dump(dict(artist=art, title=tit, dur=dur, key=bkey, ears=True, ears_only=True, offset=0), open(mp, 'w'))
r = subprocess.run(['python3', '-I', f'{REPO}/bin/zarya-brain', 'ears', raw, mp], env=dict(os.environ), capture_output=True, text=True)
i = ZB.ears_id(bkey); wp = f'{H}/.cache/zarya-brain/ears/{i}.wav'; jp = wp[:-4] + '.json'
check('ears: recording cut, raw + meta deleted', os.path.exists(wp) and os.path.exists(jp) and not os.path.exists(raw) and not os.path.exists(mp))
j = json.load(open(jp)); w = wave.open(wp)
check('8 clips (the 10 sections cut to 8), ≤ 10 s each', len(j['clips']) == 8 and all(c['len'] <= 10 for c in j['clips']))
check('WAV 22.05 kHz mono 16-bit, ~80 s + gaps', w.getframerate() == sr and w.getnchannels() == 1 and w.getsampwidth() == 2 and 80 <= w.getnframes() / sr <= 83)
check('clip song times inside their sections', all(any(s['t0'] <= c['song_at'] < s['t1'] for s in secs) for c in j['clips']))
check('size ≤ 4 MB (inline limit 20 MB)', os.path.getsize(wp) < 4e6)

# --- the brain's capture rules
open(f'{H}/.config/zarya/mind.conf', 'a').write('')
B = ZB.Brain.__new__(ZB.Brain); B.key = None; B.map = None; B.cap = None; B.studying = set(); B.last_sec = None
started = []
B.start = lambda now, meta, pos: started.append(meta); B.finish = lambda now, pos_end=None: None
B.track(time.time(), art, tit, '', dur, 0, True)
check('known song with a clip already waiting: no new capture', started == [])
os.remove(jp); os.remove(wp); ZB._EW['t'] = 0
B.track(time.time(), art, tit, '', dur, 0, True)
check('known song, not heard: ears-only capture', len(started) == 1 and started[0].get('ears_only'))
os.makedirs(f'{H}/.local/share/zarya/mind/ears-done', exist_ok=True); open(f'{H}/.local/share/zarya/mind/ears-done/{i}', 'w').write('heard')
started.clear(); B.track(time.time(), art, tit, '', dur, 0, True)
check('heard already: no capture', started == [])
os.remove(f'{H}/.local/share/zarya/mind/ears-done/{i}')
open(f'{H}/.config/zarya/mind.conf', 'a').write('ears=0\n'); ZB._EW['t'] = 0
started.clear(); B.track(time.time(), art, tit, '', dur, 0, True)
check('ears=0: no capture', started == [])
open(f'{H}/.config/zarya/mind.conf', 'w').write('gap=0\ndaily_cap=20\nbackfill_per_hour=0\n'); ZB._EW['t'] = 0
started.clear(); B.track(time.time(), art, tit, '', 30, 0, True)
check('songs under 60 s: no capture', started == [])

# --- cut again for zarya-mind
open(raw, 'wb').write(b'\x10\x00' * int(dur * sr)); json.dump(dict(artist=art, title=tit, dur=dur, key=bkey, ears=True, ears_only=True, offset=0), open(mp, 'w'))
subprocess.run(['python3', '-I', f'{REPO}/bin/zarya-brain', 'ears', raw, mp], env=dict(os.environ), capture_output=True)
# instrumental, no lyrics, no map → evenly spread clips
art2, tit2 = 'kensuke ushio', 'Sabbath Ⅰ'; bk2 = ZB.song_key(art2, tit2)
open(raw, 'wb').write(b'\x10\x00' * int(90 * sr)); json.dump(dict(artist=art2, title=tit2, dur=90, key=bk2, ears=True, ears_only=True, offset=0), open(mp, 'w'))
subprocess.run(['python3', '-I', f'{REPO}/bin/zarya-brain', 'ears', raw, mp], env=dict(os.environ), capture_output=True)
j2 = json.load(open(f'{H}/.cache/zarya-brain/ears/{ZB.ears_id(bk2)}.json'))
check('no map: clips spread over the song', len(j2['clips']) == 8 and j2['clips'][-1]['song_at'] > 70)
# lyrics for the first song in ДЕМОН's cache
json.dump(dict(ts=time.time(), artist=art, title=tit, lyrics=[[5 + 9 * k, f'sugar line {k} about a mallet'] for k in range(12)]), open(f'{H}/.cache/zarya-daemon/songs/a.json', 'w'))

SEEN = []; MODE = {'next': []}
class S(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        parts = body['contents'][0]['parts']; SEEN.append(dict(path=self.path, parts=parts, mime=body['generationConfig'].get('responseMimeType')))
        m = MODE['next'].pop(0) if MODE['next'] else 'good'
        if m == '400': self.send_response(400); self.end_headers(); self.wfile.write(b'{"error":{"message":"audio not supported"}}'); return
        if m == '503': self.send_response(503); self.end_headers(); self.wfile.write(b'{}'); return
        if m == 'garbage': txt = 'nope'
        else:
            txt = json.dumps(dict(about='Someone sings sweetly about a crushed hand.', sound='A sugary voice over bright synths that tear apart.',
                                  mood=['playful', 'dark'], dark_core=True, sections=[dict(at=2, feel='sweet'), dict(at=38, feel='sad'), dict(at=74, feel='hype'), dict(at=9999, feel='angry')], language='English'))
        self.send_response(200); self.send_header('Content-Type', 'application/json'); self.end_headers()
        self.wfile.write(json.dumps(dict(candidates=[dict(content=dict(parts=[dict(text=txt)]))])).encode())
srv = http.server.HTTPServer(('127.0.0.1', 0), S); threading.Thread(target=srv.serve_forever, daemon=True).start()
env = dict(os.environ, HOME=H, ZARYA_GEMINI_API=f'http://127.0.0.1:{srv.server_port}')
ld = importlib.machinery.SourceFileLoader('zm', f'{REPO}/bin/zarya-mind'); os.environ['ZARYA_GEMINI_API'] = env['ZARYA_GEMINI_API']
ZMd = importlib.util.module_from_spec(importlib.util.spec_from_loader('zm', ld)); ld.exec_module(ZMd)
c = ZMd.conf()
pend = ZMd.ears_pending(); check('zarya-mind sees 2 clips waiting', len(pend) == 2)
p1 = next(p for p, jj in pend if jj['title'] == tit)
how = ZMd.hear_song(c, p1, json.load(open(p1)))
s0 = SEEN[-1]; aud = s0['parts'][0].get('inlineData') or {}
check('one call: inline WAV first, then the prompt', how == 'done' and aud.get('mimeType') == 'audio/wav' and 'text' in s0['parts'][1])
wb = base64.b64decode(aud.get('data', '')); check('the audio sent = the clip file (a WAV)', wb[:4] == b'RIFF' and len(wb) > 3e6)
check('prompt lists the excerpts with song times + the lyrics', '1: 0:' in s0['parts'][1]['text'] and 'sugar line 0' in s0['parts'][1]['text'] and 'AUDIO' in s0['parts'][1]['text'])
rd_ = json.load(open(ZMd.song_path(ZMd.key_of(art, tit))))
check('reading: heard, sound line, dark core, sections inside the song', rd_.get('heard') and rd_.get('sound', '').startswith('A sugary') and rd_['dark_core'] and [s['at'] for s in rd_['sections']] == [2, 38, 74])
check('clip deleted, ears-done marker written', not os.path.exists(p1) and not os.path.exists(p1[:-5] + '.wav') and os.path.exists(f'{H}/.local/share/zarya/mind/ears-done/{i}'))
log = open(f'{H}/.cache/zarya-mind.log').read()
check('log: "ears: heard … · 0:02 sweet 0:38 sad 1:14 hype"', 'ears: heard 100 gecs - hand crushed by a mallet (8 clips)' in log and '0:38 sad' in log and 'AQ.TESTKEY' not in log)
p2 = next(p for p, jj in ZMd.ears_pending())
MODE['next'] = ['garbage']; how = ZMd.hear_song(c, p2, json.load(open(p2)))
check('garbage answer: kept for one more try', how == 'skip: bad answer' and os.path.exists(p2))
check('instrumental prompt says no lyrics', 'No lyrics known' in SEEN[-1]['parts'][1]['text'])
MODE['next'] = ['400', '400']; how = ZMd.hear_song(c, p2, json.load(open(p2)))
check('400 with audio (JSON mode, then plain) → refused, clip dropped, no reading', how == 'skip: audio refused' and not os.path.exists(p2)
      and not os.path.exists(ZMd.song_path(ZMd.key_of(art2, tit2))) and SEEN[-1]['mime'] is None)
# cap + ears off
for f in ('a.raw',): pass
open(raw, 'wb').write(b'\x10\x00' * int(90 * sr)); json.dump(dict(artist=art2, title=tit2, dur=90, key=bk2, ears=True, ears_only=True, offset=0), open(mp, 'w'))
os.remove(f'{H}/.local/share/zarya/mind/ears-done/{ZB.ears_id(bk2)}')
subprocess.run(['python3', '-I', f'{REPO}/bin/zarya-brain', 'ears', raw, mp], env=dict(os.environ), capture_output=True)
p3 = ZMd.ears_pending()[0][0]
st = ZMd.state(); st['calls'] = {time.strftime('%F'): 20}; ZMd.save_state(st); n = len(SEEN)
check('daily cap: no call, clip waits', ZMd.hear_song(c, p3, json.load(open(p3))).startswith('skip: daily cap') and len(SEEN) == n and os.path.exists(p3))
st['calls'] = {}; ZMd.save_state(st)
check('ears=0: no call', ZMd.hear_song(dict(c, ears='0'), p3, json.load(open(p3))) == 'skip: ears off' and len(SEEN) == n)
MODE['next'] = ['503', '503']; how = ZMd.hear_song(c, p3, json.load(open(p3)))
check('503 on both models → backoff, clip waits', how == 'skip: backoff' and os.path.exists(p3))
out = subprocess.run(['python3', f'{REPO}/bin/zarya-mind', 'status'], env=env, capture_output=True, text=True).stdout
check('status shows ears', 'ears: on · 1 songs heard · 1 clips waiting' in out)
check('--version m3', subprocess.run(['python3', f'{REPO}/bin/zarya-mind', '--version'], env=env, capture_output=True, text=True).stdout.strip() in ('zarya-mind m3', 'zarya-mind m4'))
check('show prints the sound line', 'sound: A sugary voice' in subprocess.run(['python3', f'{REPO}/bin/zarya-mind', 'show', 'mallet'], env=env, capture_output=True, text=True).stdout)
# a text-only read of a heard song never overwrites it (now-playing path checks the cache)
how, _ = ZMd.read_song(c, ZMd.key_of(art, tit)); check('text read later: cached, the heard reading stays', how == 'cached')
srv.shutdown()
print(f'{sum(ok)}/{len(ok)}'); sys.exit(0 if all(ok) else 1)
