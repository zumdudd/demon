# ДЕМОН · concept + direction: ШУМ (shum) · built with Claude (Anthropic)
# >>> d35 ПРИМАНКА from the reading (mint-pack v51, AI part 2 piece a). ШУМ 2026-11-05: "lets go for part 2".
#   zarya-mind (m2) reads each song once and caches {about, mood, sections, dark_core, …} in
#   ~/.local/share/zarya/mind/songs/<md5(journal key)>.json. dark_core = "the sound or surface is cute / sweet / bright but
#   the words are dark". From d35 that reading is a third way into ПРИМАНКА, next to your marks and the song brain's ears:
#     · song start: a song already read with dark_core → ПРИМАНКА at once,
#     · mid-song: zarya-mind reads a new song ~30 s in; the desk looks every 5 s and puts the mask on when the reading arrives,
#     · the ears can veto: a studied map that is hard (aggressive ≥ 0.75) with no cute side (happy < 0.35, party < 0.5,
#       no cute style) keeps the mask off (Gemini only sees the words, the map heard the song),
#     · never on a ДЕЛИКАТЕС song.
#   ПРИМАНКА is still drawn only on ПОДМЕНЫШ (binding); it never summons it. Every decision is logged once per song
#   (`hurt: ПРИМАНКА by the reading …` / `… the sound says no …`), so the bus and the digest show it.
#   Settings > «ПРИМАНКА из чтения · from the reading» = lure_mind (default 1). The reading never leaves the PC here.
#   This song… shows the reading's first line (greyed) so you can judge it while the song plays.
import json as _mj, hashlib as _mh
MIND_SONGS = f'{HOME}/.local/share/zarya/mind/songs'
MIND_POLL = 5.0             # s between looks for a reading that arrived mid-song
MIND_CUTE_HAPPY, MIND_CUTE_PARTY, MIND_HARD = 0.35, 0.5, 0.75


def _mind_key(self):
    if not (ZJ and self.music.playing() and self.mkey): return None
    try: return ZJ.key_of(self.music.artist(), self.music.title())
    except Exception: return None


def _mind_reading(self, key):
    """the cached zarya-mind reading for a journal key, or None (re-read only when the file changes)."""
    if not key: return None
    p = f'{MIND_SONGS}/{_mh.md5(key.encode()).hexdigest()}.json'
    try: mt = os.stat(p).st_mtime
    except OSError: return None
    hit = getattr(self, '_mind_c', None)
    if hit and hit[0] == key and hit[1] == mt: return hit[2]
    try: r = _mj.load(open(p, encoding='utf-8'))
    except (OSError, ValueError): return None
    if not isinstance(r, dict) or r.get('key', key) != key: return None
    self._mind_c = (key, mt, r)
    return r


def _mind_sound_no(self):
    """(True, why) when the song brain's map heard a hard song with no cute side; (False, why) when it heard a cute side
    or a soft song; (None, '') without a studied map."""
    b = self.brain; m = (getattr(b, 'map', None) or {}) if b else {}
    mo = m.get('mood') or {}
    if not mo and not m.get('genre'): return None, ''
    g = ' '.join(str(n).lower() for n, *_ in m.get('genre') or [])
    cs = [w for w in getattr(b, 'CUTE_STYLES', ()) if w in g]
    cute = mo.get('happy', 0) >= MIND_CUTE_HAPPY or mo.get('party', 0) >= MIND_CUTE_PARTY or bool(cs)
    hard = mo.get('aggressive', 0) >= MIND_HARD
    why = f"aggressive {mo.get('aggressive', '?')}, happy {mo.get('happy', '?')}, party {mo.get('party', '?')}" + (f', cute styles {cs}' if cs else '')
    return bool(hard and not cute), why


def _mind_lure(self, key=None):
    """(True / False, why) for ПРИМАНКА from the reading of the song playing now. Logs each verdict once per song."""
    if self.cfg.get('lure_mind', '1') == '0': return False, 'off'
    key = key or self.mind_key()
    r = self.mind_reading(key)
    if not r or not r.get('dark_core'): return False, ''
    if self.dg_song(): ok, why = False, 'a ДЕЛИКАТЕС song'
    else:
        no, ears = self.mind_sound_no()
        ok, why = (False, f'the sound says no ({ears})') if no else (True, (r.get('about') or '')[:70] + (f' · ears: {ears}' if ears else ''))
    seen = getattr(self, '_mind_said', None)
    if seen != (key, ok):
        self._mind_said = (key, ok)
        log(f'hurt: ПРИМАНКА by the reading ({why})' if ok else f'hurt: ПРИМАНКА: the reading says dark core, {why}: no mask')
    return ok, why


_mind_lure_song0 = Demon.lure_song
def _mind_lure_song(self):
    if _mind_lure_song0(self): return True
    try: return self.mind_lure()[0]
    except Exception as e:
        if str(e) != getattr(self, '_mind_err', None): self._mind_err = str(e); log(f'hurt: mind lure error: {e!r}')
        return False


def _mind_tick(self, now):
    """a reading that came in after the song started: the mask goes on mid-song (ПОДМЕНЫШ's per-song state is kept)."""
    if now - getattr(self, '_mind_t', 0) < MIND_POLL: return
    self._mind_t = now
    f = self.form
    if f is None or not hasattr(f, 'song') or getattr(f, 'lure', False): return
    key = self.mind_key()
    if not key or getattr(f, 'song_key', None) != key: return
    try: mt = os.stat(f'{MIND_SONGS}/{_mh.md5(key.encode()).hexdigest()}.json').st_mtime
    except OSError: return                                                   # not read yet: look again in 5 s
    if getattr(self, '_mind_tried', None) == (key, mt): return               # this reading already judged for this song
    self._mind_tried = (key, mt)
    ok, _ = self.mind_lure(key)
    if ok:
        f.lure = True; f.cracks = 0; f.face = None; f.face_t = -9; f.mask_off = False
        log(f'hurt: {ZH.FORM_NAME} ПРИМАНКА: the reading came in mid-song, the mask goes on')


_mind_event_tick0 = Demon.event_tick
def _mind_event_tick(self, now):
    _mind_event_tick0(self, now)
    try: self.mind_tick(now)
    except Exception as e:
        if str(e) != getattr(self, '_mind_err2', None): self._mind_err2 = str(e); log(f'hurt: mind tick error: {e!r}')


def mind_menu_line(self):
    """«ЧТЕНИЕ · <about>» for ♪ This song… (greyed), or None."""
    r = self.mind_reading(self.mind_key())
    if not r: return None
    ab = (r.get('about') or '').split('. ')[0].strip().rstrip('.')
    mood = '/'.join(r.get('mood') or [])
    return f'ЧТЕНИЕ · {ab[:60]}{"…" if len(ab) > 60 else ""}' + (f'  ({mood}{" · dark core" if r.get("dark_core") else ""})' if mood else '')


Demon.mind_key = _mind_key
Demon.mind_reading = _mind_reading
Demon.mind_sound_no = _mind_sound_no
Demon.mind_lure = _mind_lure
Demon.lure_song = _mind_lure_song
Demon.mind_tick = _mind_tick
Demon.event_tick = _mind_event_tick
Demon.mind_menu_line = mind_menu_line
# <<< d35
