import os, sys, time, re, glob, math, random, subprocess, threading, importlib.util
from importlib.machinery import SourceFileLoader
import gi
gi.require_version('Gtk', '3.0'); gi.require_version('PangoCairo', '1.0')
from gi.repository import Gtk, Gdk, GLib, Gio, Pango, PangoCairo
import cairo

VERSION = 'd39'
HOME = os.path.expanduser('~')
BIN = f'{HOME}/.local/bin'
CACHE = f'{HOME}/.cache/zarya-daemon'
EVENTS, JOBS, MUTE = f'{CACHE}/events', f'{CACHE}/jobs', f'{CACHE}/desk-mute'
CONF = f'{HOME}/.config/zarya/daemon.conf'
CLASSES = f'{HOME}/.config/zarya/classes.conf'                              # d25: `deli <artist>` / `lure <artist>`, one per line
DELI_SEED = ('death grips', 'excision', 'he$h', 'hesh', 'must die', 'space laces', '12th planet')
LURE_SEED = ('sewerslvt', 'utsu-p', 'utsup', 'うつp', 'purity filter')
LOG = f'{HOME}/.cache/zarya-daemon-desk.log'
TIMERS = f'{CACHE}/timers'
SPOT_TOKEN = f'{HOME}/.config/zarya/spotify-token.json'
SPOT_API = os.environ.get('ZARYA_SPOTIFY_API', 'https://api.spotify.com')
SPOT_ACCOUNTS = os.environ.get('ZARYA_SPOTIFY_ACCOUNTS', 'https://accounts.spotify.com')
RING_SOUNDS = ['/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga', '/usr/share/sounds/freedesktop/stereo/complete.oga',
               '/usr/share/sounds/LinuxMint/stereo/dialog-warning.ogg']
VIDEO_CLASSES = ('firefox', 'mpv', 'vlc', 'brave', 'chromium', 'google-chrome', 'totem', 'celluloid', 'spotify', 'xviewer')

_loader = SourceFileLoader('zarya_daemon', f'{BIN}/zarya-daemon')
_spec = importlib.util.spec_from_loader('zarya_daemon', _loader)
ZD = importlib.util.module_from_spec(_spec); _loader.exec_module(ZD)
try:                                                      # d4: music modes (optional: ДЕМОН works without it)
    _ml = SourceFileLoader('zarya_music', f'{BIN}/zarya-music')
    ZM = importlib.util.module_from_spec(importlib.util.spec_from_loader('zarya_music', _ml)); _ml.exec_module(ZM)
except Exception as _e:
    ZM = None
def _opt(name, path):                                     # d10: optional modules (ДЕМОН works without them)
    try:
        _l = SourceFileLoader(name, path); m = importlib.util.module_from_spec(importlib.util.spec_from_loader(name, _l)); _l.exec_module(m); return m
    except Exception: return None
ZH = _opt('zarya_hurt', f'{BIN}/zarya-hurt')
ZJ = _opt('zarya_journal', f'{BIN}/zarya-journal')
ZB = _opt('zarya_brain', f'{BIN}/zarya-brain')                       # d20: the song brain
AUTH_LOG = '/var/log/auth.log'
ASK_TITLE = 'КАК ОНА ЗВУЧИТ?'
SB = dict(intro='▫', verse='▪', chorus='■', bridge='◆', outro='▫', part='◇', drop='▲')     # d20: song map glyphs
FXOFF = f'{CACHE}/fx-off'
HOLD, HINTS = f'{CACHE}/select-hold', f'{CACHE}/hint-seen'   # d6
SEL_HOLD = 45
GHOSTOFF = f'{CACHE}/ghost-off'                                   # d7
REPORTS = f'{HOME}/.local/share/zarya/reports'                   # d7
BROWSERS = ('firefox', 'chromium', 'chrome', 'google', 'brave', 'vivaldi', 'opera', 'edge', 'librewolf', 'zen')
REPORT_KINDS = [('mode', 'Wrong mode (how he moves)'), ('mood', 'Wrong mood (the weather)'), ('glitch', 'Animation glitch'),
                ('afk', 'Froze / AFK'), ('way', 'Got in the way'), ('other', 'Other')]

EXCLUDE = {'claude', 'vim', 'nvim', 'vi', 'nano', 'micro', 'ssh', 'htop', 'btop', 'top', 'less', 'more', 'man',
           'python', 'python3', 'node', 'bash', 'sh', 'tmux', 'watch', 'tail', 'journalctl', 'su', 'spotify',
           'firefox', 'vlc', 'mpv', 'nemo', 'gnome-terminal', 'fzf', 'ff', 'neofetch', 'zarya-daemon', 'sleep',
           'read', 'ping', 'pet', 'steam', 'alert', 'afk', 'afk-demon', 'breach'}
LEVEL_COL = dict(info='#7B4DFF', ok='#8FD9A8', warn='#F29AB4', crit='#FF5C8A', music='#9D7BFF')
BONE, BODY, HINT, VOIDBG = '#E4E0EA', '#C9C3D6', '#6E6787', (7 / 255, 6 / 255, 13 / 255, 0.94)


def log(msg):
    try:
        with open(LOG, 'a') as f: f.write(time.strftime('%F %T ') + msg + '\n')
    except OSError: pass


def rd(p):
    try:
        with open(p) as f: return f.read()
    except OSError: return ''


def conf():
    c = dict(unit='5', music='1', x='20', y='20', downloads='1', steam='1', games='1', fx='1', fx_fps='30', caption='1', ghost='1', breach_gap='45', screen='1', possess_gap='60',
             hurt='1', stab='0', sudo_nails='0', journal='1', ask='1', form_min='45', descent_gap='180', nails='0', shadow='0', stand_gap='20', laststand='0', horde='1', form='1', reactions='1', caption_fold='0', brain='1')
    c['break'] = '60'
    for line in rd(CONF).splitlines():
        m = re.match(r'\s*([a-z_]+)\s*=\s*(.*?)\s*$', line)
        if m: c[m.group(1)] = m.group(2)
    return c


def set_conf(key, val):
    """d15: change one key in daemon.conf in place (other lines and comments untouched), or append it."""
    lines = rd(CONF).splitlines(); done = False
    for i, ln in enumerate(lines):
        if re.match(rf'\s*{key}\s*=', ln): lines[i] = f'{key}={val}'; done = True
    if not done: lines.append(f'{key}={val}')
    os.makedirs(os.path.dirname(CONF), exist_ok=True)
    with open(CONF + '.tmp', 'w') as f: f.write('\n'.join(lines).rstrip('\n') + '\n')
    os.replace(CONF + '.tmp', CONF)


def rgb(h, a=1.0): return (int(h[1:3], 16) / 255, int(h[3:5], 16) / 255, int(h[5:7], 16) / 255, a)


def cmd_word(cmd):
    w = (cmd or '').split()
    i = 0
    while i < len(w) and (re.match(r'^\w+=', w[i]) or w[i] in ('sudo', 'time', 'nohup', 'nice', 'exec', 'command', 'env') or w[i].startswith('-')): i += 1
    return w[i].split('/')[-1] if i < len(w) else ''


def fmt_dur(s):
    s = int(round(s))
    if s < 60: return f'{s}s'
    if s < 3600: return f'{s // 60}m{s % 60:02d}s'
    return f'{s // 3600}h{s % 3600 // 60:02d}m'


# ---------------- stats ----------------
class Stats:
    def __init__(self):
        self.cpu = self.cpu_t = self.gpu = self.gpu_t = self.vram = self.vram_tot = None
        self.ram = self.ram_tot = None
        self._prev = None
        self._smi = None
        threading.Thread(target=self._gpu_loop, daemon=True).start()

    def _gpu_loop(self):
        # one long-running nvidia-smi streaming every 2 s: no process spawn per sample
        while True:
            try:
                self._smi = subprocess.Popen(['nvidia-smi', '--query-gpu=utilization.gpu,temperature.gpu,memory.used,memory.total',
                                              '--format=csv,noheader,nounits', '-lms', '2000'],
                                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
                for line in self._smi.stdout:
                    p = [x.strip() for x in line.split(',')]
                    if len(p) == 4 and all(x.replace('.', '').isdigit() for x in p):
                        self.gpu, self.gpu_t, self.vram, self.vram_tot = int(p[0]), int(p[1]), int(p[2]), int(p[3])
            except FileNotFoundError:
                log('stats: nvidia-smi not found, GPU line off'); return
            except Exception as e:
                log(f'stats: nvidia-smi stream ended: {e}')
            time.sleep(10)

    def sample(self):
        f = rd('/proc/stat').split('\n', 1)[0].split()[1:]
        if f:
            v = list(map(int, f)); idle = v[3] + v[4]; tot = sum(v)
            if self._prev:
                dt, di = tot - self._prev[0], idle - self._prev[1]
                self.cpu = max(0, min(100, round(100 * (dt - di) / dt))) if dt else self.cpu
            self._prev = (tot, idle)
        for h in glob.glob('/sys/class/hwmon/hwmon*'):
            name = rd(h + '/name').strip()
            if name in ('k10temp', 'coretemp'):
                for l in sorted(glob.glob(h + '/temp*_label')):
                    if rd(l).strip() in ('Tctl', 'Tdie', 'Package id 0'):
                        try: self.cpu_t = int(rd(l.replace('_label', '_input'))) // 1000
                        except ValueError: pass
                        break
        mi = dict(re.findall(r'^(\w+):\s+(\d+)', rd('/proc/meminfo'), re.M))
        if 'MemTotal' in mi:
            t, a = int(mi['MemTotal']), int(mi['MemAvailable'])
            self.ram, self.ram_tot = (t - a) / 1048576, t / 1048576

    def lines(self):
        out = []
        c = f'CPU {self.cpu if self.cpu is not None else "?"}%'
        if self.cpu_t is not None: c += f' · {self.cpu_t}°'
        out.append(c)
        if self.gpu is not None:
            out.append(f'GPU {self.gpu}% · {self.gpu_t}° · VRAM {self.vram / 1024:.1f}/{self.vram_tot / 1024:.1f} GB')
        if self.ram is not None:
            out.append(f'RAM {self.ram:.1f}/{self.ram_tot:.1f} GB')
        return out

    def hot(self):
        return (self.cpu_t or 0) >= 85 or (self.gpu_t or 0) >= 83


# ---------------- Spotify Web API (opt-in "up next") ----------------
def spotify_next():
    """First item of the user's queue, or None. Token written by zarya-spotify-login (PKCE, no secret)."""
    import json, urllib.request, urllib.parse
    try:
        tok = json.load(open(SPOT_TOKEN))
    except (OSError, ValueError):
        return None
    try:
        if time.time() > tok.get('expires', 0) - 60:
            data = urllib.parse.urlencode(dict(grant_type='refresh_token', refresh_token=tok['refresh_token'],
                                               client_id=tok['client_id'])).encode()
            req = urllib.request.Request(SPOT_ACCOUNTS + '/api/token', data=data,
                                         headers={'Content-Type': 'application/x-www-form-urlencoded'})
            r = json.load(urllib.request.urlopen(req, timeout=8))
            tok['access_token'] = r['access_token']; tok['expires'] = time.time() + int(r.get('expires_in', 3600))
            if r.get('refresh_token'): tok['refresh_token'] = r['refresh_token']
            fd = os.open(SPOT_TOKEN, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, 'w') as f: json.dump(tok, f)
        req = urllib.request.Request(SPOT_API + '/v1/me/player/queue', headers={'Authorization': 'Bearer ' + tok['access_token']})
        q = json.load(urllib.request.urlopen(req, timeout=8)).get('queue') or []
        if not q: return None
        it = q[0]
        who = ', '.join(a.get('name', '') for a in it.get('artists', [])) or (it.get('show') or {}).get('name', '')
        return it.get('name', '?'), who
    except Exception as e:
        log(f'music: up next failed: {e}')
        return None


# ---------------- media players (MPRIS): Spotify, Firefox, Chrome… ----------------
class Music:
    """d4: watches every org.mpris.MediaPlayer2.* player. Spotify keeps the track reports; the active player
    (Spotify when it plays, else whichever plays) drives the dance, the stats and the mouse controls."""
    PREFIX = 'org.mpris.MediaPlayer2.'
    SPOTIFY = 'org.mpris.MediaPlayer2.spotify'

    def __init__(self, on_track):
        self.on_track = on_track; self.p = {}; self.last_active = None
        try:
            self.conn = Gio.bus_get_sync(Gio.BusType.SESSION, None)
            self.conn.signal_subscribe('org.freedesktop.DBus', 'org.freedesktop.DBus', 'NameOwnerChanged', '/org/freedesktop/DBus',
                                       None, Gio.DBusSignalFlags.NONE, self._owner, None)
            names = self.conn.call_sync('org.freedesktop.DBus', '/org/freedesktop/DBus', 'org.freedesktop.DBus', 'ListNames', None,
                                        GLib.VariantType('(as)'), Gio.DBusCallFlags.NONE, -1, None).unpack()[0]
            for n in names: self._add(n)
        except GLib.Error as e:
            self.conn = None; log(f'music: no session bus: {e.message}')

    def _owner(self, conn, sender, path, iface, sig, params, *_):
        name, old, new = params.unpack()
        if new: self._add(name)
        elif name in self.p:
            self.p.pop(name, None); log(f'music: {self.short(name)} closed')

    def _add(self, name):
        if not name.startswith(self.PREFIX) or name in self.p or 'playerctld' in name: return
        self.p[name] = dict(name=name, proxy=None, status=None, meta={}, track=None, since=time.time(), pos=None, pos_at=0)
        Gio.DBusProxy.new(self.conn, Gio.DBusProxyFlags.DO_NOT_AUTO_START, None, name, '/org/mpris/MediaPlayer2',
                          'org.mpris.MediaPlayer2.Player', None, self._ready, name)

    def _ready(self, src, res, name):
        try: px = Gio.DBusProxy.new_finish(res)
        except GLib.Error as e: log(f'music: proxy {name} failed: {e.message}'); return
        if name not in self.p: return
        self.p[name]['proxy'] = px
        px.connect('g-properties-changed', lambda *a: self._read(name, True))
        log(f'music: {self.short(name)} found')
        self._read(name, False)

    @staticmethod
    def short(name): return name[len(Music.PREFIX):].split('.')[0]

    def _read(self, name, announce):
        r = self.p.get(name)
        if not r or not r['proxy']: return
        st = r['proxy'].get_cached_property('PlaybackStatus'); md = r['proxy'].get_cached_property('Metadata')
        old = r['status']; r['status'] = st.unpack() if st else None
        r['meta'] = md.unpack() if md else {}
        if r['status'] == 'Playing' and old != 'Playing': r['since'] = time.time()
        if r['status'] == 'Playing': self.last_active = name
        tid = r['meta'].get('mpris:trackid') or r['meta'].get('xesam:url') or r['meta'].get('xesam:title')
        if tid and tid != r['track']:
            r['track'] = tid; r['pos'] = None; r['started'] = time.time()
            if announce and name == self.SPOTIFY and r['status'] == 'Playing' and ':ad:' not in str(tid):
                self.on_track(self.title(r), self.artist(r))

    def active(self):
        """Spotify if it plays, else the player that started playing last, else the last one that played."""
        sp = self.p.get(self.SPOTIFY)
        if sp and sp['status'] == 'Playing': return sp
        playing = [r for r in self.p.values() if r['status'] == 'Playing']
        if playing: return max(playing, key=lambda r: r['since'])
        if self.last_active in self.p: return self.p[self.last_active]
        return sp

    def title(self, r=None):
        r = r or self.active(); return ((r or {}).get('meta') or {}).get('xesam:title') or '?'
    def artist(self, r=None):
        r = r or self.active(); return ', '.join(((r or {}).get('meta') or {}).get('xesam:artist') or []) or ''
    def artists(self, r=None):
        r = r or self.active(); return [a for a in (((r or {}).get('meta') or {}).get('xesam:artist') or []) if a]
    def album(self, r=None):
        r = r or self.active(); return ((r or {}).get('meta') or {}).get('xesam:album') or ''
    def playing(self):
        r = self.active(); return bool(r and r['status'] == 'Playing')
    def trackinfo(self, r=None):
        """(trackid, url, length in s) of the active track."""
        r = r or self.active(); md = (r or {}).get('meta') or {}
        return str(md.get('mpris:trackid') or ''), str(md.get('xesam:url') or ''), (md.get('mpris:length') or 0) / 1e6
    def short_active(self):
        r = self.active(); return Music.short(r['name']) if r else ''
    def position(self):
        p = self.progress(); ln = self.trackinfo()[2]
        return p * ln if (p is not None and ln) else None

    def progress(self):
        """0..1 through the current track (MPRIS Position, polled at most every 2 s; local clock in between)."""
        r = self.active()
        if not r or not r['proxy']: return None
        ln = r['meta'].get('mpris:length') or 0
        if not ln: return None
        now = time.time()
        if now - r['pos_at'] > 2:
            r['pos_at'] = now
            try:
                v = self.conn.call_sync(r['name'], '/org/mpris/MediaPlayer2', 'org.freedesktop.DBus.Properties', 'Get',
                                        GLib.Variant('(ss)', ('org.mpris.MediaPlayer2.Player', 'Position')), GLib.VariantType('(v)'),
                                        Gio.DBusCallFlags.NONE, 300, None).unpack()[0]
                r['pos'] = (int(v), now) if v else r['pos']
            except Exception: pass
        if r['pos']:
            us, at = r['pos']; us += (now - at) * 1e6 if r['status'] == 'Playing' else 0
        else:
            us = (now - r.get('started', now)) * 1e6                       # player gives no position: count from the track start
        return max(0.0, min(1.0, us / ln))

    def cmd(self, method):
        r = self.active()
        if r and r['proxy']:
            r['proxy'].call(method, None, Gio.DBusCallFlags.NONE, -1, None, None, None)
            log(f'music: {method} ({self.short(r["name"])})')
