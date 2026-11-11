

class Form(_Form1, _Form2):
    """The possessed one as a lasting form with its own moves (rogue machine / thing from the other side).
    h6: ГОЛОД (hard songs feed it, calm songs starve it), МИМИКРИЯ (it plays at being ДЕМОН, a beat late), СОПРОТИВЛЕНИЕ
    (the first Изгнать fails, two at night), СЛЕДЫ (red dead pixels for the rest of the day, he flinches at the song it took
    him on), lyric lines rewritten in the caption, stronger at night."""
    def __init__(self, mem):
        self.mem = mem; self.rng = random.Random(); self.prev = dict(kick=0, snare=0, hat=0)
        self.move = 'stare'; self.move_t = -99; self.sec = None; self.jerk = (0, -9); self.tp = (0, 0); self.ghosts = []
        self.sx = 0.0; self.sx_to = 0.0; self.gait = 0; self.split_snap = -9; self.said = -99; self.line = None; self.lunge_t = -9
        self.eyes = [(self.rng.randint(1, 12), self.rng.randint(1, 8)) for _ in range(7)]; self.next_tick = 0
        self.mimic = None; self.next_mimic = time.time() + self.rng.uniform(40, 70); self.buf = []; self.tear_t = -9
        self.song_key = None; self.rot = 0.0; self.flies = []; self.gone = []; self.fly_t = 0; self.shards = []
        self.last = None; self.ctx = None; self.lvl_prev = 0.0; self.kprev = 0.0; self.pre_for = None; self._hit = False
        self._hits = dict(kick=False, snare=False, hat=False); self._parts = ([], [], [], []); self.skip_t = -9; self.krik_w = None
        self.song(time.time(), None)

    # ---- h6: hunger
    def hunger(self): return float(self.state().get('hunger', 0.5))

    def feed(self, now, hard, soft, heard_frac):
        """a song just ended while it was in him: hard songs feed it (+10 min), calm ones starve it. Returns 'starved' or None."""
        st = self.state()
        if not st or heard_frac < 0.25: return None
        h = self.hunger(); k = 0.5 if night(now) else 1.0
        if getattr(self, 'lure', False) and not hard: h = min(1.0, h + 0.06); why = 'sugar (ПРИМАНКА)'                     # h9
        elif hard: h = min(1.0, h + 0.2); st['until'] = st['until'] + 600 if st.get('until') else 0; why = 'fed (hard song)'
        elif soft: h -= 0.25 * k; why = 'starving (calm song)'
        else: h -= 0.06 * k; why = 'hungry'
        st['hunger'] = round(max(0.0, h), 2); self.mem.save(); log(f'hurt: {FORM_NAME} {why}, hunger {st["hunger"]:.2f}')
        return 'starved' if st['hunger'] <= 0 else None

    # ---- h6: resistance
    def resist(self, now):
        """Изгнать pressed: True = it holds on this time (first try; first two at night)."""
        st = self.state(); n = st.get('tries', 0) + 1; st['tries'] = n; self.mem.save()
        if n <= (2 if night(now) else 1):
            self.tear_t = now; self.line = ('НЕТ.', now + 1.6); log(f'hurt: {FORM_NAME} held on (try {n})'); return True
        return False

    def tries(self): return self.state().get('tries', 0)

    # ---- h6: mimicry
    def mimic_on(self, now): return self.mimic is not None and now < self.mimic

    def mimic_tick(self, now, music):
        """starts / ends the act; the desk lets ДЕМОН's own dance run while it is on."""
        if getattr(self, 'arc', None) is not None:                         # h7: not while the hype builds
            if self.mimic is not None: self.mimic = None; self.jaw_t = None; self.act = None; self.next_mimic = now + self.rng.uniform(45, 80)
            return False
        if self.mimic is None and music and now > self.next_mimic:
            self.buf = []
            if hasattr(self, '_act_pick'): self._act_pick(now, music)                                          # h18: the whole repertoire
            else: self.mimic = now + self.rng.uniform(4, 7); log(f'hurt: {FORM_NAME} pretends to be him')
        elif self.mimic is not None and now >= self.mimic:
            if getattr(self, 'jaw_t', None) is None and hasattr(self, '_act_end') and self._act_end(now, music): return True   # h18: ПРОВАЛ
            if getattr(self, 'jaw_t', None) is None and self._jaw_roll(now, music): return True               # h12: ПАСТЬ
            self.mimic = None; self.jaw_t = None; self.act = None; self.next_mimic = now + self.rng.uniform(45, 80); self.line = ('…', now + 0.8)
        return self.mimic_on(now)

    def fake_title(self, title):
        """the song title with exactly one letter wrong (same letter all song)."""
        if not title: return title
        r = random.Random(title); idx = [i for i, c in enumerate(title) if c.isalpha()]
        if not idx: return title
        i = r.choice(idx); c = title[i]
        return title[:i] + LOOK.get(c.upper(), r.choice(GLYPHS)) + title[i + 1:]

    def lyric(self, lines, pos, now):
        """h6: the current synced lyric line, rewritten: words in Cyrillic look-alikes, a few glyphs."""
        if not lines or pos is None: return None
        cur = None
        for t, ln in lines:
            if t <= pos: cur = ln
            else: break
        if not cur or not cur.strip(): return None
        r = random.Random(cur + str(int(now))); out = []
        for w in cur.split():
            if r.random() < 0.45: w = ''.join(LOOK.get(c.upper(), c) for c in w)
            out.append(''.join(r.choice(GLYPHS) if c.strip() and r.random() < 0.07 else c for c in w))
        return ' '.join(out)

    def state(self): return self.mem.d.get('form') or {}
    def active(self, now): st = self.state(); return bool(st) and (st.get('until', 0) == 0 or now < st['until'])

    def start(self, now, minutes, why, song=''):
        if night(now) and minutes > 0: minutes *= 1.5                      # h6: longer at night
        self.mem.d['form'] = dict(since=now, until=(now + minutes * 60) if minutes > 0 else 0, why=why, song=song, hunger=0.5, tries=0)
        self.mem.d['forms'] = self.mem.d.get('forms', 0) + 1; self.mem.d['last_descent'] = now; self.mem.save()
        self.line = ('ЭТО БОЛЬШЕ НЕ ОН.', now + 2.2)
        log(f'hurt: {FORM_NAME} is here ({why}, {"until you drive it out" if minutes <= 0 else f"{minutes:g} min"})')

    def end(self, now, why):
        st = self.state()
        if not st: return False
        r = random.Random(now)                                              # h6: СЛЕДЫ, dead pixels for the rest of the day
        self.mem.d['residue'] = dict(day=time.strftime('%F', time.localtime(now)), cells=[[r.randint(1, 13), r.randint(1, 9)] for _ in range(8)])
        if st.get('song'): self.mem.d['songs'][st['song']] = self.mem.d['songs'].get(st['song'], 0) + 1     # he flinches at that song
        self.mem.d['form'] = None; self.mem.save(); log(f'hurt: {FORM_NAME} left him ({why})'); return True

    def label(self):
        h = self.hunger(); n = int(round(h * 5))
        a = getattr(self, 'arc', None)
        mv = ARC_RU.get(a['ph'], '') if a else dict(FORM_MOVES).get(self.move, '')       # h7
        return f'{FORM_NAME} · ' + mv + '  ГОЛОД ' + '▮' * n + '▯' * (5 - n) + ('  ДЕЛИКАТЕС' if getattr(self, 'dg', False) else '')

    def corrupt(self, text, now):
        r = random.Random(int(now * 2)); out = []
        jump = now - getattr(self, 'skip_t', -9) < 0.4                         # h7: ПРОПУСК, the letters jump
        for ch in text or '':
            out.append(r.choice(GLYPHS) if ch.strip() and r.random() < (0.6 if jump else 0.22) else ch)
        s = ''.join(out)
        if jump and len(s) > 3: k = int(now * 9) % len(s); s = s[k:] + ' ' + s[:k]
        return s

    def _frame(self, rects, sn, now, eye='#8FD9A8', mouse=None, music=False, dance=None):
        """h7: the h6 frame (the desk calls frame()). rects: his normal frame (grid units). mouse: (dx, dy) cells from his eye, or None. dance: ДЕМОН's own dance frame
        (h6 mimicry). Returns (rects, overlays)."""
        sn = sn or {}
        if dance is not None and self.mimic_on(now):                     # h6: МИМИКРИЯ, it plays at being him, a beat late
            self.buf = [b for b in self.buf if now - b[0] < 0.5] + [(now, dance)]
            if True:
                late = next((b[1] for b in self.buf if now - b[0] <= 0.24), dance)
                out = [r[:] for r in late]
                if self.rng.random() < 0.04:                                   # one frame slips: its eye shows
                    out += [[OX + 6, OY + 4, 1, 2, RED, 1.0]]
                return out, []
        hits = {k: sn.get(k, 0) >= 0.5 and sn.get(k, 0) > self.prev[k] + 0.2 for k in self.prev}
        self.prev = {k: sn.get(k, 0) for k in self.prev}
        hit = hits['kick'] or hits['snare']; lvl = sn.get('level', 0) if music else 0.0
        self._hit = hit; self._hits = hits                                   # h7
        if music:
            sec = sn.get('section', 0)
            if sec != self.sec or now - self.move_t > 22:
                self.sec = sec; self.move_t = now
                self.move = self.rng.choice([m for m, _ in FORM_MOVES if m != self.move])
        else:
            self.move = 'stare'
            if now > self.next_tick: self.next_tick = now + self.rng.uniform(6, 12); hit = True; self.jerk = (self.rng.choice((-1, 1)), now)
        body = [r[:] for r in rects if not (OY + 4 <= r[1] < OY + 6 and OX + 2 <= r[0] < OX + 12 and r[4] != '#07060D')]
        horns = []
        for r in body:
            if int(round(r[1] - OY)) == 0 and 0.9 <= r[2] <= 1.1:
                o = -1 if r[0] - OX <= 6 else 1
                horns += [[r[0] + o * 0.5, r[1] - 1, 1, 1, r[4], r[5]], [r[0] + o, r[1] - 2, 1, 1, r[4], r[5]], [r[0] + o * 1.5, r[1] - 3, 1, 1, r[4], r[5]]]
        body += horns
        extra, ov, limbs = [], [], []
        ex = 4.0; ey = 0.0                                                      # slit eye position on the visor (cell 0-9)
        tq = math.floor(now * 8) / 8                                            # h7: the law, it never tweens: motion in snaps
        m = self.move
        if m == 'contort':
            A = 0.4 + 0.8 * lvl
            if hit: self.jerk = (self.rng.choice((-2, -1, 1, 2)), now)
            jx = self.jerk[0] if now - self.jerk[1] < 0.15 else 0
            body = [[x + (jx if y < OY + 4 else 0), y + round(0.6 * A * math.sin(tq * 3.1 + (x - OX) * 0.9) * 5) / 5, w, h, c, a] for x, y, w, h, c, a in body]
            if hits['kick']: body = [[x + (1 if x > OX + 7 else -1) if y >= OY + 8 else x, y, w, h, c, a] for x, y, w, h, c, a in body]
        elif m == 'tick':
            if hit:
                self.ghosts.append((self.tp, now)); self.tp = (self.rng.randint(-3, 3), -self.rng.randint(0, 2))
            for (gx, gy), t0 in self.ghosts:
                u = now - t0
                if u < 0.45: extra += [[x + gx, y + gy, w, h, RED, 0.35 * (1 - u / 0.45)] for x, y, w, h, c, a in body[::2]]
            self.ghosts = [g for g in self.ghosts if now - g[1] < 0.45][-4:]
            body = [[x + self.tp[0], y + self.tp[1], w, h, c, a] for x, y, w, h, c, a in body]
        elif m == 'spider':
            if hits['hat'] or hit:
                self.gait += 1
                if abs(self.sx - self.sx_to) < 0.3: self.sx_to = self.rng.uniform(-3, 4)
            self.sx = self.sx_to                                                # h7: no glide, it jumps
            sx = round(self.sx * 5) / 5
            body = [[x + sx, y + 1, w, h, c, a] for x, y, w, h, c, a in body if y < OY + 8]
            for side, bx in ((-1, OX + 1), (1, OX + 12)):
                for k in range(4):
                    up = (self.gait + k + (side > 0)) % 2
                    by = OY + 4 + k * 1.3; kx, ky = bx + side * 2.2, by - 1.6 - 0.8 * up; fx, fy = bx + side * (3.2 + 0.4 * k), OY + 10 - 0.6 * up
                    for t in range(5):
                        u = t / 4; limbs.append([sx + bx + (kx - bx) * u, by + (ky - by) * u, 0.6, 0.6, INK, 1.0])
                        limbs.append([sx + kx + (fx - kx) * u, ky + (fy - ky) * u, 0.6, 0.6, INK, 1.0])
                    extra.append([sx + fx, fy, 0.5, 0.5, RED, 0.9])
        elif m == 'split':
            if hits['kick']: self.split_snap = now; ov.append(('flash', (RED, 0.3)))
            k = 0 if now - self.split_snap < 0.15 else (3 + 1.5 * math.sin(tq * 1.7))
            for side, ph in ((-1, 0.0), (1, 2.1)):
                off = side * k + 0.6 * math.sin(tq * 4 + ph)
                extra += [[x + off, y + 0.4 * math.sin(tq * 3 + ph), w, h, RED if (int(x * 3 + y) % 3 == 0) else INK, 0.45] for x, y, w, h, c, a in body
                          if y >= OY]                                           # h19: the copies skip the horns (they smeared into a bar)
        elif m == 'rewrite':
            band = OY - 3 + ((now * 4) % 15)
            if 0 <= now - sn.get('drop_t', -99) < 0.5: band = OY + 12
            gl = []
            keep = []
            for r in body:
                if r[1] < band and 0.9 <= r[2] <= 1.1:
                    if _hash(int(r[0] * 3), int(r[1] * 3), int(now * 3)) < 0.55:
                        gl.append((r[0], r[1] - 0.2, GLYPHS[int(_hash(int(r[0]), int(r[1]), int(now * 2)) * len(GLYPHS))], 0.85, RED if r[1] % 2 else PINK))
                else: keep.append(r)
            body = keep
            extra.append([OX - 1, band, 16, 0.25, PINK, 0.8])
            ov.append(('glyphs', gl))
        if m == 'stare' or m == 'tick':
            if mouse is not None:
                ex = clamp(4 + mouse[0] / 4, 0, 9); ey = clamp(mouse[1] / 30, -0.4, 0.4)
                if math.hypot(*mouse) < 22 and now - self.lunge_t > 3: self.lunge_t = now; self.line = ('ВИЖУ.', now + 1.2)
            lu = now - self.lunge_t
            if lu < 0.3 and mouse is not None:
                d = math.hypot(*mouse) or 1; kx, ky = mouse[0] / d * 1.6, mouse[1] / d * 1.0
                body = [[x + kx, y + ky, w, h, c, a] for x, y, w, h, c, a in body]
                extra += [[OX + 2 + n, OY + 5.5 + ky, 1, 0.5, BONE, 0.95] for n in range(0, 10, 2)]
            n = 1 + int((lvl if music else 0.3) * 6)
            for k, (cx_, cy_) in enumerate(self.eyes[:n]):
                if k == 0: continue
                if int(now * 1.3 + k * 1.7) % 5 == 0: continue
                extra.append([OX + cx_, OY + cy_, 1, 1, RED, 0.85])
        body += limbs
        # possessed palette: black body, red rim underneath, slit eye + a cluster
        blk = [[x, y, w, h, '#000000' if c.upper() == '#07060D' else INK, a] for x, y, w, h, c, a in body]
        rim = []
        for dx, dy in ((-0.4, 0), (0.4, 0), (0, -0.4), (0, 0.4)):
            rim += [[x + dx, y + dy, w, h, RED, 0.9 * a] for x, y, w, h, c, a in body]
        eyes = [[OX + 2 + ex, OY + 4 + ey, 1, 2, RED, 1.0], [OX + 1 + ex, OY + 4.5, 0.6, 0.6, RED, 0.5], [OX + 3.4 + ex, OY + 5, 0.6, 0.6, RED, 0.45]]
        if m in ('tick',): eyes = [[x + self.tp[0], y + self.tp[1], w, h, c, a] for x, y, w, h, c, a in eyes]
        if m == 'spider': eyes = [[x + round(self.sx * 5) / 5, y + 1, w, h, c, a] for x, y, w, h, c, a in eyes]
        if self.rng.random() < (0.5 if music else 0.15):
            extra += [[x + self.rng.uniform(-1, 1), y, w, h, RED, 0.16] for x, y, w, h, c, a in blk[::6]]
        if music and hit and self.ctx is None and lvl >= 0.8 and now - self.said > 8 and self.rng.random() < 0.35:   # h7
            self.said = now; self.line = (self.rng.choice(FORM_LINES), now + 1.4)
        elif not music and now - self.said > 30 and self.rng.random() < 0.004:
            self.said = now; self.line = (self.rng.choice(FORM_LINES), now + 1.6)
        if self.line and now < self.line[1]: ov.append(('shout', (self.line[0], clamp((self.line[1] - now) / 0.4))))
        if self.rng.random() < 0.25:
            ov.append(('glyphs', [(OX - 2 + self.rng.random() * 18, OY - 6 + self.rng.random() * 14, self.rng.choice(GLYPHS), 0.25 + 0.4 * self.rng.random(), RED) for _ in range(3)]))
        hg = self.hunger()                                                 # h6: fed = bigger and redder, starving = it flickers
        if hg > 0.7:
            k = (hg - 0.7) / 0.3
            for (cx_, cy_) in self.eyes[1:]:
                extra.append([OX + cx_, OY + cy_, 1, 1, RED, 0.6 + 0.4 * k])
            rim += [[x + dx, y + dy, w, h, RED, 0.5 * k * a] for dx, dy in ((-0.8, 0), (0.8, 0), (0, -0.8)) for x, y, w, h, c, a in body[::2]]
            for r in horns: extra.append([r[0] + (r[0] - OX - 7) * 0.15, r[1] - 1, 1, 1, INK, 1.0])
        elif hg < 0.3 and self.rng.random() < 0.6 - hg:
            keep = 0.75 + hg
            blk = [r for r in blk if self.rng.random() < keep]
        if now - self.tear_t < 1.2:                                        # h6: it held on: his window tears
            u = (now - self.tear_t) / 1.2
            ov.append(('tear', (self.rng.uniform(-4, 4), 2 + 4 * (1 - u), RED)))
            ov.append(('flash', (RED, 0.35 * (1 - u))))
        ov.append(('under', rim))
        self._parts = (blk, extra, eyes, rim)                                # h7
        return blk + extra + eyes, ov

    # ================================================================ h7: Death Grips grammar
    def song(self, now, key, dg=False, steroids=False, lure=False):
        """every track change (key None = music stopped): per-song state; a song it rotted through leaves more СЛЕДЫ."""
        if self.rot >= 0.95 and self.state():
            r = random.Random(f'{self.song_key}{now}'); rs = self.mem.d.get('residue') or {}; day = time.strftime('%F', time.localtime(now))
            if rs.get('day') != day: rs = dict(day=day, cells=[])
            rs['cells'] = (rs.get('cells') or []) + [[r.randint(1, 13), r.randint(1, 9)] for _ in range(4)]
            self.mem.d['residue'] = rs; self.mem.save(); log(f'hurt: {FORM_NAME} rotted through the song: more СЛЕДЫ')
        self.song_key = key; self.dg = bool(dg and key); self.steroids = bool(steroids and key); self.hard = self.dg
        self.det_max = 4 if self.steroids else 2 if self.dg else 0
        self.dets = 0; self.det_t = -99; self.targets = None; self.done_t = set(); self.arc = None; self.smelled = False
        self.rot = 0.0; self.vanish = False; self.vanishes = 0; self.skips = 0; self.hold_n = 0; self.loud_t = -9; self.loud_run = now
        self.krik_t = -9; self.krik_w = None; self.wi = 0; self.kicks = []; self.pre = None; self.pre_for = None; self.shards = []
        self.drop_only = False; self.lv = []; self.rk = []; self.rs = []; self.ear_prev = dict(kick=0, snare=0); self.kick_now = False
        self.live_cd = 0.0
        self.lure = bool(lure and key); self.cracks = 0; self.face = None; self.face_t = -9; self.mask_off = False      # h9
        self.pose = (0, 0); self.pose_t = -9; self.rh = []; self.vanish_t = -9; self.lure_pv = getattr(self, 'lure_pv', 0)
        if key: log(f'hurt: {FORM_NAME} song: {"ДЕЛИКАТЕС" if self.dg else "-"}{" (Steroids)" if self.steroids else ""}'
                    f'{" ПРИМАНКА" if self.lure else ""}, detonations ≤ {self.det_max}')

    def set_hard(self, hard, soft=False):
        """the desk tells it every second whether the song is hard (mode / weather / the sound); Death Grips always is.
        h8: a song that is neither hard nor soft still gets one blast, but only on a real drop (build -> gap -> slam)."""
        h = bool(hard) or self.dg; s = bool(soft) and not h
        do = not h and not s
        if h != self.hard or do != self.drop_only or (s and self.det_max and not self.dg):
            self.hard = h; self.drop_only = do
            if not self.dg: self.det_max = 1 if (h or do) else 0
            if self.targets == [] or (s and self.targets): self.targets = None

    def set_targets(self, ts):
        self.targets = [float(t) for t in ts or []]
        log(f'hurt: {FORM_NAME} will blow up at ' + (', '.join(f'{int(t) // 60}:{int(t) % 60:02d}' for t in self.targets) or 'the hardest live moment'))

    def preview(self, now):
        """right-click > ▶ ДЕТОНАЦИЯ: the arc right now (short wind-up), with or without music."""
        self.arc = dict(ph='wind', t=now, at=None, lead=2.4, power=2.7, pv=True, k=0.0); log(f'hurt: {FORM_NAME} detonation preview')

    def chorus_off(self, now):
        """the desk keeps the lyric line out of the caption while КРИК carries the chorus."""
        return now - self.krik_t < 1.2

    # ---- ВПЕРЕДИ: it rushes the beat
    def _ahead(self, sn, now):
        sn = dict(sn or {}); k = sn.get('kick', 0) or 0
        if k >= 0.5 and k > self.kprev + 0.2: self.kicks = [t for t in self.kicks if now - t < 6][-8:] + [now]
        self.kprev = k
        d = [b - a for a, b in zip(self.kicks, self.kicks[1:]) if 0.25 <= b - a <= 1.2]
        if len(d) >= 4:
            d.sort(); med = d[len(d) // 2]; mad = sorted(abs(x - med) for x in d)[len(d) // 2]
            if mad < 0.12 * med:
                nxt = self.kicks[-1] + med
                while nxt < now - 0.05: nxt += med
                key = round(nxt, 2)
                if key != self.pre_for and nxt - (self.rng.uniform(0.06, 0.12) if self._lure_on(now) else self.rng.uniform(0.03, 0.09)) <= now < nxt + 0.1:
                    self.pre_for = key; self.pre = now
        if self.pre is not None and now - self.pre < 0.2: sn['kick'] = 1.0             # lands 30-90 ms early, the real kick is swallowed
        return sn

    # ---- h8: the live ear (real hits, before ВПЕРЕДИ fakes the kick)
    def _ear(self, sn, now, lvl):
        self.lv = [p for p in self.lv if now - p[0] < 6.0] + [(now, lvl)]
        self.kick_now = False
        for k, lst in (('kick', self.rk), ('snare', self.rs)):
            v = (sn or {}).get(k, 0) or 0
            if v >= 0.5 and v > self.ear_prev[k] + 0.2:
                lst.append(now)
                if k == 'kick': self.kick_now = True
            self.ear_prev[k] = v
        self.rk = [t for t in self.rk if now - t < 6.0]; self.rs = [t for t in self.rs if now - t < 6.0]
        hv = (sn or {}).get('hat', 0) or 0                                                     # h9: chops for КУКЛА
        if hv >= 0.5 and hv > getattr(self, 'hprev', 0) + 0.2: self.rh = [t for t in getattr(self, 'rh', []) if now - t < 2.0] + [now]
        self.hprev = hv

    def _building(self, now):
        """loudness rising over the last 4 s, or the snare roll speeding up."""
        pts = [(t - now, l) for t, l in self.lv if now - t < 6.0]
        if len(pts) >= 30 and pts[-1][0] - pts[0][0] >= 4.0:
            mx = sum(p[0] for p in pts) / len(pts); my = sum(p[1] for p in pts) / len(pts)
            vx = sum((p[0] - mx) ** 2 for p in pts) or 1e-9
            slope = sum((p[0] - mx) * (p[1] - my) for p in pts) / vx
            if slope > 0.02 and pts[-1][1] >= 0.45: return True
        r1 = sum(1 for t in self.rs if now - t < 1.0); r2 = sum(1 for t in self.rs if 1.0 <= now - t < 3.0) / 2.0
        return r1 >= 4 and r1 >= 1.5 * max(1.0, r2)

    def _gap(self, now, a, lvl):
        """the cut before the drop: no drums for 0.45 s after dense hits, or the level falls under 70 % of the build."""
        hits = sorted(self.rk + self.rs)
        dense = sum(1 for t in hits if 0.45 <= now - t < 2.45) >= 4
        nodrums = dense and not any(now - t < 0.45 for t in hits)
        if lvl < 0.7 * a['mx'] and a['mx'] >= 0.55: a['low'] = a.get('low') or now
        else: a['low'] = None
        return nodrums or (a['low'] is not None and now - a['low'] >= 0.15)

    def _jump(self, now, lvl):
        lows = [l for t, l in self.lv if now - t < 0.8]
        return self.kick_now and lvl >= 0.8 and lows and lvl - min(lows) >= 0.3

    # ---- the hype arc
    def _power(self, ctx, at):
        if ctx and ctx.get('drop_at') is not None and abs(ctx['drop_at'] - at) < 0.5: return ctx.get('drop_power')
        return None
