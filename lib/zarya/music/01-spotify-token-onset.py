

def spotify_token(write=True):
    """Access token from zarya-spotify-login's file, refreshed when needed (PKCE, no secret). None if not connected."""
    import urllib.request, urllib.parse
    try: tok = json.load(open(SPOT_TOKEN))
    except (OSError, ValueError): return None
    if time.time() > tok.get('expires', 0) - 60:
        data = urllib.parse.urlencode(dict(grant_type='refresh_token', refresh_token=tok['refresh_token'], client_id=tok['client_id'])).encode()
        req = urllib.request.Request(SPOT_ACCOUNTS + '/api/token', data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        r = json.load(urllib.request.urlopen(req, timeout=8))
        tok['access_token'] = r['access_token']; tok['expires'] = time.time() + int(r.get('expires_in', 3600))
        if r.get('refresh_token'): tok['refresh_token'] = r['refresh_token']
        if r.get('scope'): tok['scope'] = r['scope']
        if write:
            fd = os.open(SPOT_TOKEN, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, 'w') as f: json.dump(tok, f)
    return tok


def spotify_id(trackid, url=''):
    m = re.search(r'track[:/]([A-Za-z0-9]{22})', f'{trackid} {url}')
    return m.group(1) if m else None


def spotify_credits(sid):
    try:
        tok = spotify_token()
        if not tok or not sid: return [], ''
        j = _get(SPOT_API + f'/v1/tracks/{sid}', headers={'Authorization': 'Bearer ' + tok['access_token']})
        return [a.get('name') for a in j.get('artists') or [] if a.get('name')], 'Spotify'
    except Exception as e:
        return [], f'Spotify failed: {e}'


def spotify_like(sid):
    """Save the track to Liked Songs (PUT /v1/me/library, Spotify's Feb 2026 API). Returns (ok, message)."""
    import urllib.request, urllib.parse, urllib.error
    if not sid: return False, 'LIKE WORKS FOR SPOTIFY SONGS'
    try: tok = spotify_token()
    except Exception as e: return False, f'TOKEN REFRESH FAILED'
    if not tok: return False, 'CONNECT FIRST: zarya-spotify-login'
    if 'user-library-modify' not in (tok.get('scope') or ''):
        return False, 'RE-LOGIN ONCE: zarya-spotify-login'
    url = SPOT_API + '/v1/me/library?' + urllib.parse.urlencode(dict(uris=f'spotify:track:{sid}'))
    req = urllib.request.Request(url, method='PUT', headers={'Authorization': 'Bearer ' + tok['access_token'], 'User-Agent': UA})
    try:
        urllib.request.urlopen(req, timeout=8); return True, 'SAVED TO LIKED SONGS'
    except urllib.error.HTTPError as e:
        if e.code in (401, 403): return False, 'RE-LOGIN ONCE: zarya-spotify-login'
        return False, f'SPOTIFY SAID {e.code}'
    except Exception as e:
        return False, 'SPOTIFY UNREACHABLE'


def lrclib_lyrics(artist, title, album='', duration=0):
    """[(seconds, line)] from LRCLIB synced lyrics, [] if none / instrumental."""
    try:
        p = dict(artist_name=artist, track_name=base_title(title))
        if album: p['album_name'] = album
        if duration: p['duration'] = int(round(duration))
        try: j = _get(LRCLIB_API + '/api/get', p)
        except Exception:
            res = _get(LRCLIB_API + '/api/search', dict(artist_name=artist, track_name=base_title(title)))
            j = next((r for r in res or [] if r.get('syncedLyrics')), {})
        if j.get('instrumental'): return [], 'instrumental'
        out = []
        for ln in (j.get('syncedLyrics') or '').splitlines():
            m = re.match(r'\[(\d+):(\d+(?:\.\d+)?)\]\s*(.*)', ln)
            if m and m.group(3).strip(): out.append((int(m.group(1)) * 60 + float(m.group(2)), m.group(3)))
        return out, 'LRCLIB' if out else 'LRCLIB: no synced lyrics'
    except Exception as e:
        return [], f'LRCLIB failed: {e}'


def lyric_scores(lines):
    sc = {k: 0 for k in _LW}
    for _, txt in lines:
        for w in re.findall(r"[a-zñ']+", unicodedata.normalize('NFKD', txt.lower()).encode('ascii', 'ignore').decode()):
            for k, ws in _LW.items():
                if w in ws: sc[k] += 1
    return sc


def lyric_weather(lines):
    """Overall weather from word counts (crude on rap: used after tags)."""
    if len(lines) < 6: return ''
    sc = lyric_scores(lines); sc.pop('cute', None)
    tot = sum(sc.values())
    if tot < 6: return ''
    if sc['rain'] >= 3 and sc['dawn'] >= 0.6 * sc['rain']: return 'dawn'
    k, v = max(sc.items(), key=lambda kv: kv[1])
    second = sorted(sc.values())[-2]
    return k if v >= 4 and v > 1.4 * second else ''


def hooks(lines, title):
    """m4: the song's hook moments for БЕГ: lines with the title in them, else the most repeated line (the chorus).
    Times at least 20 s apart, at most 8."""
    if not lines: return []
    bt = norm(base_title(title)); out = []
    if len(bt) >= 3: out = [t for t, x in lines if bt in norm(x)]
    if len(out) < 2:
        cnt = {}
        for _, x in lines:
            k = norm(x)
            if len(k) >= 6: cnt[k] = cnt.get(k, 0) + 1
        if cnt:
            top = max(cnt, key=cnt.get)
            if cnt[top] >= 2: out = [t for t, x in lines if norm(x) == top]
    res = []
    for t in sorted(out):
        if not res or t - res[-1] >= 20: res.append(t)
    return res[:8]


def lyric_section(lines, pos):
    """Weather of the lines sung around pos (±12 s), or ''."""
    near = [l for l in lines if abs(l[0] - pos) <= 12]
    if len(near) < 2: return ''
    sc = lyric_scores(near); sc.pop('cute', None)
    k, v = max(sc.items(), key=lambda kv: kv[1])
    return k if v >= 2 and v > sorted(sc.values())[-2] else ''


def lookup(meta, duration=0, sid=None, refresh=False):
    """All network lookups for one song, cached in ~/.cache/zarya-daemon/songs/ (7 days; failures retried after 1 day)."""
    key = song_key(meta)
    os.makedirs(INFO_DIR, exist_ok=True)
    path = f'{INFO_DIR}/{hashlib.md5(key.encode()).hexdigest()}.json'
    try:
        info = json.load(open(path))
        age = time.time() - info.get('ts', 0)
        if not refresh and (age < 7 * 86400) and not (info.get('failed') and age > 86400): return info
    except (OSError, ValueError): pass
    art = (meta.get('artists') or [''])[0]; title = meta.get('title') or ''
    info = dict(ts=time.time(), key=key, artist=art, title=title, notes=[])
    info['tags'], n = lastfm_tags(art, base_title(title)); info['notes'].append(f'tags: {n}')
    credits, n1 = spotify_credits(sid) if sid else ([], '')
    if not credits: credits, n1 = mb_credits(art, title)
    info['credits'] = credits; info['notes'].append(f'credits: {n1 or "-"}')
    info['lyrics'], n2 = lrclib_lyrics(art, title, meta.get('album') or '', duration); info['notes'].append(f'lyrics: {n2}')
    info['failed'] = any('failed' in x for x in info['notes'])
    w, hint, why = tags_read(info['tags'])
    info['tag_weather'], info['tag_mode'], info['tag_why'] = w, list(hint) if hint else None, why
    info['lyric_weather'] = lyric_weather(info['lyrics'])
    try:
        with open(path + '.tmp', 'w') as f: json.dump(info, f)
        os.replace(path + '.tmp', path)
    except OSError: pass
    log(f'lookup {art} - {title}: ' + '; '.join(info['notes']) + f' → weather {w or info["lyric_weather"] or "-"}, hint {hint}')
    return info


# ======================= control (global shortcuts, scroll, menu) =======================
def _bus():
    import gi
    from gi.repository import Gio
    return Gio.bus_get_sync(Gio.BusType.SESSION, None)


def players():
    """[(busname, status)] of MPRIS players, Spotify first."""
    from gi.repository import Gio, GLib
    con = _bus()
    names = con.call_sync('org.freedesktop.DBus', '/org/freedesktop/DBus', 'org.freedesktop.DBus', 'ListNames', None,
                          GLib.VariantType('(as)'), Gio.DBusCallFlags.NONE, -1, None).unpack()[0]
    out = []
    for n in names:
        if not n.startswith('org.mpris.MediaPlayer2.') or 'playerctld' in n: continue
        try:
            v = con.call_sync(n, '/org/mpris/MediaPlayer2', 'org.freedesktop.DBus.Properties', 'Get',
                              GLib.Variant('(ss)', ('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')), GLib.VariantType('(v)'),
                              Gio.DBusCallFlags.NONE, 500, None).unpack()[0]
        except Exception: v = '?'
        out.append((n, v))
    out.sort(key=lambda x: (x[1] != 'Playing', 'spotify' not in x[0]))
    return out


def active_player():
    """The player ДЕМОН shows (music.json), else the one playing, else Spotify, else any."""
    st = _state() or {}
    ps = players()
    if not ps: return None
    if st.get('player') and time.time() - st.get('ts', 0) < 10:
        for n, s in ps:
            if n.split('.')[3] == st['player']: return n
    return ps[0][0]


def mpris(name, method):
    from gi.repository import Gio
    _bus().call_sync(name, '/org/mpris/MediaPlayer2', 'org.mpris.MediaPlayer2.Player', method, None, None, Gio.DBusCallFlags.NONE, 2000, None)


def mpris_meta(name):
    from gi.repository import Gio, GLib
    v = _bus().call_sync(name, '/org/mpris/MediaPlayer2', 'org.freedesktop.DBus.Properties', 'Get',
                         GLib.Variant('(ss)', ('org.mpris.MediaPlayer2.Player', 'Metadata')), GLib.VariantType('(v)'),
                         Gio.DBusCallFlags.NONE, 1000, None).unpack()[0]
    return v or {}


def _pactl_inputs():
    try: return json.loads(subprocess.run(['pactl', '-f', 'json', 'list', 'sink-inputs'], capture_output=True, text=True, timeout=3).stdout or '[]')
    except Exception: return []


def player_stream(short):
    """The sink-input(s) of a player (by its MPRIS short name: spotify, firefox, chromium…). Game / Discord audio untouched."""
    short = (short or '').lower(); alias = {'chromium': ('chrome', 'chromium'), 'chrome': ('chrome', 'chromium')}.get(short, (short,))
    out = []
    for si in _pactl_inputs():
        p = si.get('properties') or {}
        blob = ' '.join(str(p.get(k, '')) for k in ('application.process.binary', 'application.name', 'application.id', 'media.name')).lower()
        if any(a and a in blob for a in alias): out.append(si)
    return out


def stream_volume(si):
    vols = [int(str(c.get('value_percent', '0')).rstrip('%') or 0) for c in (si.get('volume') or {}).values()]
    return round(sum(vols) / len(vols)) if vols else 100


def volume_step(short, step):
    """Change the player's own stream by step % (0-100). Returns the new level or None."""
    sis = player_stream(short)
    if not sis: return None
    lvl = max(0, min(100, stream_volume(sis[0]) + step))
    for si in sis: subprocess.run(['pactl', 'set-sink-input-volume', str(si['index']), f'{lvl}%'], timeout=3)
    return lvl


def volume_set(short, lvl):
    for si in player_stream(short): subprocess.run(['pactl', 'set-sink-input-volume', str(si['index']), f'{int(lvl)}%'], timeout=3)


def ctl_event(what, **kv):
    os.makedirs(CACHE, exist_ok=True)
    with open(CTL_EVENT + '.tmp', 'w') as f: json.dump(dict(what=what, ts=time.time(), **kv), f)
    os.replace(CTL_EVENT + '.tmp', CTL_EVENT)


def ctl(args):
    what = args[0] if args else ''
    if what == 'stop-in':
        mins = float(args[1]) if len(args) > 1 else 30
        os.makedirs(CACHE, exist_ok=True); open(STOP_AT, 'w').write(str(time.time() + mins * 60))
        ctl_event('stop-in', mins=mins); print(f'music stops in {mins:g} min (fades out over 10 s)'); return 0
    if what == 'stop-cancel':
        try: os.remove(STOP_AT)
        except OSError: pass
        ctl_event('stop-cancel'); print('stop timer cancelled'); return 0
    name = active_player()
    if not name: print('no music player found'); return 1
    short = name.split('.')[3]
    if what in ('play', 'pause', 'play-pause'): mpris(name, 'PlayPause'); ctl_event('play')
    elif what == 'next': mpris(name, 'Next'); ctl_event('next')
    elif what in ('prev', 'previous'): mpris(name, 'Previous'); ctl_event('prev')
    elif what in ('vol+', 'vol-'):
        lvl = volume_step(short, 5 if what == 'vol+' else -5)
        ctl_event('vol', level=lvl, player=short); print(f'{short} volume {lvl}%' if lvl is not None else f'{short}: no audio stream right now')
    elif what == 'like':
        md = mpris_meta(name)
        ok, msg = spotify_like(spotify_id(md.get('mpris:trackid', ''), md.get('xesam:url', ''))) if short == 'spotify' else (False, 'LIKE WORKS FOR SPOTIFY SONGS')
        ctl_event('like', ok=ok, msg=msg); print(msg)
    else:
        print('ctl: play | next | prev | vol+ | vol- | like | stop-in MIN | stop-cancel'); return 1
    return 0


# ======================= the ear: cava -> beats, tempo, 808, loudness, sections, builds =======================
BANDS = 16
CAVA_TEXT = f'''# written by zarya-music ({VERSION}); regenerated on every start
[general]
framerate = 60
autosens = 0
sensitivity = 15
bars = {BANDS}
lower_cutoff_freq = 40
higher_cutoff_freq = 12000
[input]
method = pulse
source = auto
[output]
method = raw
raw_target = /dev/stdout
data_format = binary
bit_format = 16bit
channels = mono
mono_option = average
[smoothing]
integral = 0
monstercat = 0
waves = 0
gravity = 0
'''


def db(x): return 20 * math.log10(x + 30.0)                   # 30 = floor, so silence sits near 29.5 dB


def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x


class Onset:
    """Positive log-energy flux with an adaptive threshold and a refractory gap."""
    def __init__(self, gap, k=1.6, floor=1.2):
        self.prev = None; self.hist = []; self.last = -9; self.gap = gap; self.k = k; self.floor = floor
    def feed(self, e, t):
        flux = 0.0 if self.prev is None else max(0.0, e - self.prev)
        self.prev = e if self.prev is None else max(e, self.prev * 0.6 + e * 0.4)   # follow drops slowly
        self.hist.append(flux); self.hist = self.hist[-90:]
        m = sum(self.hist) / len(self.hist)
        sd = (sum((h - m) ** 2 for h in self.hist) / len(self.hist)) ** 0.5
        if flux > max(self.floor, m + self.k * sd) and t - self.last >= self.gap:
            self.last = t; return flux
        return 0.0
