class _Demon2:     # mixin of Demon (v35 split; one class in the original)

    def paint_frame(self, cr, rects, ov, hide):
        U, oy = self.U, self.WH - self.SH
        ga = 1 - self.ghost                                                        # ghost on approach
        inv = any(o[0] == 'invert' for o in ov)
        for kind, a in ov: self.overlay(cr, kind, a, U, oy, before=True)
        if not hide:
            for x, y, ww, hh, c, a in rects:
                a *= ga
                if a < 0.05: continue
                col = rgb(c, a)
                if inv: col = (1 - col[0], 1 - col[1], 1 - col[2], a)
                x0, y0 = round(x * U), round(oy + y * U)                         # d5: whole pixels only (no blurred edges)
                cr.set_source_rgba(*col); cr.rectangle(x0, y0, max(1, round((x + ww) * U) - x0), max(1, round(oy + (y + hh) * U) - y0)); cr.fill()
        for kind, a in ov: self.overlay(cr, kind, a, U, oy, before=False)

    def ask_menu(self, ev):
        """d10: one tap: how this song feels (saved as a song rule), or never ask about it."""
        m = Gtk.Menu(); meta = dict(artists=self.music.artists(), title=self.music.title()); key = self.asked_key
        def pick(w_, lab):
            if w_ == 'epic': ZM.teach_song(meta, peak='stand'); self.decide(); log(f'music: you said {meta["title"]} is epic (last stand)')   # d15
            elif w_: ZM.teach_song(meta, feel=w_); self.decide(); log(f'music: you said {meta["title"]} feels {w_}')
            if self.journal and key: self.journal.asked(key, lab)
            self.report_until = 0
        for lab, w_ in (('Sad · rain', 'rain'), ('Hype · clear', 'clear'), ('Aggressive · storm', 'storm'), ('Bittersweet · dawn', 'dawn'),
                        ('Epic · last stand', 'epic'), ('Leave it to the ear', None), ('Never ask about this song', None)):
            i = Gtk.MenuItem(label=lab); i.connect('activate', lambda _i, w_=w_, lab=lab: pick(w_, lab)); m.append(i)
        m.show_all(); m.popup_at_pointer(ev); self._menu = m

    def ask_tick(self, now):
        if not (self.journal and self.cfg.get('ask', '1') != '0') or self.report or self.hidden_fs or self.steam_game: return
        if self.asked_key == ('?', self.mkey) or not self.music.playing() or (self.music.progress() or 0) < 0.5: return
        r = self.journal.cur
        self.asked_key = ('?', self.mkey)
        if not r: return
        why = self.cur_mode()[2] if self.mrule or self.dancing() else None
        if self.journal.should_ask(r['key'], self.srule, why, False):
            self.asked_key = r['key']
            self.post('music', ASK_TITLE, f'{self.music.title()[:40]}\nYOU KEEP PLAYING IT. I STILL CAN\'T READ IT', 'CLICK: TELL ME · IGNORE: LATER', 14)

    def auth_scan(self, now):
        """d10: failed sudo passwords (pam_unix lines in /var/log/auth.log, readable for the adm group) stick in him."""
        try:
            sz = os.path.getsize(AUTH_LOG)
            if self.auth_pos is None or sz < self.auth_pos: self.auth_pos = sz; return
            if sz == self.auth_pos: return
            with open(AUTH_LOG, 'rb') as f: f.seek(self.auth_pos); chunk = f.read(65536).decode('utf-8', 'replace')
            self.auth_pos = sz
        except OSError as e:
            if not self.auth_warned: self.auth_warned = True; log(f'hurt: no sudo nails yet ({AUTH_LOG}: {e.strerror}); needs the adm group (or sudo_nails=0)')
            self.auth_pos = 0; return                                            # if it shows up later, read it from the start
        me = os.environ.get('USER') or os.path.basename(HOME)
        for ln in chunk.splitlines():
            if 'pam_unix(sudo:auth): authentication failure' in ln and re.search(rf'\b(?:ruser|user)={re.escape(me)}\b', ln):
                self.hurt.sudo_fail(now); log('hurt: a failed sudo password')
                if self.journal: self.journal.mark('hurt', 'sudo nail')

    def screen_done_hurt(self, ev):
        if not self.hurt or ev is None: return
        now = time.time(); song = ZJ.key_of(self.music.artist(), self.music.title()) if ZJ and self.music.active() else ''
        if ev.kind == 'hand': self.hurt.after_hand(ev.outcome or 'crushed', now, song)
        elif ev.kind == 'stand' and ev.outcome:                                                               # d13
            self.hurt.blessed = True
            if self.journal: self.journal.mark('peak', 'peak: ПОСЛЕДНИЙ РУБЕЖ')
        elif ev.kind == 'descend' and ev.outcome == 'taken' and self.form:                                     # d11
            try: mins = float(self.cfg.get('form_min', '45'))
            except ValueError: mins = 45
            self.form.start(now, mins, getattr(ev, 'why', ''), song=song)
        if self.journal and ev.outcome: self.journal.mark('hurt', f'{ev.kind}: {ev.outcome}')

    def pet_geo(self, geo):
        ox, oy = self.get_position(); U = self.U
        gx0, gy0 = ox - geo.x, oy + self.WH - self.SH - geo.y
        rects = ZD.build(dict(self.state(), mode='idle', eye=ZD.C['G'], glitch=0, blink=False))
        return dict(cx=gx0 + (ZD.OX + 7) * U, cy=gy0 + (ZD.OY + 5) * U, gx0=gx0, gy0=gy0, U=U, rects=rects, form=self.form,
                    snap=lambda: dict(self.ear.ear.snap) if self.ear and self.ear_on and self.music.playing() else {})     # d12: strikes on the hits

    def screen_event(self, ev, why):
        if ev == 'nails':                                                     # d10: not a screen event, a hunt in his window
            if self.hurt: self.hurt.start_hunt(time.time(), why, preview=(why == 'preview'))
            return
        if ev == 'hell': log('screen: ПРЕИСПОДНЯЯ was removed in v18'); return
        if ev in ('form', 'unform'):                                          # d11 previews
            if not self.form: log('screen: ПОДМЕНЫШ needs zarya-hurt (hurt=1)'); return
            if ev == 'form': self.form.start(time.time(), float(self.cfg.get('form_min', '45') or 45), why)
            else: self.exorcise(why)
            return
        if ev in ('fire', 'blown', 'goose', 'frame', 'tear', 'spark', 'back'):                                  # d16: reactions, inside his window
            self.react.start(ev, time.time(), why); return
        if ev == 'stand':                                                     # d14: inside his window, not a screen scene
            if ZH and self.hurt and hasattr(ZH, 'LastStand'): self.start_stand(time.time(), why, preview=(why == 'preview'))
            return
        if ev in ('hand', 'descend', 'shadow') and not (ZH and self.hurt): log(f'screen: {ev} needs zarya-hurt (hurt=1)'); return
        if self.screen_fx is not None or self.hidden_fs or self.steam_game:
            log(f'screen: {ev} skipped ({"already showing" if self.screen_fx else "fullscreen / game"})'); return
        d = Gdk.Display.get_default(); mon = d.get_primary_monitor() or d.get_monitor(0)
        log(f'screen: {ev} ({why})')
        geo = mon.get_geometry()
        evo = ZH.EVENTS[ev](geo.width, geo.height, self.pet_geo(geo), why) if ZH and ev in ZH.EVENTS else None
        self.screen_fx = ScreenFX(ev, geo, lambda: self.hidden_fs or bool(self.steam_game), self._screen_done, ev_obj=evo,
                                  painter=lambda cr: self.paint_overlay(cr, geo))

    def _screen_done(self):
        sfx = self.screen_fx; self.screen_fx = None
        self.screen_done_hurt(getattr(sfx, 'ev', None))

    # --- d7: Report… ---
    def report_snapshot(self):
        import json
        snap = dict(time=time.strftime('%F %T'), version=VERSION, music_version=getattr(ZM, 'VERSION', None) if ZM else None)
        try: snap['music'] = json.loads(rd(f'{CACHE}/music.json') or '{}')
        except ValueError: snap['music'] = {}
        try:
            mode, var, why = self.cur_mode() if self.music.active() else (None, '', '')
            snap['now'] = dict(title=self.music.title(), artists=self.music.artists(), album=self.music.album(),
                               player=self.music.short_active(), playing=self.music.playing(), position=self.music.position(),
                               mode=mode, variant=var, why=why, weather=list(self.cur_weather()), talk=self.talk)
        except Exception as e: snap['now'] = dict(error=repr(e))
        sn = dict(self.ear.ear.snap) if self.ear else {}
        snap['ear'] = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in sn.items() if k != 'bars'}
        snap['ear_on'] = self.ear_on; snap['ear_err'] = self.ear.err if self.ear else None; snap['ear_fps'] = self.ear.fps if self.ear else None
        snap['window'] = dict(hidden_fs=self.hidden_fs, steam_game=self.steam_game, cover_pet=self.cover_pet, cover_cap=self.cover_cap,
                              ghost_on=self.ghost_on, ghost_allowed=self.ghost_allowed(), fx_enabled=self.fx_enabled(), pinned=self.pinned,
                              caption=self.caption_on(), muted=self.muted(), pos=list(self.get_position()))
        try:
            fs, props = self.fullscreen_active(); snap['window']['active'] = props.strip()[-200:]; snap['window']['active_fullscreen'] = fs
        except Exception: pass
        snap['log'] = rd(LOG).splitlines()[-80:]
        return snap

    def open_report(self):
        if self.rep_dlg: self.rep_dlg.present(); return
        snap = self.report_snapshot()                                   # what was on screen when you clicked
        d = Gtk.Window(title='ДЕМОН · ОТЧЁТ'); self.rep_dlg = d
        d.get_style_context().add_class('zarya-report'); d.set_keep_above(True); d.set_position(Gtk.WindowPosition.CENTER)
        d.set_default_size(470, -1); d.set_resizable(False)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8); box.set_border_width(18); d.add(box)
        def lab(text, cls):
            l = Gtk.Label(label=text, xalign=0); l.set_line_wrap(True); l.get_style_context().add_class(cls); box.pack_start(l, False, False, 0); return l
        lab('ОТЧЁТ', 'rep-title')
        now = snap.get('now') or {}
        song = f"{now.get('title') or '-'} · {', '.join(now.get('artists') or []) or '-'}" if now.get('title') else 'no music playing'
        try: ml = self.mode_label() if now.get('title') else '-'
        except Exception: ml = (now.get('mode') or '-').upper()
        lab(f"{song}\n{ml}  ·  {now.get('why') or ''}", 'rep-dim')
        lab('WHAT HAPPENED', 'rep-head')
        radios, grp = [], None
        for key, text in REPORT_KINDS:
            r = Gtk.RadioButton.new_with_label_from_widget(grp, text); grp = grp or r; radios.append((key, r)); box.pack_start(r, False, False, 0)
        lab('DESCRIPTION', 'rep-head')
        tv = Gtk.TextView(); tv.set_wrap_mode(Gtk.WrapMode.WORD_CHAR); tv.set_left_margin(8); tv.set_right_margin(8); tv.set_top_margin(6)
        sw = Gtk.ScrolledWindow(); sw.set_min_content_height(110); sw.add(tv); sw.get_style_context().add_class('rep-text'); box.pack_start(sw, True, True, 0)
        lab('Saved on this PC with what he was doing. Esc cancels, Ctrl+Enter saves.', 'rep-dim')
        row = Gtk.Box(spacing=8); box.pack_start(row, False, False, 4)
        cancel = Gtk.Button(label='Cancel'); save = Gtk.Button(label='Save'); save.get_style_context().add_class('rep-save')
        row.pack_end(save, False, False, 0); row.pack_end(cancel, False, False, 0)
        def close(*_):
            self.rep_dlg = None; d.destroy()
        def do_save(*_):
            kind = next(k for k, r in radios if r.get_active())
            b = tv.get_buffer(); text = b.get_text(b.get_start_iter(), b.get_end_iter(), False).strip()
            try: rid, n = save_report(kind, text, snap)
            except OSError as e:
                log(f'report: save failed: {e}'); self.post('crit', 'ОТЧЁТ', f'NOT SAVED: {e}', '', 6); close(); return
            log(f'report: saved #{n} {rid} ({kind}): {text[:80]}')
            if self.journal: self.journal.mark('report')
            self.post('ok', 'ОТЧЁТ СОХРАНЁН', f'#{n} · {dict(REPORT_KINDS)[kind]}', 'zarya-report  ·  list / show / export', 5)
            close()
        def key(_w, ev):
            if ev.keyval == Gdk.KEY_Escape: close(); return True
            if ev.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter) and ev.state & Gdk.ModifierType.CONTROL_MASK: do_save(); return True
            return False
        cancel.connect('clicked', close); save.connect('clicked', do_save); d.connect('key-press-event', key); d.connect('delete-event', close)
        d.show_all(); tv.grab_focus(); d.present()
        log('report: dialog open')

    def caption_on(self):
        return self.cfg.get('caption', '1') != '0' and not os.path.exists(f'{CACHE}/caption-off')

    def toggle_caption(self):
        f = f'{CACHE}/caption-off'
        if os.path.exists(f): os.remove(f); log('caption on')
        else: open(f, 'w').close(); log('caption off')

    def like(self):
        tid, url, _ = self.music.trackinfo()
        def go():
            ok, msg = ZM.spotify_like(ZM.spotify_id(tid, url))
            ZM.ctl_event('like', ok=ok, msg=msg)
        threading.Thread(target=go, daemon=True).start()

    def toggle_fx(self):                                                      # d7
        if os.path.exists(FXOFF): os.remove(FXOFF); log('music animations on')
        else: open(FXOFF, 'w').close(); log('music animations OFF (right-click > Music animations to turn back on)')

    def ghost_allowed(self):
        return self.cfg.get('ghost', '1') != '0' and not os.path.exists(GHOSTOFF)

    def toggle_ghost(self):
        if os.path.exists(GHOSTOFF): os.remove(GHOSTOFF); log('fade over apps on')
        else: open(GHOSTOFF, 'w').close(); log('fade over apps off')

    def toggle_mute(self):
        if self.muted(): os.remove(MUTE); log('unmuted')
        else: open(MUTE, 'w').write(str(time.time() + 3600)); log('muted 1 h')

    # --- d4/d5: music modes ---
    def fx_enabled(self):
        return self.ear is not None and not os.path.exists(FXOFF)

    def music_tick(self, now):
        r = self.music.active()
        on = bool(r and r['status'] == 'Playing') and self.fx_enabled() and not (self.hidden_fs and not getattr(self, 'gaming', False))   # d31
        if on:
            self.music_off_at = now
            if not self.ear_on: self.ear_on = True; self.ear.start_ear()
            if self.fx_id is None:
                fps = max(10, min(60, int(self.cfg.get('fx_fps', '30') or 30)))
                self.fx_id = GLib.timeout_add(int(1000 / fps), self._fx_frame)
        elif self.ear_on and now - self.music_off_at > 5:
            self.ear_on = False; self.ear.stop_ear()
        key = (r['name'], r['track']) if r else None
        if key != self.mkey:
            if self.journal:                                                  # d10: one journal line per play
                self.journal.end(now, 'next' if key and self.mkey else 'stop')
                if key: self.journal.start(now, dict(artists=self.music.artists(), title=self.music.title(), album=self.music.album()),
                                           Music.short(r['name']), self.music.trackinfo()[2])
            if self.hurt and key: self.hurt.track_changed(now, ZJ.key_of(self.music.artist(), self.music.title()) if ZJ else self.music.title())
            if self.stand is not None and not self.stand.preview: self.stand = None                    # d14: cape + blade end with the song
            if self.brain:                                                                              # d20: map or study
                try:
                    self.brain.track(now, self.music.artist() if key else None, self.music.title() if key else None, self.music.album(),
                                     self.music.trackinfo()[2], self.music.position(), self.music.playing())
                    self.react.gap_mult = self.brain.weight(self.music.artist(), self.music.title()) if key else 1.0
                except Exception as e: log(f'brain: track error: {e!r}')
                self.bctx = None
            if self.form_on() and self.mkey and hasattr(self.form, 'feed'):                            # d19: ГОЛОД
                try:
                    mode, var, _ = self.cur_mode(); wthr = self.cur_weather()[0]; pk = (self.srule or {}).get('peak')
                    hard = ZH.is_hard(mode, var, wthr, pk, ZM.CALM) and not self.epic_song() or self.dg_song()   # d23
                    soft = not hard and mode in ZM.CALM or (wthr in ('rain', 'dawn') and mode in ('groove', 'nod', 'epic', 'kawaii'))
                    if self.form.feed(now, hard, soft, getattr(self.react, 'prog', 0.5)) == 'starved':
                        self.exorcise('the calm songs starved it', force=True)
                except Exception as e: log(f'hurt: feed error: {e!r}')
            if self.form and hasattr(self.form, 'song'):                                               # d23
                try: self.form.song(now, (ZJ.key_of(self.music.artist(), self.music.title()) if ZJ else self.music.title()) if key else None,
                                    dg=bool(key) and self.dg_song(), steroids=bool(key) and self.steroids_song(), lure=bool(key) and self.lure_song())
                except Exception as e: log(f'hurt: song error: {e!r}')
            if self.cfg.get('reactions', '1') != '0':                                                   # d18: ОБИДА, «ОПЯТЬ?»
                self.react.track_change(now, key)
                if key:
                    day = time.strftime('%F'); pk = (day, key); self.plays = {k: v for k, v in getattr(self, 'plays', {}).items() if k[0] == day}
                    self.plays[pk] = self.plays.get(pk, 0) + 1
                    if self.plays[pk] == 3: self.post('music', 'ОПЯТЬ?', f'{self.music.title()[:40]}\nTHIRD TIME TODAY', '', 5); log('react: ОПЯТЬ? (third play today)')
            self.mkey = key
            if self.ear: self.ear.ear.track_changed(); self.dance = ZM.Dance()
            self.info = None; self.hooks = []
            self.decide(); self.fetch_info()
            DIRECTOR.song(self, key)                                                                    # d28: bus

    def _fx_frame(self):
        if not self.ear_on or (self.hidden_fs and not getattr(self, 'gaming', False)):                 # d31
            self.fx_id = None; return False
        self.queue_draw(); return True

    def meta(self):
        m = dict(artists=self.music.artists(), title=self.music.title(), album=self.music.album())
        if self.info and self.info.get('credits'): m['credits'] = self.info['credits']
        return m

    def fetch_info(self):
        """d5: Last.fm tags, credits (Spotify / MusicBrainz), LRCLIB lyrics, in the background, cached per song."""
        if not ZM or not self.music.active() or not self.music.artists(): return
        meta = self.meta(); key = ZM.song_key(meta); self.info_key = key
        tid, url, ln = self.music.trackinfo()
        sid = ZM.spotify_id(tid, url) if self.music.short_active() == 'spotify' and os.path.exists(SPOT_TOKEN) else None
        def go():
            try: info = ZM.lookup(meta, ln, sid)
            except Exception as e: log(f'music: lookup failed: {e!r}'); return
            GLib.idle_add(self._got_info, key, info)
        threading.Thread(target=go, daemon=True).start()

    def _got_info(self, key, info):
        if key == self.info_key:
            self.info = info; self.decide()
            try: self.hooks = ZM.hooks(info.get('lyrics') or [], self.music.title()) if hasattr(ZM, 'hooks') else []
            except Exception as e: self.hooks = []; log(f'music: hooks: {e!r}')
            if self.hooks: log(f'music: hooks at ' + ', '.join(f'{int(x) // 60}:{int(x) % 60:02d}' for x in self.hooks))
        return False

    def decide(self):
        """Body: song rule > artist / title / album rule (credits count) > title keyword > Last.fm tag hint > the ear.
        Weather: song feel > rule weather > Last.fm tags > lyrics (per section when timed) > none."""
        self.mrule = None; self.srule = None
        if not ZM or not self.music.active(): return
        m = self.meta()
        try:
            self.srule = ZM.song_rule(m)
            r = ZM.match(m) or ZM.keyword(m)
            if self.srule and self.srule.get('mode'):
                mo, _, va = self.srule['mode'].partition(':')
                if mo in ZM.MODES: self.mrule = (mo, va, 'taught for this song', r[3] if r else '')
            if not self.mrule and r: self.mrule = r
            if not self.mrule and self.info and self.info.get('tag_mode'):
                mo, va = self.info['tag_mode']; self.mrule = (mo, va, f'Last.fm tags ({self.info.get("tag_why", "")})', '')
        except Exception as e: log(f'music: rules: {e!r}')
        if self.mrule: log(f'music: mode {self.mrule[0]}{":" + self.mrule[1] if self.mrule[1] else ""} for {m["artists"][:1]} - {m["title"]} ({self.mrule[2]})')

    def cur_weather(self):
        """(weather, why)"""
        if not ZM: return '', ''
        if self.srule and self.srule.get('feel') in ZM.WEATHERS: return self.srule['feel'], 'taught for this song'
        if self.mrule and len(self.mrule) > 3 and self.mrule[3]: return self.mrule[3], self.mrule[2]
        sw = self.section_lyrics()                                                  # d21: the lyrics of this map section
        if sw: return sw, 'the lyrics of this section'
        if self.brain:                                                              # d20: the sound models
            bw = self.brain.weather()
            if bw[0]: return bw
        inf = self.info or {}
        if inf.get('tag_weather'): return inf['tag_weather'], f'Last.fm tags ({inf.get("tag_why", "")})'
        lyr = inf.get('lyrics') or []
        if lyr:
            pos = self.pos_ctx
            sec = ZM.lyric_section(lyr, pos) if pos is not None else ''
            if sec: return sec, 'the lyrics right now'
            if inf.get('lyric_weather'): return inf['lyric_weather'], 'the lyrics'
        return '', ''

    def section_lyrics(self):
        """d21: weather from the lyric lines inside the current map section (same word test as zarya-music), cached per section."""
        b = self.bctx; lyr = (self.info or {}).get('lyrics') or []
        if not (self.brain and b and b.get('t0') is not None and lyr and hasattr(ZM, 'lyric_scores')): return ''
        k = (self.mkey, b['sec'])
        if getattr(self, 'slyr', (None, ''))[0] == k: return self.slyr[1]
        lines = [l for l in lyr if b['t0'] <= l[0] < b['t1']]; w = ''
        if len(lines) >= 2:
            sc = ZM.lyric_scores(lines); sc.pop('cute', None)
            kk, v = max(sc.items(), key=lambda kv: kv[1])
            w = kk if v >= 2 and v > sorted(sc.values())[-2] else ''
        self.slyr = (k, w); return w

    def cur_mode(self):
        """(mode, variant, reason)"""
        if self.force and time.time() < self.force[2]: return self.force[0], self.force[1], 'zarya-music try'
        hint = self.brain.mode(ZM.TAG_MODE) if (self.brain and not self.mrule and hasattr(self.brain, 'mode') and ZM) else None   # d21
        if self.mrule: mode, var, why = self.mrule[:3]
        elif hint: mode, var, why = hint
        else:
            g = self.ear.ear.auto if self.ear else None
            mode, var, why = (g[0], g[1], 'the sound') if g else ('groove', '', 'listening…')
        if mode == 'kendrick' and not var: var = ZM.kendrick_variant(self.music.album())
        return mode, var, why

    def mode_label(self, weather=True):
        if self.form_on() and not self.form.mimic_on(time.time()): return self.form.label()      # d11 / d19
        mode, var, _ = self.cur_mode()
        key = var if mode == 'break' and var in ('liquid', 'jungle') else 'loose' if var == 'loose' else 'brk' if mode == 'break' else mode
        lab = ZM.LABEL.get(key, mode.upper())
        w = self.cur_weather()[0] if weather else ''
        return lab + (f' · {ZM.WLABEL[w]}' if w else '')

