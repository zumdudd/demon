# ДЕМОН · concept + direction: ШУМ (shum) · built with Claude (Anthropic)
# >>> d31 СМЕНА + ИГРА (mint-pack v44)
#   СМЕНА: the way in / out between ДЕМОН and ПОДМЕНЫШ runs zarya-hurt's Morph in his window (h17). The way out picks a ritual
#     from the song: ПРИЗЫВ metal · КУЛЬТ Death Grips / industrial · ЯЗЫЧЕСТВО folk / pagan · ЦИФРА other hard · ГНИЛЬ calm or no song.
#     Изгнать (menu or the 2 s hold) always plays a ritual, even on a calm song.
#   ИГРА: while a game runs (Steam game or a fullscreen window that is not a video) he stays on screen and keeps everything,
#     but takes no input: clicks go through him, no menu, no hold-to-exorcise, no ghost fade. `game_show=0` = hide like before.
import hashlib
MORPH_METAL = ('metal', 'heavy metal', 'thrash metal', 'metalcore', 'deathcore', 'nu metal', 'alternative metal', 'industrial metal',
               'progressive metal', 'groove metal', 'death metal', 'black metal', 'doom metal', 'sludge metal', 'djent', 'mathcore')
MORPH_USER = ('you drove it out', 'you held it down')


def _exit_ritual(self):
    """(ritual, why) for the way out."""
    why = getattr(self, '_exit_why', '') or ''
    user = why in MORPH_USER or why.startswith('preview')
    if not (self.music.playing() and self.mkey):
        if not user: return 'plain', 'no song'
        k = ((self.form.state() if self.form else {}) or {}).get('song') or why
        return ('summon', 'cult', 'pagan')[int(hashlib.md5(k.encode()).hexdigest(), 16) % 3], 'no song: the song it came for'
    r = (self.srule or {}).get('ritual'); tags = dict((self.info or {}).get('tags') or [])
    if r: return r, 'song rule'
    rt = getattr(ZM, 'RITUAL_TAGS', {}) if ZM else {}
    sc = {k: sum(tags.get(w, 0) for w in ws) for k, ws in rt.items()}
    if sc and max(sc.values()) >= 30: b = max(sc, key=sc.get); return b, f'tags ({b})'
    if any('death grips' in a for a in self.song_artists()): return 'cult', 'Death Grips'
    if sum(v for k, v in tags.items() if k in MORPH_METAL) >= 30: return 'summon', 'metal tags'
    try:
        mo, va, _ = self.cur_mode(); hard = bool(ZH.is_hard(mo, va, self.cur_weather()[0], (self.srule or {}).get('peak'), ZM.CALM)) \
            or self.dg_song() or bool(self.brain and self.brain.hard())
    except Exception: hard = False
    if hard: return 'none', 'hard song'
    if user and ZM and hasattr(ZM, 'ritual_for'):
        return ZM.ritual_for(list(tags.items()), f'{self.music.artist()}|{self.music.title()}'), 'you drove it out (fixed pick for this song)'
    return 'plain', 'calm song'


def _exorcise_v44(self, why, force=False):
    self._exit_why = why
    return _exorcise_d30(self, why, force)


def _morph_snap(self):
    return self.ear.ear.snap if self.ear and self.ear_on and self.music.playing() else {}


def _morph_apply(self, rects, ov, hide, now, st):
    """called by draw() last: starts / runs the way in and out. Returns (rects, ov, hide)."""
    if not (ZH and self.hurt and hasattr(ZH, 'Morph')): return rects, ov, hide
    f = self.form; on = self.form_on(); sn = self._morph_snap(); idle = ZD.build(dict(st, mode='idle'))
    if f is not None and on and getattr(f, 'morph_req', None) is not None:            # way in
        f.morph_req = None
        src = getattr(self, '_demon_last', None) or idle
        body, eyes = ZH.form_cells(f, idle, now)
        self.morph = ZH.Morph('in', src, body, now, eyes=eyes, music=bool(sn), why='in')
        log(f'hurt: СМЕНА in ({len(src)} → {len(body)} cells)')
    was = getattr(self, '_was_form', on)
    if f is not None and was and not on:                                              # way out
        rit, why = self.exit_ritual(); body, eyes = getattr(self, '_form_body', None) or ZH.form_cells(f, idle, now)
        self.morph = ZH.Morph('out', body, None, now, eyes=eyes, rit=rit, music=bool(sn), eye_col=st.get('eye') or ZD.C['G'], why=why)
        log(f'hurt: СМЕНА out: {ZH.MORPH_RU.get(rit, rit)} ({why})'); self._exit_why = ''
    self._was_form = on
    m = getattr(self, 'morph', None)
    if m is None:
        if not on and not hide: self._demon_last = [list(r) for r in rects]
        if on and f is not None and now - getattr(self, '_form_body_t', 0) > 20:
            self._form_body = ZH.form_cells(f, idle, now); self._form_body_t = now
        return rects, ov, hide
    live = idle if (m.kind == 'out' and on) else rects                              # a preview while it is in him: him at rest
    r2, ov2, done = m.frame(now, sn, live)
    if done:
        self.morph = None
        if m.kind == 'in' and f is not None: self._form_body = ZH.form_cells(f, idle, now); self._form_body_t = now
        return rects, ov, hide
    return r2, ov2 + [o for o in ov if o[0] == 'shout'], False


def _morph_preview(self, kind, rit='plain'):
    if not (ZH and self.hurt and self.form is not None and hasattr(ZH, 'Morph')): return
    now = time.time(); st = self.state(); idle = ZD.build(dict(st, mode='idle')); sn = self._morph_snap()
    body, eyes = ZH.form_cells(self.form, idle, now)
    if kind == 'in': self.morph = ZH.Morph('in', getattr(self, '_demon_last', None) or idle, body, now, eyes=eyes, music=bool(sn))
    else: self.morph = ZH.Morph('out', body, None, now, eyes=eyes, rit=rit, music=bool(sn), eye_col=st.get('eye') or ZD.C['G'])
    log(f'menu: СМЕНА preview ({kind}{"" if kind == "in" else " " + ZH.MORPH_RU.get(rit, rit)})')


def _morph_menu(self, m):
    """▶ СМЕНА · the change: way in + each way out."""
    pm = Gtk.Menu(); top = Gtk.MenuItem(label='   ▶ СМЕНА · the change'); top.set_submenu(pm); m.append(top)
    top.set_sensitive(bool(ZH and self.hurt and self.form is not None and hasattr(ZH, 'Morph')))
    def add(lab, cb):
        i = Gtk.MenuItem(label=lab); i.connect('activate', lambda *_: cb()); pm.append(i)
    add('ЗАРАЖЕНИЕ · way in, the burst', lambda: self.morph_preview('in'))
    for r, en in (('summon', 'metal: dragged down'), ('cult', 'Death Grips: torn off'), ('pagan', 'folk: burnt off'),
                  ('none', 'other hard: deleted'), ('plain', 'calm: it rots')):
        add(f'{ZH.MORPH_RU[r] if ZH and hasattr(ZH, "MORPH_RU") else r} · way out, {en}', lambda r=r: self.morph_preview('out', r))


Demon.exit_ritual = _exit_ritual
_exorcise_d30 = Demon.exorcise
Demon.exorcise = _exorcise_v44
Demon._morph_snap = _morph_snap
Demon.morph_apply = _morph_apply
Demon.morph_preview = _morph_preview
Demon.morph_menu = _morph_menu
