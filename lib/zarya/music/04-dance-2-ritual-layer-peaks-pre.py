class _Dance2:     # mixin of Dance (v35 split; one class in the original)

    def ritual_layer(self, rit, k, s, t, h):
        """(attach to his body, under him, extra on top, overlays) for summon / cult / pagan / none at build-up k (0-1)."""
        attach, under, extra, ov = [], [], [], []
        if k <= 0.01: return attach, under, extra, ov
        cx, cy = OX + 7, OY + 10.3
        if rit == 'summon':
            glow = 0.55 + 0.45 * (s.get('kick', 0))
            n = int(44 * min(1.0, k * 1.3))
            for i in range(n):
                a = 2 * math.pi * i / 44
                under.append([cx + 9.5 * math.cos(a) - 0.3, cy + 1.5 * math.sin(a) - 0.2, 0.6, 0.4, C['R'], 0.75 * glow])
                if i % 2 == 0: under.append([cx + 6.5 * math.cos(a) - 0.2, cy + 1.0 * math.sin(a) - 0.15, 0.4, 0.3, C['X'], 0.55 * glow])
            for i in range(int(8 * k)):                                           # marks between the rings
                a = 2 * math.pi * (i + 0.5) / 8
                under.append([cx + 8 * math.cos(a) - 0.3, cy + 1.25 * math.sin(a) - 0.3, 0.6, 0.6, C['R'], 0.5 * glow])
            for i in range(5):                                                    # candles
                if k < (i + 1) / 6: continue
                a = 2 * math.pi * i / 5 - math.pi / 2
                x, y = cx + 9.5 * math.cos(a), cy + 1.5 * math.sin(a)
                fl = self.rng.random()
                extra += [[x - 0.2, y - 1.0, 0.4, 0.9, '#E4E0EA', 0.9], [x - 0.2, y - 1.5 - 0.2 * fl, 0.4, 0.5, C['orange'] if fl > 0.4 else '#FFD08A', 0.95]]
            if k > 0.55:                                                          # the shadow rises behind him
                r_ = min(1.0, (k - 0.55) / 0.45); sc = 1.7; top = OY + 9 - len(SHADE) * sc - 8 * r_
                for yy, row in enumerate(SHADE):
                    for xx, ch in enumerate(row):
                        if ch == 'X': under.insert(0, [cx - 4.5 * sc + xx * sc, top + yy * sc, sc, sc, '#0A0610', 0.85 * r_])
                ey = top + 4 * sc
                under += [[cx - 4.5 * sc + 2 * sc + 0.3, ey + 0.3, sc - 0.6, sc - 0.6, C['R'], r_ * (0.6 + 0.4 * glow)],
                          [cx - 4.5 * sc + 6 * sc + 0.3, ey + 0.3, sc - 0.6, sc - 0.6, C['R'], r_ * (0.6 + 0.4 * glow)]]
            if h['kick'] and k > 0.5: ov.append(('flash', (C['R'], 0.12)))
        elif rit == 'cult':
            spots = [(0.2, OY + 4.4, 0.85), (2.6, OY + 3.6, 0.85), (16.8, OY + 3.6, 0.85), (19.0, OY + 4.4, 0.85), (5.4, OY - 2.2, 0.6), (12.6, OY - 2.2, 0.6)]
            sway = 0.25 * math.sin(s.get('phase', 0) * 2 * math.pi)
            hit = h['kick'] or h['snare']
            for i, (x0, y0, sc) in enumerate(spots):
                if k < (i + 1) / 7: continue
                for yy, row in enumerate(HOOD):
                    for xx, ch in enumerate(row):
                        if ch == 'X': under.append([x0 + xx * sc + sway * (1 - yy / 7), y0 + yy * sc, sc, sc, '#120E18', 0.95])
                under.append([x0 + 1 * sc + sway, y0 + 2 * sc, sc, sc * 0.6, C['R'], 1.0 if hit else 0.45])     # the eye in the hood
                if self.rng.random() < 0.04: self.chant.append([x0 + sc, y0 - 0.5, self.rng.choice(GLYPHS), 1.0])
            keep = []
            for p in self.chant:
                p[1] -= self.dt * 1.6; p[3] -= self.dt * 0.6
                if p[3] > 0: keep.append(p)
            self.chant = keep[-14:]
            ov.append(('glyphs', [(p[0], p[1], p[2], 0.6 * p[3], C['X']) for p in self.chant]))
        elif rit == 'pagan':
            lvl = s.get('level', 0)
            for x in range(-1, 16):                                               # bonfire behind him: flames climb past his head
                mid = 1 - abs(x - 7) / 9
                hgt = (3 + (6 + 9 * lvl) * mid * (0.6 + 0.4 * math.sin(t * 9 + x * 1.7) * self.rng.random())) * k
                for yy in range(int(hgt)):
                    f = yy / max(1, hgt)
                    core = abs(x - 7) < 3 and f < 0.45
                    col = '#FFD08A' if core else C['orange'] if f < 0.5 else C['R'] if f < 0.82 else '#5A0E1E'
                    if self.rng.random() < 0.12 and f > 0.4: continue                     # ragged flame edges
                    under.append([OX + x - 0.5, OY + 9.6 - yy, 1, 1, col, (0.55 if f < 0.2 else 0.8) * (1 - f * 0.5)])
            for x0, hh in ((0, 9), (18.6, 8)):                                    # standing stones
                under += [[x0, OY + 10 - hh, 1.4, hh, '#3A3450', 0.95 * k], [x0, OY + 10 - hh, 1.4, 0.5, '#6E6787', 0.9 * k]]
            mc = C['R'] if k > 0.6 else '#E4E0EA'                                  # the moon turns red
            for yy, w in enumerate((2, 4, 5, 5, 4, 2)):
                under.append([16 - w / 2, OY - 18 + yy, w, 1, mc, 0.55 * k])
            for side, x0 in ((1, OX + 1), (-1, OX + 12)):                         # antlers grow from his horns
                for i, (dx, dy) in enumerate(ANTLER[:int(len(ANTLER) * k)]):
                    attach.append([x0 + dx * side, OY + dy, 1, 1, '#C2C0C9', 0.95])
            if self.rng.random() < 0.4 * k: self.sparks2.append([OX + 4 + self.rng.random() * 8, OY + 6, (self.rng.random() - 0.5), -3 - 2 * self.rng.random(), 1.0])
            keep = []
            for p in self.sparks2:
                p[0] += p[2] * self.dt; p[1] += p[3] * self.dt; p[4] -= self.dt * 0.7
                if p[4] > 0: keep.append(p); extra.append([p[0], p[1], 0.3, 0.3, C['ember'], 0.8 * p[4]])
            self.sparks2 = keep[-30:]
        else:                                                                     # none: digital only, the scanlines tear
            if self.rng.random() < 0.5 * k: ov.append(('tear', (self.rng.uniform(-8, 4), self.rng.uniform(1, 4), self.rng.choice((C['R'], C['B'])))))
        return attach, under, extra, ov

    # ---------------------------------------------------------------- m4: calm modes
    def _drift(self, lst, dt, rise, fade, cap=60):
        keep = []
        for p in lst:
            p[0] += p[2] * dt; p[1] += p[3] * dt; p[4] -= dt * fade
            if p[4] > 0: keep.append(p)
        return keep[-cap:]

    def sky_stars(self, t, n=12, top=-14, bot=-2, a=0.35):
        if self.stars is None:
            r = random.Random(7); self.stars = [(r.uniform(0, 20), r.uniform(OY + top, OY + bot), r.random() * 6) for _ in range(n)]
        return [[x, y, 0.3, 0.3, C['B'], a * (0.5 + 0.5 * math.sin(t * 1.3 + ph))] for x, y, ph in self.stars]

    def m_rest(self, body, var, s, t, eye, h, A):
        """ПРИВАЛ: after the battle. Sits against a rock, leans back, breathes slow, smokes; stars over him."""
        breath = -0.2 if (t % 4.6) < 2.3 else 0.0
        body = [r for r in body if not self.is_eye(r, eye)]
        body = self.warp(body, lambda x, y: (x - round(0.6 * max(0.0, (OY + 8 - y)) / 8 * 5) / 5, y + 1 + (breath if y < OY + 7 else 0)))
        body = [[x, y, w, hh, c, a * 0.9] for x, y, w, hh, c, a in body]
        lid = 0.0 if self.cath_t is None else 1.0
        e = eye or C['G']
        eyes = [[OX + 2 + n - 0.6, OY + 6 + breath, 1, 0.5 + 0.5 * lid, e, 0.75] for n in (3, 4, 5)]       # half-closed, looks down
        under = [[OX - 3 + cx, OY + 1 + top, 1, 10 - top, '#2A2440', 0.92] for cx, top in ROCK]
        under += [[OX - 3 + cx, OY + 1 + top, 1, 0.4, '#43355A', 0.9] for cx, top in ROCK]
        under += [[0, OY + 10.2, 20, 0.3, '#30263F', 0.8]]                                                   # ground
        extra = self.sky_stars(t)
        # the cigar and its ember: inhale every ~6 s
        inh = (t % 6.2) > 5.2
        tipx, tipy = OX + 12.4, OY + 6.6 + breath
        extra += [[tipx - 1.4, tipy, 1.4, 0.4, '#6B4A3A', 0.95], [tipx, tipy, 0.45, 0.4, C['orange'] if inh else C['ember'], 1.0 if inh else 0.75]]
        if self.rng.random() < 0.25: self.smoke.append([tipx + 0.2, tipy - 0.2, 0.3 + self.rng.random() * 0.3, -0.9 - self.rng.random() * 0.4, 1.0])
        if (h['vocal'] and t - self.puff_t > 3.5) or (t % 6.2 < self.dt and t - self.puff_t > 3):                  # exhale
            self.puff_t = t
            for _ in range(5): self.smoke.append([OX + 8 + self.rng.random() * 2, OY + 5.5, 0.6 + self.rng.random() * 0.8, -1.2 - self.rng.random(), 1.4])
        self.smoke = self._drift(self.smoke, self.dt, 0, 0.32)
        for p in self.smoke:
            p[0] += 0.25 * math.sin(t * 1.7 + p[1]) * self.dt
            sz = 0.35 + (1.4 - min(1.4, p[4])) * 0.5
            extra.append([p[0], p[1], sz, sz, '#A9A4B6', 0.28 * min(1.0, p[4])])
        return body + eyes, extra, [('under', under)], False

    def m_drive(self, body, var, s, t, eye, h, A):
        """ТРАССА: the night road. He sits still in the dark, street lights pass, the road runs under him. Lonely, steady."""
        bpm = s.get('bpm') or 100
        speed = 7 + bpm / 22
        sw = round(0.2 * math.sin(t * 0.45) * 5) / 5
        bump = -0.2 if s.get('kick', 0) > 0.7 else 0.0
        body = self.warp(body, lambda x, y: (x + sw * (1 - (y - OY) / 10), y + bump))
        body = [[x, y, w, hh, c, a * 0.88] for x, y, w, hh, c, a in body]
        under = []
        if self.skyline is None:
            r = random.Random(11); xx = -2; self.skyline = []
            while xx < 60: w = r.randint(2, 4); self.skyline.append((xx, w, r.randint(2, 7), [(r.random(), r.random()) for _ in range(3)])); xx += w + r.randint(0, 1)
        off = (t * speed * 0.12) % 60
        for x0, w, hh, wins in self.skyline:
            x = (x0 - off) % 60 - 4
            if x > 21: continue
            under.append([x, OY + 9.6 - hh, w, hh, '#1D1727', 0.95])
            for wx, wy in wins:
                if (int(t * 0.2 + wx * 10) % 5): under.append([x + wx * (w - 0.4), OY + 9.6 - hh + 0.6 + wy * (hh - 1.2), 0.35, 0.35, WCOL['clear'], 0.22])
        under.append([0, OY + 9.9, 20, 0.6, '#17121F', 0.95])                                                # road
        for k in range(7):
            x = (k * 4 - (t * speed) % 4) - 2
            under.append([x, OY + 10.15, 1.6, 0.18, C['B'], 0.35])
        per = max(1.2, 4 * 60 / bpm)
        if t - self.pole_t > per: self.pole_t = t; self.poles.append(22.0)
        keep, extra, sweep = [], [], None
        for x in self.poles:
            x -= self.dt * speed * 1.6
            if x > -3:
                keep.append(x)
                extra.append([x, OY - 9, 0.45, 19, '#30263F', 0.85])
                extra.append([x - 0.6, OY - 9.3, 1.2, 0.4, WCOL['clear'], 0.9])
                extra.append([x - 1.6, OY - 8.9, 3.2, 0.25, WCOL['clear'], 0.18])
                c = x - OX - 2
                if -1 <= c <= 10: sweep = c
        self.poles = keep[-6:]
        if sweep is not None:                                                            # the light slides over him
            extra += self.visor([(n, r, WCOL['clear'], 0.35 * (1 - abs(n - sweep) / 3)) for n in range(10) for r in (4, 5) if abs(n - sweep) < 3])
            body = [[x, y, w, hh, c, a] for x, y, w, hh, c, a in body] + \
                   [[x, y, w, hh, WCOL['clear'], 0.10] for x, y, w, hh, c, a in body[::3] if abs(x - (OX + 2 + sweep)) < 2.5]
        if h['vocal'] and self.rng.random() < 0.3: extra += self.visor([(n, 5, C['P'], 0.25) for n in range(10)])
        return body, extra, [('under', under)], False

    def m_bolero(self, body, var, s, t, eye, h, A):
        """БОЛЕРО: a slow three-beat sway with a rose; on a long sung note he closes his eye and leans back."""
        bpm = s.get('bpm') or 78
        per = 3 * 60 / bpm * 2
        ph = (t % per) / per
        sw = 0.6 * math.sin(2 * math.pi * ph)
        dip = 0.2 if ph < 0.08 or 0.5 <= ph < 0.58 else 0.0
        if h['vocal'] and s.get('excite', 0) < 0.8 and t > self.close_until + 2 and self.rng.random() < 0.3: self.close_until = t + 1.4
        lean = 0.5 if t < self.close_until else 0.0
        f = lambda x, y: (x + round((sw - lean) * (1 - (y - OY) / 10) * 5) / 5, y + (dip if y < OY + 8 else 0))
        body = self.warp(body, f)
        if t < self.close_until:
            e = eye or C['G']
            body = [r for r in body if not self.is_eye(r, eye)] + self.warp(self.visor([(n, 5, e, 0.9) for n in range(3, 7)]), f)
        rose = [[OX + 14.3, OY + 4.6, 0.3, 3.0, '#8FAE8B', 0.9], [OX + 13.6, OY + 5.6, 0.7, 0.3, '#8FAE8B', 0.8],
                [OX + 13.8, OY + 3.4, 1, 1, C['X'], 0.95], [OX + 14.8, OY + 3.6, 0.8, 0.8, '#D07A66', 0.95],
                [OX + 14.2, OY + 2.8, 0.8, 0.7, C['P'], 0.9]]
        rose = self.warp(rose, f)
        if self.rng.random() < 0.012 + 0.03 * s.get('vocal', 0):
            self.petals.append([rose[2][0], rose[2][1], -0.4 - self.rng.random() * 0.5, 0.9 + self.rng.random() * 0.5, 1.0])
        self.petals = self._drift(self.petals, self.dt, 0, 0.18)
        extra = rose + [[p[0] + 0.4 * math.sin(t * 2 + p[1]), p[1], 0.45, 0.3, C['P'], 0.7 * min(1, p[4])] for p in self.petals if p[1] < OY + 10.3]
        ov = [('flash', ('#FF9A5C', 0.05 + 0.025 * math.sin(t * 1.1)))]                       # candle light
        return body, extra, ov, False

    def m_run(self, body, var, s, t, eye, h, A):
        """БЕГ: running into the dusk to reach someone. At the song's hook (the title line / chorus, from synced lyrics;
        no lyrics: a drop after 30 %) he stops: only an outline is where they were, and it fades. Then he runs again."""
        ctx = getattr(self, 'ctx', {}) or {}; pos = ctx.get('pos', -1)
        if pos is not None and pos >= 0:
            prev = self.last_pos if self.last_pos is not None else pos
            for hk in ctx.get('hooks') or []:
                if prev < hk <= pos + 0.05 and hk not in self.hook_seen and (self.hook_t is None or t - self.hook_t > 12):
                    self.hook_seen.add(hk); self.hook_t = t; log(f'peak: БЕГ hook at {int(hk) // 60}:{int(hk) % 60:02d}')
            self.last_pos = pos
        if not ctx.get('hooks') and s.get('drop_t', -99) > self.run_drop + 30 and (s.get('progress') or 0) > 0.3 and t - s.get('drop_t', -99) < 0.3:
            self.run_drop = s['drop_t']; self.hook_t = t; log('peak: БЕГ hook (drop)')
        u = (t - self.hook_t) if self.hook_t is not None else 99
        k = 1.0 if u > 4.8 else max(0.0, 1 - u / 0.6) if u < 0.6 else 0.0 if u < 4.0 else (u - 4.0) / 0.8
        self.run_stop = k < 0.3
        lean = 0.7 * k
        bob = -0.2 * k if int(t * 6) % 2 else 0.0
        body = self.warp(body, lambda x, y: (x - round(lean * max(0.0, (OY + 8 - y)) / 8 * 5) / 5, y + (bob if y < OY + 8 else 0)))
        under = [[0, OY - 36 + i * 2, 20, 2, '#FF9A5C', 0.30 * (i / 22) ** 2] for i in range(23)]          # dusk, soft from the top
        for yy, w in enumerate((2, 4, 4, 2)):                                                            # small low sun, upper left
            under.append([3 - w / 2, OY - 9 + yy, w, 1, '#FFD08A' if yy < 2 else '#FF9A5C', 0.75])
        under.append([0, OY + 9.9, 20, 0.25, C['P'], 0.45])
        if not hasattr(self, 'run_off'): self.run_off = 0.0
        self.run_off += self.dt * 12 * k
        for j in range(6):
            x = (j * 4 + self.run_off) % 24 - 2
            under.append([x, OY + 10.3, 1.5, 0.2, C['B'], 0.3])
        extra = []
        if k > 0.6:
            for _ in range(2):
                y = OY + self.rng.random() * 9; L = 1 + self.rng.random() * 2.5
                extra.append([OX + 15 + self.rng.random() * 3, y, L, 0.12, C['B'], 0.35 * k])
        if u < 4.8:                                                                                      # the one who is not there
            a = 0.0 if u < 0.6 else min(1.0, (u - 0.6) / 0.4) * max(0.0, 1 - (u - 1.0) / 3.0)
            if a > 0.01:
                for yy, row in enumerate(KIN):
                    for xx, ch in enumerate(row):
                        if ch == 'X': extra.append([16.2 + xx * 0.7, OY + 5 + yy * 0.75, 0.7, 0.75, C['B'], 0.30 * a])
                extra.append([16, OY + 9.9, 4, 0.2, C['B'], 0.25 * a])
            if u > 0.6: body = [r for r in body if not self.is_eye(r, eye)] + self.visor([(8, 4, eye or C['G'], 0.9), (9, 4, eye or C['G'], 0.9)])
        return body, extra, [('under', under)], False

    def m_hum(self, body, var, s, t, eye, h, A):
        """НАПЕВ: a gentle walk. Little notes float up on the melody, grass passes at his feet, the head tilts."""
        step = int(s.get('phase', 0) * 2 if s.get('bpm') else t * 2) % 2
        bob = -0.2 if step else 0.0
        tilt = round(0.4 * math.sin(t * 1.3) * 5) / 5
        body = self.warp(body, lambda x, y: (x + (tilt if y < OY + 3 else 0), y + (bob if y < OY + 8 else 0)))
        if (h['vocal'] or h['hat']) and self.rng.random() < 0.18:
            self.notes.append([OX + 12 + self.rng.random() * 2, OY + 1, 0.5 + self.rng.random() * 0.5, -1.4 - self.rng.random() * 0.6, 1.0,
                               self.rng.choice((C['G'], C['B'], C['L']))])
        keep, extra = [], []
        for p in self.notes:
            p[0] += (p[2] + 0.5 * math.sin(t * 3 + p[1])) * self.dt; p[1] += p[3] * self.dt; p[4] -= self.dt * 0.4
            if p[4] > 0:
                keep.append(p)
                for yy, row in enumerate(NOTE):
                    for xx, ch in enumerate(row):
                        if ch == 'X': extra.append([p[0] + xx * 0.4, p[1] + yy * 0.4, 0.4, 0.4, p[5], 0.8 * min(1, p[4] * 1.5)])
        self.notes = keep[-12:]
        off = (t * 2.2) % 5
        under = [[(j * 5 - off) - 1 + dx, OY + 9.9 - hh, 0.3, hh, '#8FAE8B', 0.55] for j in range(6) for dx, hh in ((0, 0.6), (0.4, 0.9), (0.8, 0.5))]
        under.append([0, OY + 9.95, 20, 0.2, '#30263F', 0.6])
        return body, extra, [('under', under)], False

    def catharsis(self, body, extra, ov, s, t, h, eye, mode):
        """m4 КАТАРСИС (calm / sad songs, instead of МАКС, the breach and the drop rings): a breath of stillness, then the eye
        opens, a column of light rises behind him with pale motes, he lifts a little and holds while the song holds."""
        lvl = s.get('level', 0)
        trig = (s.get('max_hold', 0) > 1.0 or (0 <= t - s.get('drop_t', -99) < 0.3 and lvl > 0.75) or
                (s.get('excite', 0) > 0.95 and lvl > 0.9))
        if self.cath_t is None and trig and t > self.cath_cool:
            self.cath_t = t; log('peak: КАТАРСИС')
        if self.cath_t is None: return body, extra, ov
        u = t - self.cath_t
        if (u > 2.5 and lvl < 0.72) or u > 8:
            if not hasattr(self, 'cath_end') or self.cath_end is None: self.cath_end = t
            v = t - self.cath_end
            if v > 0.8: self.cath_t = None; self.cath_end = None; self.cath_cool = t + 20; return body, extra, ov
            k = 1 - v / 0.8
        else:
            self.cath_end = None; k = 1.0 if u > 0.4 else 0.0
        if u < 0.4: return body, [e for e in extra if e[5] < 0.5], ov                        # stillness: only him
        lift = -round(1.0 * k * min(1, (u - 0.4) / 0.6) * 5) / 5
        body = self.shift([r for r in body if not self.is_eye(r, eye)], 0, lift)
        body += self.shift(self.visor([(4, 4, C['B'], 1.0), (5, 4, C['B'], 1.0), (4, 5, C['B'], 1.0), (5, 5, C['B'], 1.0)]), 0, lift)
        col = [[OX + 7 - wdt / 2, OY + 10 - 1.2 * (i + 1), wdt, 1.2, '#F4EEF7', 0.20 * k * (1 - i / 22)] for i in range(22) for wdt in (3.0, 6.0)]
        if self.rng.random() < 0.6: self.motes.append([OX + 7 + (self.rng.random() - 0.5) * 7, OY + 9, (self.rng.random() - 0.5) * 0.6, -2 - self.rng.random() * 2, 1.0])
        self.motes = self._drift(self.motes, self.dt, 0, 0.35)
        extra = extra + [[p[0], p[1], 0.35, 0.35, C['B'] if p[4] > 0.5 else C['P'], 0.6 * p[4] * k] for p in self.motes]
        ov = ov + [('under', col)]
        return body, extra, ov

    # ---------------------------------------------------------------- peak events
    def _peaks_pre(self, s, t, h, mode):
        """Build-up charge (before the mode draws, so the ears perk)."""
        self.charge += (s.get('build', 0) - self.charge) * min(1.0, self.dt * 3)
        if s.get('drop_t', -99) > self.drop_seen + 0.5 and 0 <= t - s.get('drop_t', -99) < 0.4:
            self.drop_seen = s['drop_t']
            if self.charge > 0.2 or s.get('excite', 0) > 0.95: self.explode_t = t; log(f'peak: drop (charge {self.charge:.2f})')
            self.charge = 0.0

