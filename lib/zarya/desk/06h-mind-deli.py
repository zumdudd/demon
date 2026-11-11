# ДЕМОН · concept + direction: ШУМ (shum) · built with Claude (Anthropic)
# >>> d37 ДЕЛИКАТЕС НА СЛУХ: ДЕЛИКАТЕС by ear (mint-pack v53, top pick 3). ШУМ 2026-11-05: "yes" to the ears version.
#   The grit score alone could not find it (2026-11-05: Death Grips "Hacker" 0.21, "Three Bedrooms" 0.25 at the bottom;
#   SOAD "Know" and Skrillex "BOOSTER" 0.73 on top): the mood model hears guitars as aggressive and Death Grips as calm.
#   So since zarya-mind m4 the ears answer "deli" (Death Grips-grade voice-as-drum + abrasive electronics + hard cuts, heavy
#   dubstep, German hard techno; not metal, not plain EDM). A heard reading with deli = a third way into ДЕЛИКАТЕС, next to
#   the seed and your marks: it counts as hard, up to 2 blasts, the drop smelled 7 s ahead, ДЕМОН stays in on it (resident),
#   no ПРИМАНКА from the reading, and it summons ПОДМЕНЫШ when ДЕМОН is out.
#   The song brain can veto: a studied map with a ДЕЛИКАТЕС score under 0.15 (a soft song) keeps it off.
#   A reading is heard after the song played through once, so it works from the second play. Per song, not per artist.
#   One log line per verdict per song. Settings > «ДЕЛИКАТЕС на слух · by ear» = deli_mind (default 1).
DELI_GRIT_VETO = 0.15


def _deli_mind(self):
    """(True / False, why) ДЕЛИКАТЕС from the heard reading of the song playing now; cached per song for 2 s."""
    if self.cfg.get('deli_mind', '1') == '0': return False, 'off'
    key = self.mind_key()
    if not key: return False, ''
    now = time.time(); hit = getattr(self, '_deli_c', None)
    if hit and hit[0] == key and now - hit[1] < 2.0: return hit[2]
    r = self.mind_reading(key) or {}
    if not (r.get('heard') and r.get('deli')): res = (False, '')
    else:
        m = (getattr(self.brain, 'map', None) or {}) if self.brain else {}
        dl = m.get('delicacy')
        res = (False, f'the song brain says soft (ДЕЛИКАТЕС score {dl})') if dl is not None and dl < DELI_GRIT_VETO else \
              (True, ((r.get('sound') or r.get('about') or '')[:70]) + (f' · score {dl}' if dl is not None else ''))
    self._deli_c = (key, now, res)
    if res[1] and getattr(self, '_deli_said', None) != (key, res[0]):
        self._deli_said = (key, res[0])
        log(f'hurt: ДЕЛИКАТЕС by ear ({res[1]})' if res[0] else f'hurt: ДЕЛИКАТЕС: the ears say yes, {res[1]}: not ДЕЛИКАТЕС')
    return res


_deli_dg0 = Demon.dg_song
def _deli_dg_song(self):
    if _deli_dg0(self): return True
    try: return self.deli_mind()[0]
    except Exception as e:
        if str(e) != getattr(self, '_deli_err', None): self._deli_err = str(e); log(f'hurt: deli by ear error: {e!r}')
        return False


def _deli_tick(self, now):
    """a heard reading that lands while its song plays: ПОДМЕНЫШ's song state turns ДЕЛИКАТЕС (2 blasts)."""
    if now - getattr(self, '_deli_t', 0) < 5.0: return
    self._deli_t = now
    f = self.form
    if f is None or not hasattr(f, 'song') or getattr(f, 'dg', False): return
    key = self.mind_key()
    if not key or getattr(f, 'song_key', None) != key: return
    if self.deli_mind()[0]:
        f.dg = True; f.hard = True; f.det_max = max(f.det_max, 2)
        log(f'hurt: {ZH.FORM_NAME} ДЕЛИКАТЕС by ear mid-song: up to 2 blasts')


_deli_event_tick0 = Demon.event_tick
def _deli_event_tick(self, now):
    _deli_event_tick0(self, now)
    try: self.deli_tick(now)
    except Exception as e:
        if str(e) != getattr(self, '_deli_err2', None): self._deli_err2 = str(e); log(f'hurt: deli tick error: {e!r}')


_deli_menu0 = Demon.mind_menu_line
def _deli_menu_line(self):
    ml = _deli_menu0(self)
    if not ml: return ml
    try: return ml + (' · ДЕЛИКАТЕС by ear' if self.deli_mind()[0] else '')
    except Exception: return ml


Demon.deli_mind = _deli_mind
Demon.dg_song = _deli_dg_song
Demon.deli_tick = _deli_tick
Demon.event_tick = _deli_event_tick
Demon.mind_menu_line = _deli_menu_line
# <<< d37
