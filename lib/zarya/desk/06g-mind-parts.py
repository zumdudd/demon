# ДЕМОН · concept + direction: ШУМ (shum) · built with Claude (Anthropic)
# >>> d36 ЧАСТИ ПЕСНИ: the song's parts steer ПОДМЕНЫШ (mint-pack v52, AI part 2 piece b). ШУМ 2026-11-05: top pick 1;
#   "yes, send clips" (Gemini hears the song, zarya-mind m3).
#   zarya-mind's reading carries a feel per part of the song ({at, feel}; since m3 heard from clips of the song, before that
#   from the lyrics). From d36 the part playing now steers ПОДМЕНЫШ while it is in him:
#     · calm part (calm / sad / tender / sweet / hollow): no new blast (an arc already running finishes), no ПАСТЬ, no
#       ПРОВАЛ; its mimicry fakes his quiet acts only (ПРИВАЛ, НАПЕВ, ПАМЯТЬ, БОЛЕРО, ТРАССА, groove, nod, СОН, СЛЕЗА),
#     · loud part (hype / angry / defiant / dark): ПАСТЬ at an act's end 1 in 2 (else 1 in 3),
#     · anything else: as before.
#     · ДЕМОН ВЫГЛЯДЫВАЕТ (peek): a calm part with ≥ 30 s of calm ahead, while it lives here (resident) → it rots off (ГНИЛЬ)
#       and ДЕМОН witnesses the calm part; it comes back (СМЕНА) when a loud part starts, ≥ 20 s later. Once per song.
#       A new song hands over to the resident rules (a calm song keeps ДЕМОН, else it comes back 8 s in).
#   A reading from the lyrics only (not heard) loses to the song brain's ears: a studied map section that is aggressive
#   ≥ 0.7 or energy ≥ 0.75 is not a calm part. Each part change is logged once (`hurt: ЧАСТЬ 0:38 sad (heard) → calm …`).
#   Settings > «ЧАСТИ ПЕСНИ из чтения» (mind_parts, default 1) · «ДЕМОН выглядывает» (mind_peek, default 1).
PART_CALM = ('calm', 'sad', 'tender', 'sweet', 'hollow')
PART_LOUD = ('hype', 'angry', 'defiant', 'dark')
PART_POLL = 1.0             # s between looks at the part playing now
PEEK_MIN = 30.0             # s of calm ahead before ДЕМОН peeks out
PEEK_OUT_MIN = 20.0         # s ДЕМОН stays out at least
PART_EARS_AGGR, PART_EARS_ENERGY = 0.7, 0.75
PART_JAW_LOUD = 1 / 2
PART_QUIET_ACTS = ('d:rest', 'd:hum', 'd:memory', 'd:bolero', 'd:drive', 'd:groove', 'd:nod', 's:sleep', 'r:tear')


def _part_now(self, pos=None):
    """(class, feel, at, calm_ahead_s, heard) for the song position now: class 'calm' | 'loud' | None. None without a reading
    with 2+ parts, off, or no position."""
    if self.cfg.get('mind_parts', '1') == '0': return None
    r = self.mind_reading(self.mind_key())
    secs = (r or {}).get('sections') or []
    if len(secs) < 2: return None
    pos = self.music.position() if pos is None else pos
    if pos is None: return None
    i = max((k for k, s in enumerate(secs) if s.get('at', 0) <= pos + 0.5), default=None)
    if i is None: return None
    feel = secs[i].get('feel'); heard = bool(r.get('heard'))
    cls = 'calm' if feel in PART_CALM else 'loud' if feel in PART_LOUD else None
    if cls == 'calm' and not heard and self.brain:                                    # the ears win over the words
        s = self.brain.section(pos) or {}
        if (s.get('aggressive') or 0) >= PART_EARS_AGGR or (s.get('energy') or 0) >= PART_EARS_ENERGY: cls = None
    ahead = 0.0
    if cls == 'calm':
        nxt = next((s['at'] for s in secs[i + 1:] if s.get('feel') not in PART_CALM), None)
        dur = self.music.trackinfo()[2] or 0
        end = nxt if nxt is not None else (dur or secs[-1]['at'] + 30)
        ahead = max(0.0, end - pos)
    return cls, feel, secs[i]['at'], ahead, heard


def _part_tick(self, now):
    if now - getattr(self, '_part_t', 0) < PART_POLL: return
    self._part_t = now
    f = self.form
    if f is None: return
    p = self.part_now() if (self.music.playing() and self.mkey) else None
    cls = p[0] if p else None
    key = self.mkey if self.music.playing() else None
    f.part_feel = cls if self.form_on() else None
    said = (key, p[2] if p else None, cls)
    if p and self.form_on() and getattr(self, '_part_said', None) != said:
        self._part_said = said
        what = {'calm': 'calm: no blasts, no hunts, quiet acts', 'loud': 'loud: hunts 1 in 2'}.get(cls, 'as before')
        log(f'hurt: ЧАСТЬ {int(p[2]) // 60}:{int(p[2]) % 60:02d} {p[1]}{" (heard)" if p[4] else ""} → {what}')
    self.peek_tick(now, p, key)


def _peek_tick(self, now, p, key):
    away = getattr(self, '_res_away', None)
    pk = getattr(self, '_peek', None)
    if away and away[0] == 'peek':                                                   # ДЕМОН is out for a calm part
        if key != (pk or {}).get('key'):                                             # a new song: the resident rules decide
            self._res_away = ('calm', now, now); self._peek = None; log('hurt: peek over: a new song, the resident rules decide'); return
        if p and p[0] == 'loud' and now - pk['t'] >= PEEK_OUT_MIN:
            self._res_away = None; self._res_sent = None; self._peek = None
            song = ZJ.key_of(self.music.artist(), self.music.title()) if ZJ else self.music.title()
            self.form.start(now, 0, f'resident: back for the loud part ({p[1]})', song=song)
        return
    if not (p and p[0] == 'calm' and p[3] >= PEEK_MIN): return
    if self.cfg.get('mind_peek', '1') == '0' or not self.res_on() or not self.form_on() or self.dg_song(): return
    if (pk or {}).get('key') == key or getattr(self, '_peek_done', None) == key: return
    if self.screen_fx is not None or getattr(self, 'morph', None) is not None or self.stand is not None: return
    f = self.form
    if getattr(f, 'arc', None) is not None or getattr(f, 'jaw', None) is not None: return
    self._peek_done = key
    log(f'hurt: peek: a calm part ({p[1]}, {p[3]:.0f} s of it), ДЕМОН looks out for it')
    self.exorcise('a calm part of the song: he peeks out', force=True)
    if not self.form_on():
        self._res_away = ('peek', now, float('inf')); self._peek = dict(key=key, t=now)


_part_event_tick0 = Demon.event_tick
def _part_event_tick(self, now):
    _part_event_tick0(self, now)
    try: self.part_tick(now)
    except Exception as e:
        if str(e) != getattr(self, '_part_err', None): self._part_err = str(e); log(f'hurt: parts tick error: {e!r}')


_part_menu0 = Demon.mind_menu_line
def _part_menu_line(self):
    ml = _part_menu0(self)
    if not ml: return ml
    r = self.mind_reading(self.mind_key()) or {}
    p = None
    try: p = self.part_now()
    except Exception: pass
    return ml + (' · heard' if r.get('heard') else '') + (f' · now {p[1]}' if p else '')


# ---- ПОДМЕНЫШ side (zarya-hurt Form): reads f.part_feel, set by the desk every second
if ZH and hasattr(ZH, 'Form'):
    _part_arc0 = ZH.Form._arc_tick
    def _part_arc(self, now, sn, ctx, pos, music, lvl):
        if getattr(self, 'part_feel', None) == 'calm' and self.arc is None:
            if lvl < 0.78: self.loud_run = now                                        # keep the live arc's loudness clock
            return
        return _part_arc0(self, now, sn, ctx, pos, music, lvl)
    ZH.Form._arc_tick = _part_arc

    _part_jaw0 = ZH.Form._jaw_roll
    def _part_jaw(self, now, music):
        pf = getattr(self, 'part_feel', None)
        if pf == 'calm': return False
        if pf != 'loud': return _part_jaw0(self, now, music)
        old = ZH.JAW_CHANCE; ZH.JAW_CHANCE = max(old, PART_JAW_LOUD)
        try: return _part_jaw0(self, now, music)
        finally: ZH.JAW_CHANCE = old
    ZH.Form._jaw_roll = _part_jaw

    if hasattr(ZH.Form, '_act_pick'):
        _part_act0 = ZH.Form._act_pick
        def _part_act(self, now, music, fail=None):
            if getattr(self, 'part_feel', None) != 'calm' or fail: return _part_act0(self, now, music, fail)
            bag = getattr(self, 'bag', None); self.bag = [self.rng.choice(PART_QUIET_ACTS)]
            try: return _part_act0(self, now, music, False)
            finally: self.bag = bag
        ZH.Form._act_pick = _part_act


Demon.part_now = _part_now
Demon.part_tick = _part_tick
Demon.peek_tick = _peek_tick
Demon.event_tick = _part_event_tick
Demon.mind_menu_line = _part_menu_line
# <<< d36
