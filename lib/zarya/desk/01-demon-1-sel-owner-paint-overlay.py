class _Demon1:     # mixin of Demon (v35 split; one class in the original)

    def _sel_owner(self, clip, ev):
        """Text selected in a terminal (drag, double click, Select All): the docks stay frozen for SEL_HOLD s, until the next
        click (a new press writes its own hold) or until a command runs in that terminal."""
        _, p = self.fullscreen_active()
        if 'gnome-terminal' in p.lower():
            now = time.time(); self.sel_at = now; self._hold(now + SEL_HOLD, self.btn1_at if self.btn1 else now - 0.5)
    def motion(self, w, ev):
        sx, sy = ev.x, ev.y
        self._hover(sx < self.SW and sy > self.WH - self.SH)
        return False

    def click(self, w, ev):
        if self.hurt and ev.button == 1 and ev.type in (Gdk.EventType.BUTTON_PRESS, Gdk.EventType._2BUTTON_PRESS, Gdk.EventType._3BUTTON_PRESS) \
                and not (self.bubble_rect and ev.x >= self.SW):                                           # d10
            gx, gy = ev.x / self.U, (ev.y - (self.WH - self.SH)) / self.U
            sfx = self.screen_fx
            if sfx is not None and getattr(sfx, 'ev', None) is not None:              # rescue: single presses count
                if ev.type != Gdk.EventType.BUTTON_PRESS or sfx.ev.click(time.time() - sfx.t0): return True
            if ev.type == Gdk.EventType.BUTTON_PRESS:
                if ev.state & Gdk.ModifierType.SHIFT_MASK and self.cfg.get('stab', '1') != '0':     # Shift+click: you stab him
                    if self.hurt.stab(time.time(), gx, gy):
                        if self.journal: self.journal.mark('hurt', 'stabbed (you)')
                        return True
                elif self.hurt.pull(time.time(), gx, gy):                                       # click a nail: pull it out
                    if self.journal: self.journal.mark('hurt', 'nail pulled out')
                    return True
            elif self.hurt.nails or ev.state & Gdk.ModifierType.SHIFT_MASK: return True      # no "next track" while pulling / stabbing
        if ev.type == Gdk.EventType.BUTTON_PRESS and ev.button == 1 and self.report and self.report[1] == ASK_TITLE \
                and self.bubble_rect and ev.x >= self.SW:
            self.ask_menu(ev); return True
        if ev.type == Gdk.EventType._2BUTTON_PRESS and ev.button == 1 and not (self.bubble_rect and ev.x >= self.SW):
            self.music.cmd('Next'); self.fx = ('poke', time.time()); return True          # d5: double click = next track
        if ev.type != Gdk.EventType.BUTTON_PRESS: return True
        on_bubble = self.bubble_rect and ev.x >= self.SW
        if ev.button == 1:
            if self.ringing: self.stop_ring()
            elif self.report: self.report_until = 0
            elif on_bubble: self.pinned = False
            else:
                self.pinned = not self.pinned; self.fx = ('poke', time.time()); self.glitch = 0.4
        elif ev.button == 2: self.music.cmd('PlayPause'); self.fx = ('poke', time.time())
        elif ev.button == 3: self.menu(ev)
        return True

    def scroll(self, w, ev):
        """d5: scroll = the player's own volume (game / Discord audio untouched); the visor fills like a level meter."""
        step = 5 if ev.direction == Gdk.ScrollDirection.UP else -5 if ev.direction == Gdk.ScrollDirection.DOWN else 0
        if not step or not ZM: return True
        if step > 0: self.react.vol_up = time.time()                             # d18: louder at a peak = СДУЛО
        short = self.music.short_active()
        def go():
            lvl = ZM.volume_step(short, step)
            GLib.idle_add(self._show_vol, lvl)
        threading.Thread(target=go, daemon=True).start()
        return True

    def _show_vol(self, lvl):
        self.vol_show = (lvl, time.time()); log(f'volume: {self.music.short_active()} {lvl}%')
        if self.journal: self.journal.mark('vol')
        return False

    def menu(self, ev):
        m = Gtk.Menu()
        def item(label, cb, menu=None):
            i = Gtk.MenuItem(label=label); i.connect('activate', lambda *_: cb()); (menu or m).append(i); return i
        def sub(label, menu=None):
            sm = Gtk.Menu(); top = Gtk.MenuItem(label=label); top.set_submenu(sm); (menu or m).append(top); return sm
        if ZM and self.music.active() and self.music.artists():
            sm = sub('♪ This song…'); self.song_menu(sm)
            if self.music.short_active() == 'spotify': sm.append(Gtk.SeparatorMenuItem()); item('♥ Like song', self.like, sm)
            if self.brain:                                                                          # d20
                if self.brain.map:
                    item('Song map · ' + ' '.join(SB.get(s['kind'], '?') for s in self.brain.map.get('sections', [])[:14]), lambda: None, sm).set_sensitive(False)
                    item('Study it again', lambda: (os.remove(ZB.map_path(self.brain.key)) if os.path.exists(ZB.map_path(self.brain.key)) else None,
                                                    setattr(self.brain, 'map', None), log('brain: map dropped, studied again next play')), sm)
                else: item('Song map · ' + ('studying it now…' if self.brain.learning() else 'learns it on a full play'), lambda: None, sm).set_sensitive(False)
            ml_ = self.mind_menu_line() if hasattr(self, 'mind_menu_line') else None                    # d35: zarya-mind's reading
            if ml_: item(ml_, lambda: None, sm).set_sensitive(False)
            if self.form is not None:                                                                   # d25: song classes
                ar_ = self.music.artists()[0]; sm.append(Gtk.SeparatorMenuItem())
                mine_ = {(k, v.casefold()) for k, v in self.marks()}
                for kind_, ru_, en_ in (('deli', 'ДЕЛИКАТЕС', 'hits like Death Grips'), ('lure', 'ПРИМАНКА', 'cute + dark')):
                    on_ = ('deli', ar_.casefold()) in mine_ if kind_ == 'deli' else ('lure', ar_.casefold()) in mine_
                    item(f'{ru_} · {"✓ " if on_ else "mark "}{ar_[:22]}  ({en_})', lambda k=kind_, a=ar_: self.toggle_mark(k, a), sm)
            self.teach_menu(sub(f'♪ Mode for {self.music.artists()[0][:24]}'))
        if ZM: self.anim_menu(sub('▶ Animations'))                                                  # d15
        if ZJ: item('ДНЕВНИК · listening diary', lambda: subprocess.Popen([f'{BIN}/zarya-journal', 'diary'], start_new_session=True,
                                                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        if self.form_on(): item(f'Изгнать {ZH.FORM_NAME} · ' + ('again, it held on' if getattr(self.form, 'tries', lambda: 0)() else 'drive it out'),
                                lambda: self.exorcise('you drove it out'))     # d11 / d19
        m.append(Gtk.SeparatorMenuItem())
        se = sub('Settings')                                                                        # d16: every switch, with its state
        ck = lambda on: '  ✓' if on else '  ✗  (off)'
        item('Song info' + ck(self.caption_on()), self.toggle_caption, se)
        item('Song info over windows' + ck(self.cfg.get('caption_fold', '0') != '1'),
             lambda: self.set_opt('caption_fold', '0' if self.cfg.get('caption_fold', '0') == '1' else '1'), se)
        if ZM and self.ear is not None:                                                         # d7: shows the state
            item('Music animations' + ck(self.fx_enabled()), self.toggle_fx, se)
        item('Reactions' + ck(self.cfg.get('reactions', '1') != '0'),
             lambda: self.set_opt('reactions', '0' if self.cfg.get('reactions', '1') != '0' else '1'), se)
        item('Fade over apps' + ck(self.ghost_allowed()), self.toggle_ghost, se)
        item('Song brain (studies songs)' + ck(self.cfg.get('brain', '1') != '0'),
             lambda: self.set_opt('brain', '0' if self.cfg.get('brain', '1') != '0' else '1'), se)
        item('Pin stats' + ck(self.pinned), lambda: setattr(self, 'pinned', not self.pinned), se)
        item('Quiet for 1 hour' if not self.muted() else 'Talk again', self.toggle_mute, se)
        mo = sub('More')
        if ZM:
            st = sub('Stop music in…', mo)
            for mins in (15, 30, 60): item(f'{mins} min', lambda mins=mins: (ZM.ctl(['stop-in', str(mins)]), None), st)
            if os.path.exists(ZM.STOP_AT): item('Cancel', lambda: ZM.ctl(['stop-cancel']), st)
        item('Timer 5 min', lambda: subprocess.Popen([f'{BIN}/zt', '5m'], start_new_session=True), mo)
        if glob.glob(TIMERS + '/*-*'):
            item('Cancel timers', lambda: subprocess.Popen([f'{BIN}/zt', '-c'], start_new_session=True), mo)
        item('Pet in a terminal', lambda: subprocess.Popen(['gnome-terminal', '--', f'{BIN}/zarya-daemon', '--live'], start_new_session=True), mo)
        item('System monitor', lambda: subprocess.Popen(['gnome-system-monitor'], start_new_session=True, stderr=subprocess.DEVNULL), mo)
        if not os.path.exists(SPOT_TOKEN):
            item('Spotify: up next + like…', lambda: subprocess.Popen(['gnome-terminal', '--', f'{BIN}/zarya-spotify-login'], start_new_session=True), mo)
        item(f'ОБ АВТОРЕ · ШУМ · about: made by shum with Claude ({VERSION})', lambda: None, mo).set_sensitive(False)   # d26
        item('Report…', self.open_report)                                                     # d7
        m.append(Gtk.SeparatorMenuItem())
        item('Quit ДЕМОН', Gtk.main_quit)
        menu_skin(self)                                                                         # d29: ПОДМЕНЫШ palette
        gray_menu(m)                                                                            # d16
        m.show_all(); m.popup_at_pointer(ev)
        self._menu = m

    # --- d15: every animation in one list ---
    def anim_menu(self, m):
        def add(lab, cb, on=True):
            i = Gtk.MenuItem(label=lab); i.set_sensitive(on); i.connect('activate', lambda *_: cb()); m.append(i)
        def head(lab):
            i = Gtk.MenuItem(label=lab); i.set_sensitive(False); m.append(i)
        hurt = bool(ZH and self.hurt); playing = self.music.playing()
        head('Reactions · short')
        add('   ▶ ОГОНЬ · catches fire', lambda: self.screen_event('fire', 'preview'))
        add('   ▶ СДУЛО · blown away', lambda: self.screen_event('blown', 'preview'))
        add('   ▶ МУРАШКИ · goosebumps', lambda: self.screen_event('goose', 'preview'))
        add('   ▶ КАДР · freeze frame', lambda: self.screen_event('frame', 'preview'))
        add('   ▶ СЛЕЗА · one tear', lambda: self.screen_event('tear', 'preview'))
        add('   ▶ ИСКРЫ · static', lambda: self.screen_event('spark', 'preview'))
        add('   ▶ ОБИДА · turns his back', lambda: self.screen_event('back', 'preview'))
        m.append(Gtk.SeparatorMenuItem())
        head('Big scenes · play now')
        add('   ▶ ПОСЛЕДНИЙ РУБЕЖ · last stand', lambda: self.screen_event('stand', 'preview'), hurt and hasattr(ZH, 'LastStand'))
        add('   ▶ ПОДМЕНЫШ · the lightning takes him', lambda: self.screen_event('descend', 'preview'), hurt and not self.form_on())
        add('   ▶ ДЕТОНАЦИЯ · it blows up', lambda: self.form.preview(time.time()), hurt and self.form_on() and hasattr(self.form, 'preview'))
        add('   ▶ ПРИМАНКА · the mask', lambda: self.form.lure_preview(time.time()), hurt and self.form_on() and hasattr(self.form, 'lure_preview'))
        if hasattr(self, 'jaw_menu'): self.jaw_menu(m)                                              # d32: each hunt + ПРОВАЛ
        else: add('   ▶ ПАСТЬ · the jaw', lambda: self.form.jaw_preview(time.time(), self.music.playing()), hurt and self.form_on() and hasattr(self.form, 'jaw_preview'))   # d29
        if hasattr(self, 'morph_menu'): self.morph_menu(m)                                          # d31: ▶ СМЕНА
        if hasattr(ZM, 'RITUALS'):
            pm = Gtk.Menu(); top = Gtk.MenuItem(label='   ▶ ОДЕРЖИМОСТЬ' + ('' if playing else '  (needs a song playing)')); top.set_submenu(pm)
            top.set_sensitive(playing); m.append(top)
            for r in ZM.RITUALS:
                i = Gtk.MenuItem(label=ZM.RLABEL.get(r, r) + ('' if r != 'none' else ' · digital only'))
                i.connect('activate', lambda _i, r=r: self.force_possess(r)); pm.append(i)
        add('   ▶ ВОЗНЕСЕНИЕ · whole-screen rise', lambda: self.screen_event('ascend', 'preview'))
        if self.form_on(): add(f'   ✕ Изгнать {ZH.FORM_NAME} · drive it out', lambda: self.exorcise('you drove it out'))
        m.append(Gtk.SeparatorMenuItem())
        head('On their own')
        def tog(lab, key, note=''):
            on = self.cfg.get(key, '1') != '0'
            add(f'   {lab}  {"✓" if on else "✗  (off)"}{note}', lambda: self.set_opt(key, '0' if on else '1'))
        tog('Reactions', 'reactions')
        on = self.cfg.get('laststand', '0') != '0'
        add(f'   ПОСЛЕДНИЙ РУБЕЖ on epic songs  {"✓" if on else "✗  (off)"}', lambda: self.set_opt('laststand', '0' if on else '1'))
        tog('   · with the horde', 'horde')
        tog('ПОДМЕНЫШ on hard songs', 'form')
        tog('ПОДМЕНЫШ ЖИВЁТ ЗДЕСЬ · the face, he shows on calm songs', 'resident')     # d34
        tog('ПРИМАНКА из чтения · the mask from the song reading', 'lure_mind')       # d35
        tog('ЧАСТИ ПЕСНИ из чтения · the song\'s parts steer it', 'mind_parts')        # d36
        tog('ДЕМОН выглядывает · he peeks out on calm parts', 'mind_peek')             # d36
        tog('ДЕЛИКАТЕС на слух · by ear, from the heard reading', 'deli_mind')        # d37

    def set_opt(self, key, val):
        if key == 'brain':                                                          # d20: start / stop at once
            if val == '0' and self.brain: self.brain.finish(time.time(), None); self.brain = None
            elif val != '0' and ZB and not self.brain: self.brain = ZB.Brain()
        try: set_conf(key, val)
        except OSError as e: log(f'config: could not save {key}={val}: {e.strerror}')
        self.cfg[key] = val; log(f'config: {key}={val} (right-click menu)')
        if key == 'laststand' and val == '0' and self.stand is not None and not self.stand.preview: self.stand = None

    def force_possess(self, r):
        os.makedirs(os.path.dirname(ZM.POSSESS_FILE), exist_ok=True)
        with open(ZM.POSSESS_FILE, 'w') as f: f.write(f'{r} {time.time() + 4:.0f}')
        log(f'menu: ОДЕРЖИМОСТЬ preview ({r})')

    # --- d9: ОДЕРЖИМОСТЬ ---
    def ritual(self):
        r = (self.srule or {}).get('ritual')
        if r: return r
        if not hasattr(ZM, 'ritual_for'): return 'none'
        return ZM.ritual_for((self.info or {}).get('tags') or [], f'{self.music.artist()}|{self.music.title()}')

    def take_force_possess(self):
        """zarya-music possess RITUAL writes "ritual until"; hand it to the dance once."""
        if not hasattr(ZM, 'POSSESS_FILE'): return None
        txt = rd(ZM.POSSESS_FILE).split()
        if len(txt) == 2:
            try: until = float(txt[1])
            except ValueError: until = 0
            try: os.remove(ZM.POSSESS_FILE)
            except OSError: pass
            if until > time.time() and txt[0] in ZM.RITUALS: return txt[0]
        return None

    # --- d8: whole-screen events ---
    def event_tick(self, now):
        try: mt = os.path.getmtime(ZM.SCREEN_FILE) if hasattr(ZM, 'SCREEN_FILE') else 0
        except OSError: mt = 0
        if mt > self.ev_seen:                                              # zarya-music show EVENT (preview)
            self.ev_seen = mt
            if now - mt < 6: self.screen_event(rd(ZM.SCREEN_FILE).split()[0] if rd(ZM.SCREEN_FILE).split() else 'ascend', 'preview')
        if self.hurt: self.hurt_tick(now)
        if self.form and self.form.state() and not self.form.active(now): self.exorcise('its time ran out', force=True)     # d11
        ev = (self.srule or {}).get('event')
        if not ev or self.ev_done == self.mkey or not self.music.playing() or not self.fx_enabled(): return
        if self.cfg.get('screen', '1') == '0' or self.hidden_fs or self.steam_game: return
        at = (self.srule or {}).get('event_at'); pos = self.music.position(); prog = self.music.progress()
        sn = self.ear.ear.snap if self.ear else {}
        fire = False
        if at is not None: fire = pos is not None and at <= pos < at + 20
        elif prog is not None:
            peak = (0 <= now - sn.get('drop_t', -99) < 0.5) or sn.get('max_hold', 0) > 1.0 or \
                   (self.dance is not None and getattr(self.dance, 'cath_t', None) is not None and now - self.dance.cath_t < 0.5)
            fire = (prog >= 0.35 and peak) or prog >= 0.7
        if fire: self.ev_done = self.mkey; self.screen_event(ev, f'{self.music.title()[:40]} @ {int(pos or 0) // 60}:{int(pos or 0) % 60:02d}')

    def hurt_tick(self, now):
        """d10: nails on the hits, the hand after the third, ПРЕИСПОДНЯЯ on the biggest moment of a hard song (once a day)."""
        H = self.hurt; sn = self.ear.ear.snap if self.ear and self.ear_on else {}
        H.tick(now, sn, self.music.playing() and self.dancing())
        why = H.take_hand(now) if self.screen_fx is None else None            # d11: wait while another scene runs
        if why:
            if self.cfg.get('screen', '1') != '0' and not (self.hidden_fs or self.steam_game): self.screen_event('hand', f'third nail ({why})')
            else: log('hurt: the hand stays away (fullscreen / game / screen=0)'); H.after_hand('spared', now, '')
        if not self.dancing() or self.screen_fx is not None or H.busy(): return
        if self.stand_tick(now, sn): return                                # d13: epic songs
        hard, peak = self.route
        mh = sn.get('max_hold', 0) or 0
        if not hard and not self.form_on(): return
        screen_ok = self.cfg.get('screen', '1') != '0' and not (self.hidden_fs or self.steam_game)
        if self.form_on():                                                 # d11: ПОДМЕНЫШ: the hardest moments raise ТЕНЬ
            mo, va, _ = self.cur_mode()
            hard_now = ZH.is_hard(mo, va, self.cur_weather()[0], (self.srule or {}).get('peak'), ZM.CALM) or mh > 3.0
            if hard_now and mh > 2.0 and now > self.shadow_gap and screen_ok and self.cfg.get('shadow', '0') == '1':      # d12: archived
                self.shadow_gap = now + 60; self.screen_event('shadow', f'{self.music.title()[:40]}')
            return
        if peak == 'possess' and self.cfg.get('form', '1') != '0' and self.descent_ok(now) and mh > 1.5 and screen_ok and self.ev_done != self.mkey:
            self.ev_done = self.mkey; self.screen_event('descend', f'{self.music.title()[:40]}'); return
        if peak == 'nails' and mh > 1.2 and self.hunted != self.mkey:
            self.hunted = self.mkey; H.start_hunt(now, self.music.title()[:40])

    def stand_tick(self, now, sn):
        """d13: ПОСЛЕДНИЙ РУБЕЖ: ЭПОС songs, once per play, at the climax (held peak, or a drop / big moment past 30 %)."""
        if self.form_on() or self.ev_done == self.mkey or self.cfg.get('screen', '1') == '0' or self.hidden_fs or self.steam_game: return False
        try: gap = float(self.cfg.get('stand_gap', '20')) * 60
        except ValueError: gap = 1200
        if self.cfg.get('laststand', '1') == '0' or now - getattr(self, 'stand_at', 0) < gap or not self.epic_song(): return False
        if self.stand_key == self.mkey: return False                                                     # d14: once per play
        prog = self.music.progress() or 0; lvl = sn.get('level', 0) or 0
        if (prog > 0.12 and lvl > 0.7) or (sn.get('build', 0) or 0) > 0.4 or (sn.get('max_hold', 0) or 0) > 0.5:
            self.stand_at = now; self.start_stand(now, self.music.title()[:40]); return True
        return False

    def epic_song(self):
        """d14: ЭПОС, a stand song rule, or power / symphonic metal in the Last.fm tags."""
        r = self.srule or {}
        if r.get('peak') == 'stand' or r.get('event') == 'stand': return True
        if self.brain and self.brain.epic(): return True                           # d20: style from the sound
        if self.cur_mode()[0] == 'epic': return True
        tags = dict((self.info or {}).get('tags') or [])
        return sum(v for k, v in tags.items() if k in ('power metal', 'symphonic metal', 'symphonic power metal', 'epic metal', 'heroic metal', 'epic power metal', 'melodic power metal')) >= 30

    def start_stand(self, now, why, preview=False):
        self.stand = ZH.LastStand(now, preview=preview, horde=self.cfg.get('horde', '1') != '0')
        self.stand_key = self.mkey; self.stand_phase = 'fight'
        if self.journal: self.journal.mark('peak', 'peak: ПОСЛЕДНИЙ РУБЕЖ')

    def form_on(self):
        return bool(self.form) and self.form.active(time.time())

    def dg_song(self):                                                        # d23 / d25: ДЕЛИКАТЕС (seed + your marks)
        return self.in_class('deli', DELI_SEED)

    def lure_song(self):                                                      # d25: ПРИМАНКА (seed + your marks + the sound)
        if self.in_class('lure', LURE_SEED): return True
        if self.brain and self.cfg.get('lure_auto', '1') != '0' and hasattr(self.brain, 'lure'):
            ok, why = self.brain.lure()
            if ok: log(f'hurt: ПРИМАНКА by sound ({why})')
            return bool(ok)
        return False

    def song_artists(self):
        return [a.casefold().strip() for a in (self.music.artists() or [self.music.artist() or '']) if a]

    def marks(self):
        try: return [ln.strip().split(' ', 1) for ln in open(CLASSES, encoding='utf-8') if ' ' in ln.strip() and not ln.startswith('#')]
        except OSError: return []

    def in_class(self, kind, seed):
        arts = self.song_artists(); mine = {v.casefold() for k, v in self.marks() if k == kind}
        return any(s in a for a in arts for s in seed) or any(a in mine for a in arts)

    def toggle_mark(self, kind, artist):
        a = artist.casefold().strip(); rows = self.marks(); has = [kind, a] in [[k, v.casefold()] for k, v in rows]
        rows = [r for r in rows if not (r[0] == kind and r[1].casefold() == a)] + ([] if has else [[kind, a]])
        try:
            os.makedirs(os.path.dirname(CLASSES), exist_ok=True)
            with open(CLASSES, 'w', encoding='utf-8') as f:
                f.write('# ДЕМОН song classes (right-click > This song…): deli = ДЕЛИКАТЕС, lure = ПРИМАНКА\n')
                for k, v in rows: f.write(f'{k} {v}\n')
        except OSError as e: log(f'classes: not saved: {e}')
        log(f'classes: {"unmarked" if has else "marked"} {a} as {"ДЕЛИКАТЕС" if kind == "deli" else "ПРИМАНКА"}')
        if self.form and hasattr(self.form, 'song'):                                   # applies to the song playing now
            if kind == 'lure': self.form.lure = self.lure_song()
            else: self.form.dg = self.dg_song(); self.form.det_max = max(self.form.det_max, 2) if self.form.dg else self.form.det_max

    def steroids_song(self):                                                  # d23: the megamix, one 22-minute track
        return self.dg_song() and 'steroids' in (self.music.title() or '').casefold()

    def lyric_raw(self):                                                      # d23: the current synced lyric line for КРИК
        pos = self.music.position(); cur = None
        if pos is None: return None
        for t, ln in (self.info or {}).get('lyrics') or []:
            if t <= pos: cur = ln
            else: break
        return cur

    def descent_ok(self, now):
        try: gap = float(self.cfg.get('descent_gap', '180')) * 60
        except ValueError: gap = 10800
        return self.form is not None and now - self.hurt.mem.d.get('last_descent', 0) > gap

    def exorcise(self, why, force=False):
        if self.form and not force and hasattr(self.form, 'resist') and self.form.active(time.time()) and self.form.resist(time.time()):
            if self.journal: self.journal.mark('hurt', f'{ZH.FORM_NAME} held on')
            return                                                                  # d19: СОПРОТИВЛЕНИЕ
        if self.form and self.form.end(time.time(), why):
            self.hurt.expel(time.time())
            if self.journal: self.journal.mark('hurt', f'{ZH.FORM_NAME} left ({why})')

    def paint_overlay(self, cr, geo):
        """d11: his current frame on the screen-event overlay, in front of the scene."""
        if not self.frame: return
        ox, oy = self.get_position()
        cr.save(); cr.translate(ox - geo.x, oy - geo.y); self.paint_frame(cr, *self.frame); cr.restore()

