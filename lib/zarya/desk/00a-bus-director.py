# ДЕМОН · concept + direction: ШУМ (shum) · built with Claude (Anthropic)
# >>> d28 bus + director (mint-pack v36)
# BUS: every log line and every decision also goes, as one JSON line, to ~/.cache/zarya/bus-YYYYmmdd.jsonl with the song
#      and the second in it. This is what the digest (v37) and Claude read through the bridge. 14 days kept. bus=0 turns it off.
# DIRECTOR: holds the "when" rules. First slice (v36): the reaction gates (reactions off, ПОДМЕНЫШ here, the stand fighting,
#      one at a time, the gap × song weight, too early in the song). Same decisions as d27; what changed is that a reaction
#      that wanted to fire and was held back now says why (kind "skip", once per song per reaction and reason).
import json as _json

BUS_DIR = f'{HOME}/.cache/zarya'
BUS_KEEP_DAYS = 14
_log_file = log                                                            # d27 file logger (00-version-music.py)


class Bus:
    def __init__(self):
        self.on = True; self.ctx = None; self.err = None; self.day = None; self.path = None

    def attach(self, demon):
        self.on = demon.cfg.get('bus', '1') != '0'
        self.ctx = demon
        if self.on: self.prune()

    def prune(self):
        try:
            cut = time.time() - BUS_KEEP_DAYS * 86400
            for p in glob.glob(f'{BUS_DIR}/bus-*.jsonl'):
                if os.path.getmtime(p) < cut: os.remove(p)
        except OSError: pass

    def where(self):
        """(song, second) from the demon, never raises; no song while nothing plays."""
        d = self.ctx
        if d is None or not getattr(d, 'mkey', None): return None, None
        try:
            song = f'{d.music.artist() or "?"} — {d.music.title() or "?"}'
            pos = d.music.position()
            return song, (round(pos, 1) if pos is not None else None)
        except Exception: return None, None

    def emit(self, kind, msg='', **data):
        if not self.on: return
        now = time.time(); song, sec = self.where()
        rec = dict(t=round(now, 2), at=time.strftime('%T', time.localtime(now)), kind=kind)
        if msg: rec['msg'] = msg
        if song: rec['song'] = song
        if sec is not None: rec['sec'] = sec
        if data: rec.update(data)
        day = time.strftime('%Y%m%d', time.localtime(now))
        if day != self.day: self.day = day; self.path = f'{BUS_DIR}/bus-{day}.jsonl'
        try:
            os.makedirs(BUS_DIR, exist_ok=True)
            with open(self.path, 'a', encoding='utf-8') as f: f.write(_json.dumps(rec, ensure_ascii=False) + '\n')
        except (OSError, TypeError, ValueError) as e:
            if str(e) != self.err: self.err = str(e); _log_file(f'bus: not written: {e!r}')


BUS = Bus()
_KIND = ('react', 'hurt', 'screen', 'brain', 'classes', 'music', 'peak', 'journal', 'report', 'menu', 'skip', 'director')


def log(msg):
    """d28: the d27 file log + the same line on the bus (kind = the line's prefix)."""
    _log_file(msg)
    try:
        head = msg.split(':', 1)[0].strip().lower() if ':' in msg[:14] else ''
        BUS.emit(head if head in _KIND else 'log', msg)
    except Exception: pass


if ZM is not None and hasattr(ZM, 'log'):                                 # zarya-music writes the same file itself
    _zm_log = ZM.log
    def _zm_bus_log(msg, _f=_zm_log):
        _f(msg)
        try: BUS.emit('peak' if msg.startswith('peak:') else 'music', msg)
        except Exception: pass
    ZM.log = _zm_bus_log


class Director:
    """d28: one place for "may this fire now". v36 holds the reaction rules; the rest moves here in later packs."""
    def __init__(self):
        self.noted = set(); self.key = None

    def _note(self, key, name, why, **data):
        if key != self.key: self.key = key; self.noted = set()
        k = (name, why)
        if k in self.noted: return
        self.noted.add(k)
        _log_file(f'director: skipped {name}: {why}')
        BUS.emit('skip', name=name, why=why, **data)

    def song(self, d, key):
        """a song starts (or the music stops), with ДЕМОН's first read of it (the map / Last.fm tags may still be coming)."""
        if not key: BUS.emit('song_end'); return
        try:
            mo, va, _ = d.cur_mode()
            BUS.emit('song_start', mode=mo + (f':{va}' if va else ''), weather=d.cur_weather()[0], epic=bool(d.epic_song()),
                     deli=bool(d.dg_song()), lure_mark=bool(d.in_class('lure', LURE_SEED)), weight=getattr(d.react, 'gap_mult', 1.0),
                     changeling=bool(d.form_on()))
        except Exception as e: BUS.emit('song_start', error=repr(e)[:120])

    # ---- reactions, outer gate (was inline in Demon.tick, d16-d23): None = may run
    def react_outer(self, d):
        if d.cfg.get('reactions', '1') == '0': return 'reactions are off (Settings)'
        if not d.dancing(): return 'not dancing'
        if d.form_on(): return 'ПОДМЕНЫШ is here (its own moves)'
        if d.stand is not None and d.stand.phase in ('fight', 'climax'): return 'ПОСЛЕДНИЙ РУБЕЖ is fighting'
        return None

    def react_outer_note(self, d, why):
        if why in ('not dancing', 'reactions are off (Settings)'): return       # nothing to explain: no music / switched off
        self._note(d.mkey, 'reactions', why)

    # ---- reactions, inner gate (was the first line of Reactions.tick after ВОЗНЕСЕНИЕ, d16-d20)
    def react_gate(self, r, now):
        if r.cur: return 'another reaction is playing'
        gap = REACT_GAP * getattr(r, 'gap_mult', 1.0)
        if now - r.last < gap: return f'{REACT_GAP:g} s gap × song weight {getattr(r, "gap_mult", 1.0):g}'
        if r.prog < 0.08: return 'too early in the song (< 8 %)'
        return None

    def react_wanted(self, r, why, now, sn, epic, soft, lvl, ex, mx, drop):
        """Which reactions' moments were there while the gate said no (read-only: no dice, no state)."""
        if why.startswith('too early'): return
        want = []
        if not soft and lvl > 0.75 and now - r.vol_up < 1.2 and 'blown' not in r.done: want.append('blown')
        if soft and 'tear' not in r.done and r.prog > 0.55 and lvl > 0.6 and ex > 0.7: want.append('tear')
        if epic and 'frame' not in r.done and mx > 2.0 and r.prog > 0.5: want.append('frame')
        if epic and 'goose' not in r.done and drop and (sn.get('build', 0) or 0) > 0.3: want.append('goose')
        if not epic and not soft and 'blown' not in r.done and (mx > 1.2 or (drop and lvl > 0.85)): want.append('blown')
        busy = r.cur[0] if r.cur else None
        for k in dict.fromkeys(want):
            if k != busy: self._note(r.key, k, why, level=round(lvl, 2), max_hold=round(mx, 2))


DIRECTOR = Director()
# <<< d28 bus + director
