class _Demon3:     # mixin of Demon (v35 split; one class in the original)

    def speech_tick(self, now):
        """d7: a browser tab with no song match (no credits, no lyrics) only dances once the ear hears a steady beat
        (beat ≥ 0.35 for 4 s; synthetic: music 0.44-0.84, speech 0.05-0.18). Spotify and matched songs always dance. Decided once per track (latched when music)."""
        key = self.mkey
        if key != self.talk_key: self.talk_key = key; self.talk = None; self.beat_since = None
        if self.talk is False or not self.music.playing(): return
        short = (self.music.short_active() or '').lower()
        inf = self.info
        if not short.startswith(BROWSERS) or (inf and (inf.get('credits') or inf.get('lyrics'))):
            if self.talk: log('music: song confirmed, dancing')
            self.talk = False; return
        beat = (self.ear.ear.snap.get('beat') or 0) if self.ear_on else 0
        if beat >= 0.35:
            self.beat_since = self.beat_since or now
            if now - self.beat_since >= 4:
                log(f'music: steady beat ({beat:.2f}) in {short}, dancing'); self.talk = False; return
        else: self.beat_since = None
        if self.talk is None and inf is not None and self.ear_on:
            self.talk = True; log(f'music: talk / video in {short} (no song match, beat {beat:.2f}), not dancing: {self.music.title()[:60]}')

    def dancing(self):
        if not (self.ear_on and self.music.playing()): return False
        if self.talk is not False and (self.music.short_active() or '').lower().startswith(BROWSERS) and not (
                self.info and (self.info.get('credits') or self.info.get('lyrics'))): return False     # d7: not until it's music
        sn = self.ear.ear.snap
        return bool(sn.get('t')) and time.time() - sn['t'] < 1.0

    def write_music_state(self, now):
        if not ZM: return
        r = self.music.active()
        try:
            import json
            mode, var, why = self.cur_mode() if r else (None, '', '')
            w, wwhy = self.cur_weather() if r else ('', '')
            sn = self.ear.ear.snap if self.ear else {}
            inf = self.info or {}
            info = dict(tags=inf.get('tags') or [], credits=inf.get('credits') or [], lyrics_n=len(inf.get('lyrics') or []),
                        lyric_weather=inf.get('lyric_weather'), tag_weather=inf.get('tag_weather'), tag_mode=inf.get('tag_mode'),
                        notes=inf.get('notes') or (['looking up…'] if r and not inf else []))
            j = dict(ts=now, playing=self.music.playing(), player=Music.short(r['name']) if r else None, title=self.music.title(),
                     artists=self.music.artists(), album=self.music.album(), mode=mode, variant=var, reason=why,
                     label=(var if mode == 'break' and var else mode), fx=self.fx_enabled(), weather=w, wreason=wwhy, info=info,
                     talk=self.talk, beat=sn.get('beat'), ghost_allowed=self.ghost_allowed(),
                     bpm=sn.get('bpm'), level=sn.get('level'), subr=sn.get('subr'), wall=sn.get('wall'), section=sn.get('section'),
                     position=self.music.position(), brain=dict(studied=bool(self.brain and self.brain.map), learning=bool(self.brain and self.brain.learning()),
                                                               now=self.bctx) if self.brain else None,
                     ear_err=self.ear.err if self.ear else ('zarya-music missing' if not ZM else 'fx=0 in daemon.conf'))
            with open(f'{CACHE}/music.json.tmp', 'w') as f: json.dump(j, f)
            os.replace(f'{CACHE}/music.json.tmp', f'{CACHE}/music.json')
        except Exception as e: log(f'music.json: {e}')
        try:
            mm, _, until = rd(ZM.FORCE).partition(' ')
            mo, _, va = mm.partition(':')
            self.force = (mo, va, float(until)) if mo in ZM.MODES and float(until) > now else None
        except ValueError: self.force = None

    MODE_OPTS = [('БРЕЙК · liquid', 'break:liquid'), ('БРЕЙК · jungle', 'break:jungle'), ('ПАМЯТЬ', 'memory'), ('КИВОК', 'nod'),
                 ('КИВОК · loose', 'nod:loose'), ('МОШ', 'mosh'), ('КЕНДРИК', 'kendrick'), ('РАСПАД', 'grips'), ('ЭПОС · epic, last stand at the climax', 'epic'),
                 ('КАВАЙ', 'kawaii'), ('ПРИВАЛ · rest, smoke', 'rest'), ('ТРАССА · night drive', 'drive'), ('БОЛЕРО · romantic', 'bolero'),
                 ('БЕГ · run to someone', 'run'), ('НАПЕВ · gentle walk', 'hum'), ('ГРУВ (neutral)', 'groove')]

    def teach_menu(self, sub):
        art = self.music.artists()[0]
        for lab, mv in self.MODE_OPTS:
            mo, _, va = mv.partition(':')
            i = Gtk.MenuItem(label=lab)
            i.connect('activate', lambda _w, mo=mo, va=va: (ZM.teach(art, mo, va), log(f'music: taught {art} -> {mo} {va}'), self.decide()))
            sub.append(i)
        sub.append(Gtk.SeparatorMenuItem())
        f = Gtk.MenuItem(label='Forget (back to the sound)')
        f.connect('activate', lambda *_: (ZM.forget(art), self.decide())); sub.append(f)
        if hasattr(ZM, 'ARTIST_ALL') and hasattr(ZM, 'RITUALS'):                                   # d15: every song by them
            sub.append(Gtk.SeparatorMenuItem())
            meta = dict(artists=[art], title=ZM.ARTIST_ALL)
            cur = (ZM.load_songs().get(ZM.norm(art) + '|*') or {}).get('peak', '')
            pm = Gtk.Menu(); top = Gtk.MenuItem(label=f'Peak for every {art[:20]} song'); top.set_submenu(pm); sub.append(top)
            for lab, v in self.peak_opts():
                i = Gtk.MenuItem(label=('● ' if cur == v else '   ') + lab)
                i.connect('activate', lambda _w, v=v: (ZM.teach_song(meta, peak=v), log(f'music: {art} peak {v or "auto"} (every song)'), self.decide())); pm.append(i)

    def peak_opts(self):
        opts = [('ПОДМЕНЫШ · lightning, then the changeling (hard songs)', 'possess'), ('ПОСЛЕДНИЙ РУБЕЖ · last stand (epic songs)', 'stand'),
                ('ТРИ ГВОЗДЯ · nails, then the hand', 'nails'), ('Blackwall rift', 'rift'), ('Auto (from the sound and tags)', '')]
        if self.cfg.get('nails', '0') != '1': opts = [o for o in opts if o[1] != 'nails']                       # d12: archived
        return opts

    def song_menu(self, sub):
        """d5: per-song teaching. Feels = the weather layer, Mode = the body."""
        meta = dict(artists=self.music.artists(), title=self.music.title())
        cur = (self.srule or {})
        for lab, w in (('Feels: rain (sad)', 'rain'), ('Feels: clear (hype)', 'clear'), ('Feels: storm (aggressive)', 'storm'),
                       ('Feels: dawn (bittersweet)', 'dawn'), ('Feels: auto', '')):
            i = Gtk.MenuItem(label=('● ' if cur.get('feel', '') == w and (w or 'feel' not in cur) else '   ') + lab)
            i.connect('activate', lambda _w, w=w: (ZM.teach_song(meta, feel=w), log(f'music: song feels {w or "auto"}'), self.decide())); sub.append(i)
        sub.append(Gtk.SeparatorMenuItem())
        ms = Gtk.Menu(); top = Gtk.MenuItem(label='Mode for this song'); top.set_submenu(ms); sub.append(top)
        for lab, mv in self.MODE_OPTS + [('Auto (artist rule / sound)', '')]:
            i = Gtk.MenuItem(label=lab)
            i.connect('activate', lambda _w, mv=mv: (ZM.teach_song(meta, mode=mv), log(f'music: song mode {mv or "auto"}'), self.decide())); ms.append(i)
        if hasattr(ZM, 'RITUALS'):                                                   # d9
            pm = Gtk.Menu(); top = Gtk.MenuItem(label='Peak · the big moment'); top.set_submenu(pm); sub.append(top)
            for lab, v in self.peak_opts():                                                              # d15
                i = Gtk.MenuItem(label=('● ' if cur.get('peak', '') == v else '   ') + lab)
                i.connect('activate', lambda _w, v=v: (ZM.teach_song(meta, peak=v), log(f'music: song peak {v or "auto"}'), self.decide())); pm.append(i)
            rm = Gtk.Menu(); top = Gtk.MenuItem(label='Ritual'); top.set_submenu(rm); sub.append(top)
            for lab, v in (('ПРИЗЫВ · summoning', 'summon'), ('КУЛЬТ · cult', 'cult'), ('ЯЗЫЧЕСТВО · pagan', 'pagan'), ('None (digital only)', 'none'), ('Auto', '')):
                i = Gtk.MenuItem(label=('● ' if cur.get('ritual', '') == v else '   ') + lab)
                i.connect('activate', lambda _w, v=v: (ZM.teach_song(meta, ritual=v), log(f'music: song ritual {v or "auto"}'), self.decide())); rm.append(i)

    def ctl_tick(self, now):
        """d5: actions from the global shortcuts (zarya-music ctl …) and the stop-in timer."""
        try: mt = os.path.getmtime(ZM.CTL_EVENT)
        except OSError: mt = 0
        if mt > self.ctl_seen:
            first = self.ctl_seen == 0; self.ctl_seen = mt
            if not first and now - mt < 5:
                try:
                    import json; ev = json.loads(rd(ZM.CTL_EVENT))
                except ValueError: ev = {}
                w = ev.get('what')
                if w == 'vol' and ev.get('level') is not None:
                    self.vol_show = (ev['level'], now)
                    if self.journal: self.journal.mark('vol')
                elif w == 'like':
                    if ev.get('ok'):
                        self.love_until = now + 1.8
                        if self.journal: self.journal.mark('like')
                    self.post('ok' if ev.get('ok') else 'warn', '♥' if ev.get('ok') else 'ЛАЙК', ev.get('msg', ''), '', 4)
                elif w in ('next', 'prev', 'play'): self.fx = ('poke', now)
                elif w == 'stop-in': self.post('info', 'СОН', f'MUSIC STOPS IN {ev.get("mins", 0):g} MIN', 'RIGHT-CLICK > STOP MUSIC IN… > CANCEL', 5)
        try: at = float(rd(ZM.STOP_AT) or 0)
        except ValueError: at = 0
        if at and now >= at - 10 and self.stop_fade is None and self.music.playing():
            short = self.music.short_active(); sis = ZM.player_stream(short)
            vol0 = ZM.stream_volume(sis[0]) if sis else None
            self.stop_fade = (short, vol0, at); log(f'stop-in: fading {short} from {vol0}%')
        if self.stop_fade:
            short, vol0, at2 = self.stop_fade
            if vol0 is not None and now < at2:
                k = max(0.0, (at2 - now) / 10); threading.Thread(target=ZM.volume_set, args=(short, round(vol0 * k)), daemon=True).start()
            elif now >= at2:
                self.music.cmd('Pause'); self.yawn_until = now + 3
                if vol0 is not None: GLib.timeout_add(1200, lambda: (threading.Thread(target=ZM.volume_set, args=(short, vol0), daemon=True).start(), False)[1])
                try: os.remove(ZM.STOP_AT)
                except OSError: pass
                self.stop_fade = None; log('stop-in: paused, volume restored')
        elif at and now > at + 30:
            try: os.remove(ZM.STOP_AT)
            except OSError: pass

    def ghost_tick(self, now):
        """d5: over another app, ДЕМОН fades to 25 % and lets clicks through when the mouse comes near.
        Hold the mouse still on him for 1 s and he comes back."""
        want = False
        if self.screen_fx is None and self.ghost_allowed() and self.cover_pet and self.mouse and not self.pinned and not self.report \
                and not getattr(self, 'gaming', False):                         # d31: no fade in games
            ox, oy = self.get_position(); cx, cy = ox + self.SW / 2, oy + self.WH - self.SH / 2
            near = abs(self.mouse[0] - cx) < self.SW / 2 + 60 and abs(self.mouse[1] - cy) < self.SH / 2 + 60
            on = abs(self.mouse[0] - cx) < self.SW / 2 and abs(self.mouse[1] - cy) < self.SH / 2
            if on and now - self.last_move > 1.0: self.still_at = now
            if self.still_at and not on: self.still_at = None
            want = near and not self.still_at
        if want != self.ghost_on:
            self.ghost_on = want; self.reshape()
            if want: self.hover = False
        self.ghost += ((0.75 if want else 0.0) - self.ghost) * 0.35

    # --- animation ---
    def tick(self):
        now = time.time()
        gaming = getattr(self, 'gaming', False)                                  # d31 ИГРА: he keeps going during games
        if self.hidden_fs and not gaming: return True
        seat = Gdk.Display.get_default().get_default_seat()
        _, mx, my, mask = Gdk.get_default_root_window().get_device_position(seat.get_pointer())   # d6: + buttons (global)
        self.hold_tick(now, 0 if gaming else mask)                                # d31: no hold-to-exorcise in a game
        if self.mouse != (mx, my): self.mouse = (mx, my); self.last_move = now
        if self.ear: self.music_tick(now); self.speech_tick(now)
        if ZM: self.event_tick(now)
        if self.stand is not None:                                                    # d14
            self.stand.tick(now, self.ear.ear.snap if self.ear and self.ear_on else {})
            if self.stand.phase != self.stand_phase:
                self.stand_phase = self.stand.phase
                if self.stand.phase == 'climax' and self.journal: self.journal.mark('peak', 'peak: ПОСЛЕДНИЙ РУБЕЖ: still breathing')
            if self.stand.preview and self.stand.phase == 'after' and now - (self.stand.climax_t or now) > 12: self.stand = None; log('hurt: stand preview over')
        if self.form_on() and self.music.playing(): self.react.prog = self.music.progress() or 0                  # d19: for ГОЛОД
        if self.form_on() and self.music.playing() and hasattr(self.form, 'set_hard') and now - getattr(self, 'hard_t', 0) > 1.0:   # d23
            self.hard_t = now
            try:
                mo, va, _ = self.cur_mode(); wt = self.cur_weather()[0]; pk = (self.srule or {}).get('peak')
                calm_ = ZM.CALM if ZM else ()
                soft_ = self.epic_song() or mo in calm_ or (wt in ('rain', 'dawn') and mo in ('groove', 'nod', 'epic', 'kawaii'))   # d24
                hard_ = (ZH.is_hard(mo, va, wt, pk, calm_) and not self.epic_song()) or bool(self.brain and self.brain.hard())
                try: self.form.set_hard(hard_, soft=soft_ and not hard_)
                except TypeError: self.form.set_hard(hard_)
            except Exception as e:
                if str(e) != getattr(self, 'hard_err', None): self.hard_err = str(e); log(f'hurt: hard check error: {e!r}')
        if self.form is not None and self.hurt and not self.form_on() and self.cfg.get('form', '1') != '0' and self.mkey \
                and self.music.playing() and getattr(self, 'summoned', None) != self.mkey and self.dg_song() and self.screen_fx is None:
            pos_ = self.music.position() or 0
            lv = ((self.ear.ear.snap or {}).get('level', 0) if self.ear and self.ear_on else 0) or 0
            if pos_ >= 4 and (lv >= 0.5 or pos_ >= 12):                                                  # d23: ДЕЛИКАТЕС
                self.summoned = self.mkey; log(f'hurt: ДЕЛИКАТЕС: it smells {self.music.title()[:40]} and comes for it')
                if self.journal: self.journal.mark('hurt', 'ДЕЛИКАТЕС: it came for the song')
                if self.cfg.get('screen', '1') != '0' and not (self.hidden_fs or self.steam_game):
                    self.screen_event('descend', f'ДЕЛИКАТЕС · {self.music.title()[:30]}')
                else:
                    try: mins = float(self.cfg.get('form_min', '45') or 45)
                    except ValueError: mins = 45
                    self.form.start(now, mins, 'ДЕЛИКАТЕС (no screen: fullscreen / game)',
                                    song=ZJ.key_of(self.music.artist(), self.music.title()) if ZJ else self.music.title())
        blk_ = DIRECTOR.react_outer(self)                                                           # d28: was inline (d16)
        if blk_: DIRECTOR.react_outer_note(self, blk_)
        else:
            try:
                self.react.song(self.mkey)
                r_ = self.react.tick(now, self.ear.ear.snap, self.epic_song(), bool(getattr(self.dance, 'soft', False)), self.music.progress())
                if r_ == 'ascend' and self.cfg.get('screen', '1') != '0': self.screen_event('ascend', 'godlike moment')     # d18
            except Exception as e:
                if str(e) != getattr(self, 'react_err', None): self.react_err = str(e); log(f'react: tick error: {e!r}')
        if self.brain and now - self.brain_t > 1.0:                                       # d20: pause / seek spoil a recording
            self.brain_t = now
            try:
                self.brain.check(now, self.music.position(), self.music.playing() and not getattr(self, 'gaming', False))   # d31: no study in games
                if int(now) % 5 == 0: self.brain.refresh()
            except Exception as e: log(f'brain: check error: {e!r}')
        if ZM: self.ctl_tick(now)
        if ZM and self.journal:                                                    # d10: his peaks go into the journal
            q = getattr(ZM, 'PEAK_Q', None)
            while q: self.journal.mark('peak', q.pop(0))
            self.ask_tick(now)
        self.ghost_tick(now)
        self.blink = max(0.0, self.blink - 0.1); self.next_blink -= 0.1
        if self.next_blink <= 0: self.blink = 0.15; self.next_blink = 2.5 + random.random() * 5
        self.glitch = self.glitch * 0.8 if self.glitch > 0.03 else 0.0
        if random.random() < 0.002: self.glitch = 0.6
        if self.report and now > self.report_until: self.report = None
        if not self.report and self.reports and not self.muted():
            self.report = self.reports.pop(0); self.report_until = now + self.report[4]
            self.fx = ('alert' if self.report[0] == 'crit' else 'poke', now); self.glitch = 0.5
        elif self.muted(): self.reports.clear()
        self.queue_draw()
        return True

    def state(self):
        now = time.time(); t = now - self.t0
        st = dict(t=t, glitch=self.glitch, blink=self.blink > 0, hot=self.hot_on)
        if self.fx and now - self.fx[1] < 0.9:
            st.update(mode=self.fx[0], t=now - self.fx[1], level='crit' if self.fx[0] == 'alert' else 'info')
        elif self.ringing: st['mode'] = 'ring'
        elif self.job or (self.cpu_busy_since and now - self.cpu_busy_since >= 4): st['mode'] = 'work'
        elif self.timer:
            end, start, lab = self.timer
            st.update(mode='timer', progress=(end - now) / max(1, end - start))
        elif now < self.yawn_until or (now - self.last_move > 600 and not self.music.playing() and not self.report): st['mode'] = 'sleep'
        else:
            st['mode'] = 'idle'
            if self.mouse:
                ox, oy = self.get_position()
                ex = ox + (ZD.OX + 7) * self.U; ey = oy + self.WH - self.SH + (ZD.OY + 4.5) * self.U
                dx, dy = (self.mouse[0] - ex) / 2.0, (self.mouse[1] - ey)
                L = (dx * dx + dy * dy) ** 0.5 or 1; k = min(1, L / 150)
                st['pupil'] = (dx / L * k, dy / L * k)
        if st['mode'] == 'idle' and now < self.look_up_until:
            st['pupil'] = (0.9, -0.9)                                             # top-right
        if self.music.playing() and st['mode'] == 'idle' and self.dancing():
            st['eye'] = ZD.C['G']; st['glitch'] = min(st['glitch'], 0.2)        # d4: the music mode moves the eye
        elif self.music.playing() and st['mode'] == 'idle' and not st.get('blink'):
            st['eye'] = '#9D7BFF' if int(t / 0.5) % 2 else ZD.C['G']     # eye pulses with the music
        return st

