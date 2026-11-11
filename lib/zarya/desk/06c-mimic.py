# ДЕМОН · concept + direction: ШУМ (shum) · built with Claude (Anthropic)
# >>> d32 МИМИКРИЯ acts + ПАСТЬ hunts menu (mint-pack v45; the hurt side is zarya-hurt h18, hurt/03b-act.py).
#   While ПОДМЕНЫШ fakes him, the desk draws the act it picked instead of the song's own mode: one of the 14 dances, one of
#   his 7 reactions on top of the song's dance, asleep or startled. A failed act (ПРОВАЛ) also ignores the beat: it dances
#   to a song that isn't playing (a slow sway on a hard song, a mosh pit on a calm one).
_MIMIC_REACT = None


def _mimic_mode(self, mode, var, sn, now):
    a = getattr(self.form, 'act', None) if self.form_on() else None
    if not a: return mode, var, sn
    if a['kind'] == 'd' and a['name'] in ZM.MODES:
        mode = a['name']; var = 'base' if mode == 'kendrick' else ''
    if a.get('fail'):                                                      # ПРОВАЛ: the beat it hears is not the song's
        r = random.Random(int(now * 4) + int(a['seed'] * 1e6))
        calm = mode in ZM.CALM or a['name'] in ('sleep', 'tear')
        sn = dict(sn)
        for k in ('kick', 'snare', 'hat'): sn[k] = (r.random() * 0.4 if calm else (0.9 if r.random() < 0.5 else 0.0))
        sn['level'] = 0.2 if calm else 0.9
        sn['punch'] = 0.0 if calm else r.random() * 0.6
        for k in ('drop_t', 'build'): sn.pop(k, None)
    return mode, var, sn


def _mimic_after(self, rects, ov, hide, now, st, sn):
    global _MIMIC_REACT
    a = getattr(self.form, 'act', None) if self.form_on() else None
    if not a or hide: return rects, ov, hide
    e = now - a['t0']
    if a['kind'] == 'r':
        if _MIMIC_REACT is None: _MIMIC_REACT = Reactions()
        fn = getattr(_MIMIC_REACT, '_' + a['name'], None)
        if fn is not None and e < Reactions.DUR.get(a['name'], 6):
            try: rects, ov = fn(rects, ov, e, sn or {}, st.get('eye') or ZD.C['G'])
            except Exception as ex:
                if str(ex) != getattr(self, 'mimic_err', None): self.mimic_err = str(ex); log(f'react: mimic {a["name"]} error: {ex!r}')
    elif a['kind'] == 's':
        rects = ZD.build(dict(st, mode=a['name'], t=e)); ov = [o for o in ov if o[0] != 'shout']
    return rects, ov, hide


def _jaw_menu(self, m):
    on = bool(ZH and self.hurt and self.form_on() and hasattr(self.form, 'jaw_preview'))
    pm = Gtk.Menu(); top = Gtk.MenuItem(label='   ▶ ПАСТЬ · the jaw'); top.set_submenu(pm); top.set_sensitive(on); m.append(top)
    ru = getattr(ZH, 'HUNT_RU', {}) if ZH else {}
    for v, en in (('hunt', 'bites on the kick'), ('stalk', 'it stalks first'), ('fear', 'he sees it coming'),
                  ('miss', 'it misses'), ('slaughter', 'fast and bloody')):
        i = Gtk.MenuItem(label=f'{ru.get(v, v)} · {en}')
        i.connect('activate', lambda _i, v=v: self.form.jaw_preview(time.time(), self.music.playing(), v)); pm.append(i)
    i = Gtk.MenuItem(label='   ▶ ПРОВАЛ · the act fails'); i.set_sensitive(on and hasattr(self.form, 'fail_preview') and self.music.playing())
    i.connect('activate', lambda *_: self.form.fail_preview(time.time(), self.music.playing())); m.append(i)


Demon.mimic_mode = _mimic_mode
Demon.mimic_after = _mimic_after
Demon.jaw_menu = _jaw_menu
# <<< d32
