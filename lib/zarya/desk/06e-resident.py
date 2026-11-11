# ДЕМОН · concept + direction: ШУМ (shum) · built with Claude (Anthropic)
# >>> d34 ПОДМЕНЫШ ЖИВЁТ ЗДЕСЬ (mint-pack v47). ШУМ 2026-11-04 23:34: ПОДМЕНЫШ is the face everywhere except Zarya.
#   resident=1 (default): ПОДМЕНЫШ is his default form and stays until something sends it away (no time limit).
#   ДЕМОН shows only:
#     · on calm songs (calm modes, rain / dawn soft songs, epic songs): after 20 s of a calm song it rots off (ГНИЛЬ) and he
#       witnesses the song; it comes back on the next song that is not calm (not sooner than 60 s after it left),
#     · when ГОЛОД starves to 0: it comes back after resident_rest minutes (default 20),
#     · after Изгнать (menu or the 2 s hold): it comes back after resident_banish minutes (default 30).
#   Every way back in is a normal Form.start, so СМЕНА plays the burst. Every start while resident is open-ended
#   (ДЕЛИКАТЕС and the lightning no longer give it a 45-minute stay that ends on its own).
#   A ДЕЛИКАТЕС song or the lightning still bring it back early. resident=0 in daemon.conf = d33 behaviour.
#   The menu / message skin is on whenever resident=1, also while ДЕМОН shows (06a skin_on).
RES_CALM_HOLD = 20          # s of a calm song before it leaves
RES_MIN_AWAY = 60           # s it stays away after a calm song sent it off
RES_BACK_HOLD = 8           # s a not-calm song must play before it comes back


def _res_on(self):
    return bool(self.form is not None and self.hurt and self.cfg.get('resident', '1') != '0' and self.cfg.get('form', '1') != '0')


def _res_calm(self):
    """(calm, hard) for the song playing now; (None, None) with no song or before the mode is known."""
    if not (self.music.playing() and self.mkey): return None, None
    try:
        mo, va, _ = self.cur_mode(); wt = self.cur_weather()[0]; pk = (self.srule or {}).get('peak')
        calm_ = ZM.CALM if ZM else ()
        soft = bool(self.epic_song() or mo in calm_ or (wt in ('rain', 'dawn') and mo in ('groove', 'nod', 'epic', 'kawaii')))
        hard = bool((ZH.is_hard(mo, va, wt, pk, calm_) and not self.epic_song()) or self.dg_song() or (self.brain and self.brain.hard()))
        return soft and not hard, hard
    except Exception as e:
        if str(e) != getattr(self, '_res_err', None): self._res_err = str(e); log(f'hurt: resident calm check error: {e!r}')
        return None, None


def _res_tick(self, now):
    if not self.res_on(): return
    if self.screen_fx is not None or getattr(self, 'morph', None) is not None or self.stand is not None: return
    calm, hard = self.res_calm()
    key = self.mkey if self.music.playing() else None
    if key != getattr(self, '_res_key', None): self._res_key = key; self._res_since = now      # a new song (or the music stopped)
    held = now - getattr(self, '_res_since', now)
    if self.form_on():
        self._res_away = None
        if calm and held >= RES_CALM_HOLD and getattr(self, '_res_sent', None) != key:
            self._res_sent = key
            log(f'hurt: resident: a calm song, ДЕМОН comes out for it ({(self.music.title() or "")[:40]})')
            self.exorcise('a calm song: he comes out for it', force=True)
            if not self.form_on(): self._res_away = ('calm', now, now + RES_MIN_AWAY)
        return
    away = getattr(self, '_res_away', None)
    if away is None:                                       # left some other way (time, starved, the menu): find out why once
        why = getattr(self, '_res_left_why', '') or ''
        mins = float(self.cfg.get('resident_banish', '30') or 30) if why in MORPH_USER else \
            float(self.cfg.get('resident_rest', '20') or 20) if 'starved' in why else 0
        away = self._res_away = ('user' if why in MORPH_USER else 'starved' if 'starved' in why else 'other', now, now + mins * 60)
        log(f'hurt: resident: it is away ({away[0]}{f", back in {mins:g} min" if mins else ""})')
    kind, t0, until = away
    if now < until: return
    if calm or (calm is None and kind == 'calm' and key is not None): return            # ДЕМОН keeps the calm song
    if key is not None and calm is None: return                                          # mode not known yet
    if key is not None and held < RES_BACK_HOLD: return
    self._res_away = None; self._res_sent = None
    song = (ZJ.key_of(self.music.artist(), self.music.title()) if ZJ else self.music.title()) if key else ''
    self.form.start(now, 0, f'resident: it comes back ({kind})', song=song)


def _res_event_tick(self, now):
    _res_event_tick0(self, now)
    try: self.res_tick(now)
    except Exception as e:
        if str(e) != getattr(self, '_res_err2', None): self._res_err2 = str(e); log(f'hurt: resident tick error: {e!r}')


def _res_exorcise(self, why, force=False):
    was = self.form_on()
    r = _res_exorcise0(self, why, force)
    if was and not self.form_on(): self._res_left_why = why
    return r


_res_form_start0 = ZH.Form.start if ZH and hasattr(ZH, 'Form') else None
def _res_form_start(self, now, minutes, why, song=''):
    d = getattr(ZH, '_RES_DESK', None)
    if d is not None and not d.res_on(): d = None
    if d is not None and minutes > 0:
        why = f'{why}, resident: no time limit'; minutes = 0
    if d is not None: d._res_away = None; d._res_left_why = ''
    return _res_form_start0(self, now, minutes, why, song)


Demon.res_on = _res_on
Demon.res_calm = _res_calm
Demon.res_tick = _res_tick
_res_event_tick0 = Demon.event_tick
Demon.event_tick = _res_event_tick
_res_exorcise0 = Demon.exorcise
Demon.exorcise = _res_exorcise
if _res_form_start0 is not None: ZH.Form.start = _res_form_start
_res_init0 = Demon.__init__
def _res_init(self, *a, **k):
    _res_init0(self, *a, **k)
    try:
        if ZH: ZH._RES_DESK = self
        if not self.res_on(): return
        st = self.form.state()
        if self.form_on() and st.get('until'):                               # a stay from before v47: open-ended now
            st['until'] = 0; self.form.mem.save(); log('hurt: resident: ПОДМЕНЫШ lives here now (its stay has no end)')
        elif not self.form_on():
            self._res_away = ('start', time.time(), time.time() + 3); log('hurt: resident: ПОДМЕНЫШ lives here, it comes in a moment')
    except Exception as e: log(f'hurt: resident start error: {e!r}')
Demon.__init__ = _res_init
# <<< d34
