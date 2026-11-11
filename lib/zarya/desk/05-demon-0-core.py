

# ---------------- the pet ----------------
class Demon(_Demon1, _Demon2, _Demon3, _Demon4, Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.cfg = conf()
        self.U = max(3, min(10, int(self.cfg.get('unit', '5'))))
        self.SW, self.SH = ZD.W * self.U, ZD.H * self.U
        self.WW, self.WH = self.SW + int(420 * self.U / 4) + 12, max(self.SH, 280)       # tall bubbles grow upward
        self.set_title('ДЕМОН')
        self.set_decorated(False); self.set_keep_above(True); self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True); self.set_accept_focus(False); self.stick()
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)       # d6: Muffin keeps DESKTOP / DOCK windows on Show Desktop (Super+D)
        self.set_app_paintable(True)
        scr = self.get_screen(); vis = scr.get_rgba_visual()
        if vis and scr.is_composited(): self.set_visual(vis)
        self.set_default_size(self.WW, self.WH)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.SCROLL_MASK |
                        Gdk.EventMask.ENTER_NOTIFY_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK | Gdk.EventMask.POINTER_MOTION_MASK)
        self.connect('draw', self.draw); self.connect('button-press-event', self.click)
        self.connect('scroll-event', self.scroll); self.connect('motion-notify-event', self.motion)
        self.connect('leave-notify-event', lambda *a: self._hover(False))
        self.connect('realize', lambda *a: self.place())
        self.t0 = time.time(); self.fx = None; self.glitch = 0.8; self.blink = 0.0; self.next_blink = 2.0
        self.hover = False; self.pinned = False; self.reports = []; self.report = None; self.report_until = 0
        self.last_move = time.time(); self.mouse = None; self.hidden_fs = False; self.hot_on = False
        self.job = None; self.bubble_rect = None
        self.timer = None; self.ringing = None; self.next_ring = 0; self.ring_until = 0
        self.game = None; self.look_up_until = 0
        self.active_since = None; self.cpu_busy_since = None; self.up_next = None
        self.steam_dl = {}; self.steam_tick = 0
        # d4: music modes
        self.ear = None; self.dance = None; self.mkey = None; self.mrule = None; self.force = None
        self.fx_id = None; self.ear_on = False; self.music_off_at = 0; self.fx_err = None
        # d5
        self.info = None; self.info_key = None; self.wx = ('', ''); self.srule = None; self.announce = None
        self.cover_pet = False; self.cover_cap = False; self.steam_game = None; self.ghost = 0.0; self.ghost_on = False
        self.still_at = None; self.ctl_seen = 0; self.vol_show = None; self.love_until = 0; self.stop_fade = None; self.yawn_until = 0
        self.last_click = 0; self.pos_ctx = None
        # d6
        self.btn1 = False; self.btn1_at = 0; self.hold_wrote = 0; self.sel_at = 0
        # d7
        self.talk = None; self.beat_since = None; self.talk_key = None; self.rep_dlg = None
        # d9
        self.force_poss = None; self.poss_seen = None
        # d8
        self.hooks = []; self.ev_done = None; self.screen_fx = None
        # d10
        if ZH: ZH.set_logger(log)
        self.hurt = ZH.Hurt() if ZH and self.cfg.get('hurt', '1') != '0' else None
        self.journal = ZJ.Journal(log) if ZJ and self.cfg.get('journal', '1') != '0' else None
        if ZB: ZB.set_logger(log)
        self.brain = ZB.Brain() if ZB and self.cfg.get('brain', '1') != '0' else None; self.bctx = None; self.brain_t = 0   # d20
        self.app = None; self.cover_prev = False; self.hunted = None; self.route = (False, None); self.asked_key = None
        self.auth_pos = None; self.auth_warned = False
        # d11
        self.form = ZH.Form(self.hurt.mem) if self.hurt and hasattr(ZH, 'Form') else None
        self.frame = None; self.shadow_gap = 0.0
        self.stand = None; self.stand_key = None; self.stand_phase = None                                   # d14
        self.react = Reactions()                                                                             # d16
        BUS.attach(self)                                                                                     # d28: event bus
        if self.form and self.form.active(time.time()): log(f'hurt: {ZH.FORM_NAME} is still in him')
        try: self.ev_seen = os.path.getmtime(ZM.SCREEN_FILE) if ZM and hasattr(ZM, 'SCREEN_FILE') else 0.0
        except OSError: self.ev_seen = 0.0
        try: self.hints = int(rd(HINTS) or 0)
        except ValueError: self.hints = 0
        try:
            Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY).connect('owner-change', self._sel_owner)
        except Exception as e: log(f'select-hold: no owner-change ({e})')
        if ZM and self.cfg.get('fx', '1') != '0':
            self.ear = ZM.Listener(); self.ear.start(); self.dance = ZM.Dance()
        self.stats = Stats(); self.music = Music(self.on_track)
        os.makedirs(EVENTS, exist_ok=True); os.makedirs(TIMERS, exist_ok=True)
        self.watch_downloads()
        GLib.timeout_add(100, self.tick)
        GLib.timeout_add(2000, self.slow)
        GLib.timeout_add(1000, self.scan)
        log(f'start {VERSION}: unit {self.U}, music {self.cfg.get("music")}, fx {"on" if self.ear else "off" if ZM else "missing zarya-music"}'
            + f', hurt {"on" if self.hurt else "off"}, journal {"on" if self.journal else "off"}'
            + (' (but Music animations is OFF: fx-off file)' if os.path.exists(FXOFF) else '') + (', fade over apps off' if os.path.exists(GHOSTOFF) else ''))

    # --- placement / visibility ---
    def place(self):
        d = Gdk.Display.get_default(); mon = d.get_primary_monitor() or d.get_monitor(0)
        wa = mon.get_workarea()
        x = wa.x + int(self.cfg.get('x', 20)) - ZD.OX * self.U // 2
        y = wa.y + wa.height - self.WH - int(self.cfg.get('y', 20))
        self.move(x, y); self.wa = wa
        log(f'place {x},{y} on {wa.width}x{wa.height}')
        self.reshape()

    def reshape(self):
        if self.ghost_on or getattr(self, 'gaming', False): rects = []              # d5: ghost = click-through · d31: games too
        else:
            rects = [cairo.RectangleInt(0, self.WH - self.SH, self.SW, self.SH)]
            if self.bubble_rect: rects.append(cairo.RectangleInt(*[int(v) for v in self.bubble_rect]))
        if self.get_window(): self.input_shape_combine_region(cairo.Region(rects) if rects else cairo.Region())

    def fullscreen_active(self):
        try:
            a = subprocess.run(['xprop', '-root', '_NET_ACTIVE_WINDOW'], capture_output=True, text=True, timeout=1).stdout
            m = re.search(r'(0x[0-9a-f]+)', a)
            if not m or m.group(1) == '0x0': return False, ''
            p = subprocess.run(['xprop', '-id', m.group(1), '_NET_WM_STATE', 'WM_CLASS'], capture_output=True, text=True, timeout=1).stdout
            return '_NET_WM_STATE_FULLSCREEN' in p, p
        except Exception:
            return False, ''

    def scan_windows(self):
        """d5, every 2 s: Steam game windows anywhere (ДЕМОН hides while one exists, even borderless windowed),
        and whether a visible window covers his corner (ghost on approach) or the caption (caption folds away)."""
        try:
            out = subprocess.run(['wmctrl', '-lGx'], capture_output=True, text=True, timeout=1).stdout
            dsk = subprocess.run(['wmctrl', '-d'], capture_output=True, text=True, timeout=1).stdout
        except Exception:
            if not getattr(self, '_wm_warned', False): self._wm_warned = True; log('windows: wmctrl missing, caption shows everywhere, no ghost / Steam hide')
            self.steam_game = None; self.cover_pet = self.cover_cap = False; return
        m = re.search(r'^(\d+)\s+\*', dsk, re.M); cur = int(m.group(1)) if m else 0
        ox, oy = self.get_position()
        pet = (ox, oy + self.WH - self.SH, self.SW, self.SH)
        cap = (ox + self.SW, oy + self.WH - 84, 380, 84)
        hit = lambda a, b: a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]
        steam = None; cp = cc = False
        for line in out.splitlines():
            p = line.split(None, 7)
            if len(p) < 7: continue
            try: wid, desk, x, y, w, h = p[0], int(p[1]), int(p[2]), int(p[3]), int(p[4]), int(p[5])
            except ValueError: continue
            cls = p[6].lower()
            if cls.startswith('steam_app_'): steam = steam or cls.split('.')[0]
            if desk not in (cur, -1) or 'zarya-daemon-desk' in cls or 'nemo-desktop' in cls or cls.startswith(('desktop_window', 'cinnamon')): continue
            r = (x, y, w, h); a, b = hit(r, pet), hit(r, cap)
            if not (a or b) or (cp and cc): continue
            try: st = subprocess.run(['xprop', '-id', wid, '_NET_WM_STATE'], capture_output=True, text=True, timeout=1).stdout
            except Exception: st = ''
            if '_NET_WM_STATE_HIDDEN' in st: continue                           # minimised
            cp, cc = cp or a, cc or b
        if steam != self.steam_game: log(f'windows: Steam game {"running: " + steam if steam else "gone"}')
        self.steam_game = steam; self.cover_pet = cp; self.cover_cap = cc

    def muted(self):
        try: return float(rd(MUTE) or 0) > time.time()
        except ValueError: return False

    # --- events in ---
    def on_track(self, title, artist):
        self.up_next = None
        log(f'music: now playing {artist} - {title}')
        if self.cfg.get('music', '1') == '0' or self.muted(): return
        self.announce = time.time()                         # d5: big caption for 3 s, then it settles (no report bubble)
        if os.path.exists(SPOT_TOKEN):
            def fetch():
                time.sleep(1.5)                          # let Spotify update its queue first
                nx = spotify_next()
                if nx: GLib.idle_add(self._got_next, nx)
            threading.Thread(target=fetch, daemon=True).start()

    def _got_next(self, nx):
        self.up_next = nx                                   # shown in the caption and the hover bubble
        log(f'music: up next {nx[1]} - {nx[0]}')
        return False

    def post(self, level, title, body, hint='', secs=6):
        self.reports.append([level, title, body, hint, secs])
        log(f'report {level}: {title} | {body.splitlines()[0] if body else ""}')

    # --- downloads (Firefox *.part, Chrome *.crdownload renamed to the final name) ---
    def watch_downloads(self):
        if self.cfg.get('downloads', '1') == '0': return
        d = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOWNLOAD) or f'{HOME}/Downloads'
        try:
            self._dlmon = Gio.File.new_for_path(d).monitor_directory(Gio.FileMonitorFlags.WATCH_MOVES, None)
            self._dlmon.connect('changed', self._dl_event)
            log(f'downloads: watching {d}')
        except GLib.Error as e:
            log(f'downloads: cannot watch {d}: {e.message}')

    def _dl_event(self, mon, f, other, ev):
        if ev != Gio.FileMonitorEvent.RENAMED or not other: return
        old, new = f.get_basename(), other.get_basename()
        if not old.endswith(('.part', '.crdownload')) or new.endswith(('.part', '.crdownload', '.tmp')): return
        try: size = os.path.getsize(other.get_path())
        except OSError: size = 0
        sz = f'{size / 1073741824:.1f} GB' if size >= 1073741824 else f'{size / 1048576:.1f} MB' if size >= 1048576 else f'{size // 1024} KB'
        self.post('ok', 'ЗАГРУЗКА ГОТОВА', new if len(new) <= 34 else new[:33] + '…', f'DOWNLOAD DONE · {sz}', 7)

    # --- Steam installs / updates ---
    def steam_libraries(self):
        libs = []
        for vdf in (f'{HOME}/.steam/steam/steamapps/libraryfolders.vdf', f'{HOME}/.local/share/Steam/steamapps/libraryfolders.vdf'):
            for p in re.findall(r'"path"\s+"([^"]+)"', rd(vdf)):
                p = os.path.realpath(p)
                if p not in libs: libs.append(p)
        return libs

    def scan_steam(self):
        now = {}
        for lib in self.steam_libraries():
            for d in glob.glob(f'{lib}/steamapps/downloading/*/'):
                appid = os.path.basename(d.rstrip('/'))
                if appid.isdigit(): now[appid] = lib
        for appid, lib in self.steam_dl.items():
            if appid not in now:
                acf = rd(f'{lib}/steamapps/appmanifest_{appid}.acf')
                name = (re.search(r'"name"\s+"([^"]+)"', acf) or [None, f'app {appid}'])[1]
                flags = (re.search(r'"StateFlags"\s+"(\d+)"', acf) or [None, '0'])[1]
                if flags == '4': self.post('ok', 'STEAM · ГОТОВО', name, 'INSTALLED / UPDATED · READY TO PLAY', 8)
        self.steam_dl = now

    def steam_name(self, appid):
        for lib in self.steam_libraries():
            m = re.search(r'"name"\s+"([^"]+)"', rd(f'{lib}/steamapps/appmanifest_{appid}.acf'))
            if m: return m.group(1)
        return None

    def scan(self):
        # running terminal jobs (written by the ZARYA terminal bashrc hooks)
        now = time.time(); job = None
        for f in glob.glob(JOBS + '/*'):
            pid = os.path.basename(f)
            if not pid.isdigit() or not os.path.exists('/proc/' + pid): continue
            st, _, cmd = rd(f).partition('\n')
            try:
                if now - float(st) >= 3 and cmd_word(cmd) not in EXCLUDE: job = (cmd.strip(), now - float(st)); break
            except ValueError: pass
        self.job = job
        # kitchen timers (zt): ~/.cache/zarya-daemon/timers/<end>-<rand>, content "start<TAB>label"
        timer = None
        for f in sorted(glob.glob(TIMERS + '/*-*')):
            m = re.match(r'(\d+)-', os.path.basename(f))
            if not m: continue
            end = int(m.group(1)); st, _, lab = rd(f).partition('\t')
            try: start = float(st)
            except ValueError: start = now
            lab = (lab.strip() or 'ТАЙМЕР').upper()
            if end <= now:
                if self.ringing != f:
                    if now - end > 300:                 # missed by more than 5 min (asleep / logged out)
                        try: os.remove(f)
                        except OSError: pass
                        self.post('warn', f'ВРЕМЯ ВЫШЛО · {lab}', f'TIME RAN OUT {int((now - end) // 60)} MIN AGO', 'CLICK TO DISMISS', 12)
                        continue
                    self.ringing = f; self.ring_until = now + 300; self.next_ring = 0
                    self.post('crit', f'ВРЕМЯ ВЫШЛО · {lab}', 'TIME IS UP', 'CLICK ME TO STOP', 300)
                    log(f'timer: ringing {lab}')
                continue
            if not timer: timer = (end, start, lab)
        self.timer = timer
        if self.ringing:
            if not os.path.exists(self.ringing) or now > self.ring_until:
                self.stop_ring()
            elif now >= self.next_ring:
                self.next_ring = now + 4
                snd = next((x for x in RING_SOUNDS if os.path.exists(x)), None)
                if snd: subprocess.Popen(['paplay', snd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        # finished jobs and posted reports
        for f in sorted(glob.glob(EVENTS + '/*')):
            if os.path.basename(f).startswith('.') or not f.endswith(('.tsv', '.json')): continue   # skip files still being written
            txt = rd(f)
            try: os.remove(f)
            except OSError: pass
            if f.endswith('.tsv'):
                p = txt.rstrip('\n').split('\t', 2)
                if len(p) < 3: continue
                dur, rc, cmd = p
                _, info = self.fullscreen_active()
                if 'gnome-terminal' in info.lower() or cmd_word(cmd) in EXCLUDE or rc == '130':
                    continue                     # the terminal already reacted inline
                short = cmd if len(cmd) <= 30 else cmd[:29] + '…'
                if rc == '0': self.post('ok', 'ГОТОВО', short, f'FINISHED IN {fmt_dur(float(dur))}')
                else: self.post('crit', f'СБОЙ ✕{rc}', short, f'FAILED AFTER {fmt_dur(float(dur))}', 9)
            elif f.endswith('.json'):
                try:
                    import json; j = json.loads(txt)
                    self.post(j.get('level', 'info'), j.get('title', ''), j.get('body', ''), j.get('hint', ''), 8)
                except Exception as e: log(f'event {f}: {e}')
        return True

    def stop_ring(self):
        if self.ringing:
            try: os.remove(self.ringing)
            except OSError: pass
            log('timer: stopped')
        self.ringing = None
        if self.report and self.report[1].startswith('ВРЕМЯ ВЫШЛО'): self.report_until = 0

    def slow(self):
        now = time.time()
        self.stats.sample()
        fs, info = self.fullscreen_active()
        self.scan_windows()
        if (fs or self.steam_game) and not self.hidden_fs:
            self.hidden_fs = True                                                   # d31: hide only for video (was: always)
            m = re.search(r'WM_CLASS\(STRING\) = "([^"]*)", "([^"]*)"', info)
            cls = (m.group(1) if m and fs else self.steam_game or '').lower()
            name = None
            sa = re.match(r'steam_app_(\d+)', cls)
            if sa: name = self.steam_name(sa.group(1))
            self.game = dict(start=now, cls=cls, name=name or (m.group(2) if m else 'fullscreen app'), cpu=0, gpu=0,
                             video=any(v in f'{cls} {(m.group(2) if m and fs else "")}'.lower() for v in VIDEO_CLASSES))   # d31: both WM_CLASS fields (Firefox = Navigator, firefox)
            if self.game['video'] or self.cfg.get('game_show', '1') == '0':
                self.hide(); log(f'hide: {"fullscreen window focused" if fs else "Steam game running"} ({cls})')
            else:                                                                   # d31 ИГРА: he stays, takes no input
                self.gaming = True; self.ghost_on = False; self.hover = False; self.reshape()
                if hasattr(self, 'game_layer'): self.game_layer(True)                # d33: drawn on top of the game
                log(f'game: he stays, hands off ({self.game["name"]} · {cls})')
        elif not fs and not self.steam_game and self.hidden_fs:
            self.hidden_fs = False
            if getattr(self, 'gaming', False):
                self.gaming = False; self.reshape(); log('game: over, he takes input again')
                if hasattr(self, 'game_layer'): self.game_layer(False)              # d33
            else: self.show_all(); self.place(); log('show: fullscreen / game gone')
            g = self.game; self.game = None
            if g and not g['video'] and now - g['start'] >= float(self.cfg.get('game_min', '5')) * 60 and self.cfg.get('games', '1') != '0':
                peak = ' · '.join(x for x in (f'GPU PEAK {g["gpu"]}°' if g['gpu'] else '', f'CPU PEAK {g["cpu"]}°' if g['cpu'] else '') if x)
                self.post('info', 'СЕАНС ОКОНЧЕН', f'{g["name"]}\nPLAYED {fmt_dur(now - g["start"])}', peak, 9)
            self.active_since = None
        m_ = re.search(r'WM_CLASS\(STRING\) = "([^"]*)", "([^"]*)"', info or '')        # d10: the app in front (journal)
        self.app = m_.group(2) if m_ else self.app
        if self.hurt and self.cover_pet and not self.cover_prev and not self.hidden_fs: self.hurt.covered(now)
        self.cover_prev = self.cover_pet
        if self.hurt and self.cfg.get('sudo_nails', '1') != '0': self.auth_scan(now)
        if self.journal and self.music.active():
            try:
                mode = self.cur_mode()[0] if self.dancing() or self.mrule else None
                if self.form_on(): mode = 'changeling'
                w, why = self.cur_weather(); why = (self.cur_mode()[2] if self.mrule or self.dancing() else None)
                self.journal.tick(now, self.music.playing(), self.music.position(), mode, w, why, self.app,
                                  self.ear.ear.snap if self.ear and self.ear_on else None, self.talk)
            except Exception as e: log(f'journal: {e!r}')
        if self.game:
            self.game['cpu'] = max(self.game['cpu'], self.stats.cpu_t or 0); self.game['gpu'] = max(self.game['gpu'], self.stats.gpu_t or 0)
        # Steam installs, every 30 s
        if self.cfg.get('steam', '1') != '0' and now >= self.steam_tick:
            self.steam_tick = now + 30; self.scan_steam()
        # break reminder: continuous activity at the desk
        brk = float(self.cfg.get('break', '60') or 0)
        if brk > 0 and not self.hidden_fs:
            if now - self.last_move > 300: self.active_since = None
            elif self.active_since is None: self.active_since = now
            elif now - self.active_since >= brk * 60:
                self.post('warn', 'ПЕРЕРЫВ', f'{fmt_dur(now - self.active_since).upper()} AT THE DESK\nSTAND UP · DRINK WATER', 'CLICK TO DISMISS', 15)
                self.active_since = now
        # share stats + now playing with the terminal docks (zarya-dock reads stats.json, fresh for 10 s)
        try:
            import json
            st = self.stats
            j = dict(ts=now, cpu=st.cpu, cpu_t=st.cpu_t, gpu=st.gpu, gpu_t=st.gpu_t, ram=st.ram, ram_tot=st.ram_tot,
                     music=dict(playing=self.music.playing(), title=self.music.title(), artist=self.music.artist(),
                                mode=self.mode_label() if self.dancing() else ''),
                     changeling=dict(on=True, move=getattr(self.form, 'move', ''), hunger=self.form.hunger() if hasattr(self.form, 'hunger') else 0.5,
                                     name=ZH.FORM_NAME) if self.form_on() else None)
            with open(f'{CACHE}/stats.json.tmp', 'w') as f: json.dump(j, f)
            os.replace(f'{CACHE}/stats.json.tmp', f'{CACHE}/stats.json')
        except Exception as e:
            log(f'stats.json: {e}')
        self.write_music_state(now)
        # RunCat: heavy CPU makes the visor scan
        if (self.stats.cpu or 0) >= 75: self.cpu_busy_since = self.cpu_busy_since or now
        else: self.cpu_busy_since = None
        hot = self.stats.hot()
        if hot and not self.hot_on:
            self.hot_on = True; self.post('crit', 'ПЕРЕГРЕВ', '\n'.join(self.stats.lines()[:2]), 'RUNNING HOT', 8); log('hot: on')
        elif self.hot_on and (self.stats.cpu_t or 0) < 80 and (self.stats.gpu_t or 0) < 78:
            self.hot_on = False; log('hot: off')
        return True

    # --- input ---
    def _hover(self, on):
        if on and not self.hover and self.hints < 6:                               # d6: hint on hovers 1-5, then never
            self.hints += 1
            try:
                with open(HINTS, 'w') as f: f.write(str(self.hints))
            except OSError: pass
        if self.hover != on: self.hover = on

    # --- d6: tell the terminal docks to hold still while text is being selected ---
    def _hold(self, until, since):
        try:
            with open(HOLD + '.tmp', 'w') as f: f.write(f'{until:.2f} {since:.2f}\n')
            os.replace(HOLD + '.tmp', HOLD)
        except OSError as e: log(f'select-hold: {e}')

    def hold_tick(self, now, mask):
        down = bool(mask & Gdk.ModifierType.BUTTON1_MASK)
        if down and self.btn1 and self.form_on() and now - self.btn1_at > 2.0 and self.mouse and not getattr(self, 'held_out', False):
            ox, oy = self.get_position(); mx, my = self.mouse                         # d19: hold him down 2 s = it is forced out
            if ox <= mx <= ox + self.SW and oy + self.WH - self.SH <= my <= oy + self.WH:
                self.held_out = True; self.exorcise('you held it down', force=True)
        if not down: self.held_out = False
        if down and not self.btn1: self.btn1 = True; self.btn1_at = now; self._hold(now + 30, now); self.hold_wrote = now
        elif down and now - self.hold_wrote > 10: self._hold(now + 30, self.btn1_at); self.hold_wrote = now
        elif not down and self.btn1:
            self.btn1 = False                                                        # a drag that selected text in a terminal keeps the hold
            self._hold(now + (SEL_HOLD if self.sel_at >= self.btn1_at else 1.0), self.btn1_at)
