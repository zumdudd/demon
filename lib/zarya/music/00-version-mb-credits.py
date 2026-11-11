import os, sys, re, time, math, json, random, struct, subprocess, threading, unicodedata, hashlib
# m3 (mint-pack v14): artist rules match the song's own artist(s) only; a featured / credited artist counts only through a
#     "feat" rule (e.g.  kendrick feat Kendrick Lamar). Love Game (Eminem ft. Kendrick) no longer turns into КЕНДРИК.
#     The ear reports beat steadiness (snap['beat'] 0-1): speech has none, so ДЕМОН stops dancing to talk videos.
# m4 (mint-pack v15): five calm modes from shum's notes (2026-10-26): ПРИВАЛ rest (sits against a rock, smokes; Gats),
#     ТРАССА drive (night road, passing street lights; 505), БОЛЕРО bolero (slow 3-beat sway with a rose; Spanish romantic),
#     БЕГ run (running into the dusk; at the song's hook he stops where someone used to be; Aoi, Koi, Daidaiiro no Hi),
#     НАПЕВ hum (a gentle walk with little notes; instrumentals, Bob Dylan). КАТАРСИС replaces МАКС / breach / drop rings on
#     calm and sad songs (calm modes, or rain / dawn weather): stillness, eye opens, light rises behind him.
#     ПАМЯТЬ gets a song-long arc: memory fragments → someone's outline above him → it fades, the dawn line dims at the end.
#     Song rules: event=ascend[@M:SS] fires a whole-screen event (ВОЗНЕСЕНИЕ); "* — Title" matches any artist.
#     zarya-music show ascend   previews a screen event.
# m5 (mint-pack v16): ОДЕРЖИМОСТЬ, the hard-song peak (МОШ, РАСПАД, jungle, storm weather, or song rule peak=possess):
#     МАКС held → panic (eye darting, trembling, backing off, «НЕТ НЕТ НЕТ») → the ghost in the machine gets in (red glyphs
#     crawl over him, frames tear) → possessed (black body, red outline, slit eye, levitating, horns stretch, head jerks on the
#     hits, «ОН ЗДЕСЬ») → it rips out of him when the song lets go → he collapses, dazed, then gets up. Rituals around it:
#     ПРИЗЫВ summon (sigil circle, candles, a horned shadow rises), КУЛЬТ cult (hooded figures chant), ЯЗЫЧЕСТВО pagan
#     (bonfire, antlers grow, standing stones, red moon), or none (digital only). The Blackwall rift stays for every other
#     song (and for song rule peak=rift). Song rules: peak=possess|rift, ritual=summon|cult|pagan|none.
#     zarya-music possess [RITUAL]   preview it now (a song must be playing).   zarya-music show descend   screen СОШЕСТВИЕ.
# m6 (mint-pack v17): song rule peak=nails (ТРИ ГВОЗДЯ, drawn by zarya-hurt in the desk): hard songs with it skip ОДЕРЖИМОСТЬ;
#     screen events hand / hell / nails (event=…, zarya-music show …); `zarya-music hell` = ПРЕИСПОДНЯЯ now (does not use up the
#     daily one); every "peak:" log line is also queued (PEAK_Q) so the desk can put it in the listening journal.
# m7 (mint-pack v18): ПРЕИСПОДНЯЯ removed (`zarya-music hell` says so). ctx peak=descend (the desk is about to let the hand take
#     him under) also skips ОДЕРЖИМОСТЬ. Screen events: descend (now takes him: ПОДМЕНЫШ), shadow (ТЕНЬ), form / unform (start /
#     drive out ПОДМЕНЫШ now).
# m8 (mint-pack v19): text only: `show descend` is now the lightning that turns him into ПОДМЕНЫШ; nails / hand / shadow are
#     archived (their previews still run).
# m9 (mint-pack v20): screen event stand (ПОСЛЕДНИЙ РУБЕЖ, epic songs): song rule event=stand, zarya-music show stand.
# m10 (mint-pack v21): song rule peak=stand (the dark last stand, inside his window); peak=stand never starts ОДЕРЖИМОСТЬ.
# m11 (mint-pack v22): artist-wide song rules "Artist — * :: peak=stand" (a rule for the song itself wins key by key);
#     zarya-music peak …; zarya-music show with no name lists the animations.

VERSION = 'm13'
HOME = os.path.expanduser('~')
CACHE = f'{HOME}/.cache/zarya-daemon'
CFG = f'{HOME}/.config/zarya'
RULES = f'{CFG}/music-rules.conf'
SONGS = f'{CFG}/music-songs.conf'
LASTFM_KEY = f'{CFG}/lastfm.key'
SPOT_TOKEN = f'{CFG}/spotify-token.json'
STATE = f'{CACHE}/music.json'            # written by the desktop ДЕМОН every 2 s
FORCE = f'{CACHE}/music-force'           # "mode until" (zarya-music try)
CTL_EVENT = f'{CACHE}/ctl-event'         # last control action (the desktop ДЕМОН shows it)
STOP_AT = f'{CACHE}/stop-at'             # "stop music at" (epoch)
INFO_DIR = f'{CACHE}/songs'              # lookup cache, one json per song
CAVA_CONF = f'{CACHE}/cava.conf'
LASTFM_API = os.environ.get('ZARYA_LASTFM_API', 'https://ws.audioscrobbler.com')
LRCLIB_API = os.environ.get('ZARYA_LRCLIB_API', 'https://lrclib.net')
MB_API = os.environ.get('ZARYA_MB_API', 'https://musicbrainz.org')
SPOT_API = os.environ.get('ZARYA_SPOTIFY_API', 'https://api.spotify.com')
SPOT_ACCOUNTS = os.environ.get('ZARYA_SPOTIFY_ACCOUNTS', 'https://accounts.spotify.com')
UA = 'zarya-music/m2 (desktop pet; personal use)'
MODES = ('break', 'memory', 'nod', 'mosh', 'kendrick', 'grips', 'groove', 'epic', 'kawaii', 'rest', 'drive', 'bolero', 'run', 'hum')
CALM = ('memory', 'rest', 'drive', 'bolero', 'run', 'hum')               # m4: КАТАРСИС instead of МАКС / breach / rings
SCREEN_EVENTS = ('ascend', 'descend', 'hand', 'nails', 'shadow', 'form', 'unform', 'stand')    # m6: + hand, nails; m7: + shadow, form, unform (hell gone); m9: + stand
RITUALS = ('summon', 'cult', 'pagan', 'none')
RLABEL = dict(summon='ПРИЗЫВ', cult='КУЛЬТ', pagan='ЯЗЫЧЕСТВО', none='ОДЕРЖИМОСТЬ')
POSSESS_FILE = os.path.expanduser('~/.cache/zarya-daemon/possess-now')        # m5: "ritual until" (preview)
RITUAL_TAGS = {'summon': ['black metal', 'doom metal', 'occult', 'satanic', 'blackgaze', 'dsbm', 'death metal', 'dark ambient', 'witch house', 'atmospheric black metal'],
               'cult': ['experimental hip hop', 'industrial', 'noise', 'industrial hip hop', 'experimental', 'grindcore', 'sludge', 'noise rock', 'digital hardcore'],
               'pagan': ['folk metal', 'pagan metal', 'viking metal', 'pagan', 'dark folk', 'nordic folk', 'slavic', 'neofolk', 'medieval', 'celtic']}
POSSESSED_LINES = ['ОН ЗДЕСЬ', 'МЫ ВНУТРИ', 'ВПУСТИ НАС', 'НЕ ВЫКЛЮЧАЙ', 'ГРОМЧЕ', 'ТЫ СЛЫШИШЬ НАС', 'ОТКРОЙ']


def ritual_for(tags, key=''):
    """m5: the ritual for a hard song from Last.fm tags, else a fixed pick per song (so a song always gets the same one)."""
    d = dict(tags or []); best, bs = None, 0
    for r, words in RITUAL_TAGS.items():
        sc = sum(d.get(w, 0) for w in words)
        if sc > bs: best, bs = r, sc
    if bs >= 30: return best
    return RITUALS[int(hashlib.md5((key or '').encode()).hexdigest(), 16) % 4]
SCREEN_FILE = os.path.expanduser('~/.cache/zarya-daemon/screen-event')
WEATHERS = ('rain', 'clear', 'storm', 'dawn')
LABEL = dict(brk='БРЕЙК', liquid='БРЕЙК · ЖИДКИЙ', jungle='БРЕЙК · ДЖАНГЛ', memory='ПАМЯТЬ', nod='КИВОК', loose='КИВОК · СВОБОДНО',
             mosh='МОШ', kendrick='КЕНДРИК', grips='РАСПАД', groove='ГРУВ', epic='ЭПОС', kawaii='КАВАЙ',
             rest='ПРИВАЛ', drive='ТРАССА', bolero='БОЛЕРО', run='БЕГ', hum='НАПЕВ')
WLABEL = dict(rain='ДОЖДЬ', clear='ЯСНО', storm='ГРОЗА', dawn='РАССВЕТ')
WGLYPH = dict(rain='', clear='', storm='', dawn='')      # Weather Icons in JetBrainsMono Nerd Font
WCOL = dict(rain='#8FB0E8', clear='#F7D58C', storm='#FF5C8A', dawn='#F29AB4')
C = dict(V='#7B4DFF', L='#9D7BFF', D='#07060D', G='#8FD9A8', P='#F29AB4', X='#FF5C8A', B='#E4E0EA', dim='#3A3450',
         R='#FF2244', void='#07060D', orange='#FF7A1A', ember='#FF9A5C', chrome='#B8B4C2', chromeL='#E8E6EE')


PEAK_Q = []                                                    # m6: peaks for the listening journal (the desk drains it)


def log(msg):
    if msg.startswith('peak:'):
        PEAK_Q.append(msg); del PEAK_Q[:-40]
    try:
        with open(f'{HOME}/.cache/zarya-daemon-desk.log', 'a') as f: f.write(time.strftime('%F %T ') + 'music: ' + msg + '\n')
    except OSError: pass


# ======================= rules: artist / title / album -> mode (+ weather) =======================
def norm(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode() or (s or '')
    s = s.lower().replace('$', 's').replace('&', 'and')
    s = re.sub(r'[^a-z0-9぀-ヿ一-鿿]+', ' ', s).strip()
    return re.sub(r'^the ', '', s)


FEAT_RX = re.compile(r'[\(\[]\s*(?:feat\.?|ft\.?|featuring|with|w/)\s+([^\)\]]+)[\)\]]|\s-\s(?:feat\.?|ft\.?)\s+(.+)$|\s(?:feat\.|ft\.)\s+(.+)$', re.I)


def split_names(s):
    return [x.strip() for x in re.split(r'\s*(?:,|&|\band\b|\bx\b|\+|/)\s*', s or '', flags=re.I) if x.strip()]


def base_title(t):
    """Title without "(feat. …)" / "- 2011 Remaster" (remix names stay: a remix is another song)."""
    t = FEAT_RX.sub('', t or '')
    t = re.sub(r'\s-\s[^-]*\b(remaster(ed)?|version|mono|stereo|edit)\b.*$', '', t, flags=re.I)
    return t.strip()


def title_credits(meta):
    """Featured artists named in the title, plus artists packed into one MPRIS string ("A & B")."""
    out = []
    for m in FEAT_RX.finditer(meta.get('title') or ''):
        out += split_names(next(g for g in m.groups() if g))
    for a in meta.get('artists') or []:
        if re.search(r'\s(&|,|feat\.?|ft\.?)\s', a, re.I): out += split_names(re.sub(r'\s(feat\.?|ft\.?)\s', ',', a, flags=re.I))
    return out


def all_artists(meta):
    seen, out = set(), []
    for a in (meta.get('artists') or []) + title_credits(meta) + (meta.get('credits') or []):
        k = norm(a)
        if k and k not in seen: seen.add(k); out.append(a)
    return out


RULE_RX = re.compile(r'(\w+)(?::(\w+))?(?:\+(\w+))?\s+(artist|feat|title|album)\s+(.+)$')


def load_rules():
    out = []
    try: lines = open(RULES, encoding='utf-8').read().splitlines()
    except OSError: return out
    for ln in lines:
        ln = ln.split('#', 1)[0].strip()
        m = RULE_RX.match(ln)
        if m and m.group(1) in MODES:
            w = m.group(3) if m.group(3) in WEATHERS else ''
            out.append((m.group(1), m.group(2) or '', m.group(4), norm(m.group(5)), w))
    return out


def primary_artists(meta):
    """m3: the song's own artists = MPRIS artists (also when packed as "A & B"); not "feat." names or looked-up credits."""
    seen, out = set(), []
    for a in meta.get('artists') or []:
        for x in ([a] + (split_names(re.sub(r'\s(feat\.?|ft\.?)\s.*$', '', a, flags=re.I)) if re.search(r'\s(&|,)\s', a) else [])):
            k = norm(x)
            if k and k not in seen: seen.add(k); out.append(x)
    return out


def match(meta, rules=None):
    """meta: dict(artists=[...], title, album, credits=[...]). Returns (mode, variant, reason, weather) or None.
    m3: "artist" rules match the song's own artist(s); "feat" rules match any credited artist (feat. in the title,
    MusicBrainz / Spotify credits). Then title / album rules."""
    rules = load_rules() if rules is None else rules
    prim = primary_artists(meta); pk = {norm(a) for a in prim}
    for a in prim:                                             # the song's own artist first
        for mode, var, kind, text, w in rules:
            if kind == 'artist' and norm(a) == text:
                return mode, var, f'artist {a}', w
    for a in all_artists(meta):                                # then features, only through "feat" rules
        if norm(a) in pk: continue
        for mode, var, kind, text, w in rules:
            if kind == 'feat' and norm(a) == text:
                return mode, var, f'feat {a}', w
    title, album = norm(meta.get('title')), norm(meta.get('album'))
    for mode, var, kind, text, w in rules:
        if kind == 'title' and text and text in title: return mode, var, f'title has "{text}"', w
        if kind == 'album' and text and text in album: return mode, var, f'album has "{text}"', w
    return None


def teach(artist, mode, var=''):
    """Rewrite the artist's taught line in place (other lines untouched), or append one."""
    try: lines = open(RULES, encoding='utf-8').read().splitlines()
    except OSError: lines = []
    key = norm(artist); new = f'{mode}{":" + var if var else ""} artist {artist}   # taught {time.strftime("%F")}'
    done = False
    for i, ln in enumerate(lines):
        m = re.match(r'\s*(\w+)(?::\w+)?(?:\+\w+)?\s+artist\s+(.+?)\s*(#.*)?$', ln)
        if m and norm(m.group(2)) == key:
            if not done:
                w = re.match(r'\s*\w+(?::\w+)?(\+\w+)?', ln).group(1) or ''           # keep a weather the line had
                lines[i] = new.replace(' artist ', f'{w} artist ', 1); done = True
            else: lines[i] = ''
    if not done: lines.append(new)
    _save(RULES, lines)


def forget(artist):
    try: lines = open(RULES, encoding='utf-8').read().splitlines()
    except OSError: return False
    key = norm(artist); keep = []; hit = False
    for ln in lines:
        m = re.match(r'\s*(\w+)(?::\w+)?(?:\+\w+)?\s+artist\s+(.+?)\s*(#.*)?$', ln)
        if m and norm(m.group(2)) == key: hit = True; continue
        keep.append(ln)
    if hit: _save(RULES, keep)
    return hit


def _save(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + '.tmp', 'w', encoding='utf-8') as f: f.write('\n'.join(lines).rstrip('\n') + '\n')
    os.replace(path + '.tmp', path)


# ---- song rules: ~/.config/zarya/music-songs.conf   "Artist — Title :: mode=nod feel=rain cue=17:00:cursed" ----
def song_key(meta):
    arts = meta.get('artists') or ['']
    return norm(arts[0]) + '|' + norm(base_title(meta.get('title')))


def load_songs():
    out = {}
    try: lines = open(SONGS, encoding='utf-8').read().splitlines()
    except OSError: return out
    for ln in lines:
        if ln.lstrip().startswith('#') or '::' not in ln: continue
        head, _, tail = ln.partition('::')
        a, _, t = head.partition('—')
        if not t: a, _, t = head.partition(' - ')
        k = ('*' if a.strip() == '*' else norm(a)) + '|' + ('*' if t.strip() == '*' else norm(base_title(t)))   # m4: "* — Title"; m11: "Artist — *"
        d = dict(cues=[])
        for kv in tail.split():
            key, _, val = kv.partition('=')
            if key == 'cue':
                m = re.match(r'(\d+):(\d\d)(?::(\w+))?$', val)
                if m: d['cues'].append((int(m.group(1)) * 60 + int(m.group(2)), m.group(3) or 'cursed'))
            elif key in ('mode', 'feel'): d[key] = val
            elif key == 'peak' and val in ('possess', 'rift', 'nails', 'stand'): d['peak'] = val   # m5 (m6: nails, m10: stand)
            elif key == 'ritual' and val in RITUALS: d['ritual'] = val
            elif key == 'event':                                                  # m4: event=ascend[@M:SS]
                nm, _, at = val.partition('@'); m = re.match(r'(\d+):(\d\d)$', at)
                if nm in SCREEN_EVENTS: d['event'] = nm; d['event_at'] = int(m.group(1)) * 60 + int(m.group(2)) if m else None
        out[k] = d
    return out


def song_rule(meta, songs=None):
    songs = load_songs() if songs is None else songs
    own = songs.get(song_key(meta)) or songs.get('*|' + norm(base_title(meta.get('title'))))
    every = songs.get(norm((meta.get('artists') or [''])[0]) + '|*')                  # m11: every song by this artist
    if not every: return own
    r = dict(every); r.update({k: v for k, v in (own or {}).items() if k != 'cues' or v}); return r


ARTIST_ALL = '*'                                                                      # m11: teach_song(dict(artists=[a], title=ARTIST_ALL), …)


def teach_song(meta, **kv):
    """Set mode= / feel= for this song (value '' removes it). Other songs and cue= stay as they are."""
    try: lines = open(SONGS, encoding='utf-8').read().splitlines()
    except OSError: lines = ['# ДЕМОН song rules (zarya-music m2). One song per line:  Artist — Title :: mode=MODE[:var] feel=WEATHER cue=MM:SS[:cursed]',
                             '# Taught by right-click > This song…  (or: zarya-music song MODE / zarya-music feel rain)']
    every = (meta.get('title') or '').strip() == ARTIST_ALL                         # m11
    key = norm((meta.get('artists') or [''])[0]) + '|*' if every else song_key(meta); found = False
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith('#') or '::' not in ln: continue
        head, _, tail = ln.partition('::')
        a, _, t = head.partition('—')
        if norm(a) + '|' + ('*' if t.strip() == '*' else norm(base_title(t))) != key: continue
        parts = [p for p in tail.split() if p.split('=')[0] not in kv]
        parts += [f'{k}={v}' for k, v in kv.items() if v]
        lines[i] = f'{head.rstrip()} :: ' + ' '.join(parts); found = True; break
    if not found:
        parts = [f'{k}={v}' for k, v in kv.items() if v]
        if not parts: return
        lines.append(f'{(meta.get("artists") or ["?"])[0]} — {ARTIST_ALL if every else base_title(meta.get("title"))} :: ' + ' '.join(parts))
    _save(SONGS, lines)


KEYWORDS = [(r'\bliquid\b', 'break', 'liquid'), (r'\b(jungle|breakcore|amen)\b', 'break', 'jungle'),
            (r'\b(dnb|d n b|drum (and|n) bass|neurofunk)\b', 'break', ''), (r'\bphonk\b', 'nod', '')]


def keyword(meta):
    t = norm(f'{meta.get("title", "")} {meta.get("album", "")}')
    for rx, mode, var in KEYWORDS:
        if re.search(rx, t): return mode, var, f'title says {re.search(rx, t).group(0)}', ''
    return None


# ======================= lookups: Last.fm tags, credits, synced lyrics =======================
TAG_WEATHER = {
    'rain': ['sad', 'melancholic', 'melancholy', 'depressing', 'depressive', 'emotional', 'heartbreak', 'lonely', 'dark', 'mellow',
             'somber', 'sombre', 'sorrow', 'gloomy', 'sadcore', 'rainy', 'introspective', 'sad rap', 'emo rap', 'slowcore', 'grief',
             'bleak', 'haunting', 'cold', 'night', 'lofi sad', 'sad songs'],
    'clear': ['happy', 'upbeat', 'party', 'energetic', 'hype', 'fun', 'feel good', 'feel-good', 'summer', 'dance', 'banger',
              'uplifting', 'euphoric', 'turn up', 'sunny', 'catchy', 'groovy', 'joyful'],
    'storm': ['aggressive', 'angry', 'brutal', 'noise', 'industrial', 'rage', 'violent', 'abrasive', 'hardcore punk', 'grindcore',
              'thrash', 'thrash metal', 'horrorcore', 'death metal', 'chaotic', 'harsh noise', 'experimental hip hop', 'noise rock'],
    'dawn': ['nostalgic', 'nostalgia', 'bittersweet', 'hopeful', 'dreamy', 'coming of age', 'sentimental', 'wistful', 'reflective', 'warm'],
}
TAG_MODE = {
    ('epic', ''): ['epic', 'soundtrack', 'orchestral', 'choir', 'film score', 'video game music', 'ost', 'symphonic', 'score', 'anime'],
    ('kawaii', ''): ['cute', 'kawaii', 'j-pop', 'jpop', 'hyperpop', 'bedroom pop', 'denpa', 'idol', 'kawaii future bass', 'city pop'],
    ('break', 'jungle'): ['breakcore', 'jungle', 'drill and bass', 'atmospheric breakcore', 'digicore'],
    ('break', 'liquid'): ['liquid funk', 'liquid drum and bass', 'atmospheric drum and bass', 'liquid dnb'],
    ('break', ''): ['drum and bass', 'dnb', 'neurofunk', 'drumfunk'],
    ('mosh', ''): ['metal', 'heavy metal', 'nu metal', 'thrash metal', 'death metal', 'punk', 'grunge', 'metalcore', 'hardcore punk',
                   'punk rock', 'sludge', 'doom metal', 'black metal', 'speed metal'],
    ('nod', ''): ['hip-hop', 'hip hop', 'rap', 'trap', 'phonk', 'west coast rap', 'conscious hip hop', 'gangsta rap', 'cloud rap'],
    ('bolero', ''): ['bolero', 'balada', 'baladas', 'latin', 'latin pop', 'spanish', 'balada romantica', 'ranchera', 'latin ballad',
                     'bossa nova', 'cancion melodica', 'romantic', 'espanol', 'en espanol'],
    ('hum', ''): ['acoustic', 'folk', 'singer-songwriter', 'folk rock', 'americana', 'chillhop', 'ukulele', 'lo-fi', 'lofi', 'children'],
    ('drive', ''): ['synthwave', 'outrun', 'retrowave', 'dreamwave', 'night drive', 'darkwave'],
    ('run', ''): ['j-rock', 'japanese rock', 'midwest emo', 'math rock', 'emo'],
}
LYRIC_WORDS = {
    'rain': 'cry crying cried tears tear alone lonely goodbye lost pain hurt hurts die dying dead death gone miss missing sorry empty cold '
            'dark broken sad blue grave funeral numb bleed bleeding heartbreak fear afraid sorrow suicide regret ghost nobody never '
            'llorar llanto lagrimas solo sola dolor muerte adios perdido triste',
    'clear': 'party dance dancing money rich win winning celebrate shine fly flying gang bounce lit flex drip champion king alive fun '
             'sunshine summer happy free fiesta bailar feliz',
    'storm': 'kill killing kill hate war fight blood rage burn burning gun guns shoot destroy enemy smash scream violence murder revenge '
             'fire riot odio guerra sangre matar',
    'dawn': 'tomorrow someday rise rising dawn morning hope remember home again forever sunrise believe light heal healing grow '
            'manana esperanza recuerdo',
    'cute': 'love baby sweet cute kiss heart honey darling hug smile candy cuddle sugar amor corazon',
}
_LW = {k: set(v.split()) for k, v in LYRIC_WORDS.items()}


def _get(url, params=None, headers=None, timeout=7):
    import urllib.request, urllib.parse
    if params: url += ('&' if '?' in url else '?') + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r: return json.loads(r.read().decode('utf-8', 'replace'))


def lastfm_key():
    k = os.environ.get('ZARYA_LASTFM_KEY') or ''
    if not k:
        try: k = open(LASTFM_KEY).read().strip()
        except OSError: k = ''
    return k if re.fullmatch(r'[0-9a-f]{32}', k or '') else ''


def lastfm_tags(artist, title):
    key = lastfm_key()
    if not key: return [], 'no key'
    try:
        j = _get(LASTFM_API + '/2.0/', dict(method='track.gettoptags', artist=artist, track=title, autocorrect=1, api_key=key, format='json'))
        if 'error' in j: raise RuntimeError(f'Last.fm error {j.get("error")}: {j.get("message")}')
        tags = [(t['name'].lower(), int(t.get('count') or 0)) for t in (j.get('toptags') or {}).get('tag') or []]
        src = 'track'
        if sum(c for _, c in tags) < 60:                                         # thin track tags: add the artist's
            j = _get(LASTFM_API + '/2.0/', dict(method='artist.gettoptags', artist=artist, autocorrect=1, api_key=key, format='json'))
            at = [(t['name'].lower(), int(t.get('count') or 0) // 2) for t in (j.get('toptags') or {}).get('tag') or []]
            if at: tags = tags + [x for x in at if x[0] not in dict(tags)]; src = 'track+artist' if tags else 'artist'
        return [t for t in tags if t[1] > 0][:25], src
    except Exception as e:
        return [], f'Last.fm failed: {e}'


def tags_read(tags):
    """(weather, (mode, var) or None, why) from Last.fm tags with counts."""
    d = dict(tags); score = {}
    for w, words in TAG_WEATHER.items(): score[w] = sum(d.get(x, 0) for x in words)
    top = sorted(score.items(), key=lambda kv: -kv[1])
    weather = top[0][0] if top[0][1] >= 40 and top[0][1] > 1.3 * top[1][1] else ''
    best, bs = None, 0
    for mv, words in TAG_MODE.items():
        s = sum(d.get(x, 0) for x in words)
        if s > bs: best, bs = mv, s
    hint = best if bs >= 50 else None
    why = ', '.join(t for t, _ in tags[:4])
    return weather, hint, why


def mb_credits(artist, title):
    try:
        q = f'recording:"{base_title(title)}" AND artist:"{artist}"'
        j = _get(MB_API + '/ws/2/recording', dict(query=q, fmt='json', limit=5))
        bt = norm(base_title(title))
        for rec in j.get('recordings') or []:
            if norm(base_title(rec.get('title'))) != bt: continue
            names = [c.get('name') or (c.get('artist') or {}).get('name') for c in rec.get('artist-credit') or []]
            names = [n for n in names if n]
            if any(norm(n) == norm(artist) for n in names): return names, 'MusicBrainz'
        return [], 'MusicBrainz: no match'
    except Exception as e:
        return [], f'MusicBrainz failed: {e}'
