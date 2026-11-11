class _Dance1:     # mixin of Dance (v35 split; one class in the original)

    def m_memory(self, body, var, s, t, eye, h, A):
        bpm = s.get('bpm') or 70
        per = max(2.5, min(6.0, 4 * 60 / bpm))
        sw = 0.6 * math.sin(2 * math.pi * t / per)
        bob = round(0.2 * math.sin(2 * math.pi * t / per * 2) * 5) / 5
        body = self.warp(body, lambda x, y: (x + round(sw * (1 - (y - OY) / 12) * 5) / 5, y + bob))
        body = [[x, y, w, hh, c, a * 0.78] for x, y, w, hh, c, a in body]
        prog = s.get('progress')
        prog = 0.5 if prog is None else max(0.0, min(1.0, prog))
        extra = []
        for _ in range(5):
            extra.append([OX - 2 + self.rng.random() * 18, OY - 2 + self.rng.random() * 13, 0.4, 0.4, C['B'], 0.12 + self.rng.random() * 0.15])
        if self.rng.random() < 0.04: extra.append([OX - 1 + self.rng.random() * 16, OY - 3, 0.25, 14, C['B'], 0.10])
        dens = int(round(10 * (1 - prog) + 1))
        if len(self.parts) < dens and self.rng.random() < 0.5:
            self.parts.append([OX - 3 + self.rng.random() * 20, OY - 12 - self.rng.random() * 4, 0.35 + self.rng.random() * 0.3])
        keep = []
        for p in self.parts:
            p[1] += self.dt * 14 * p[2] * 2
            if p[1] < OY + 10: keep.append(p); extra.append([p[0], p[1], 0.3, 1.2, C['L'], 0.30 * (1 - prog * 0.6)])
        self.parts = keep
        if prog > 0.05:                                       # m4: bittersweet, then sad: the line peaks at 65 % and dims to the end
            up = min(1.0, prog / 0.65); down = 1.0 if prog < 0.65 else max(0.0, 1 - (prog - 0.65) / 0.35)
            col = C['dim'] if prog < 0.35 or prog > 0.9 else C['P']
            w = 4 + 14 * up * (0.4 + 0.6 * down)
            extra.append([OX + 7 - w / 2, OY + 10.6, w, 0.35, col, (0.25 + 0.6 * up) * (0.35 + 0.65 * down)])
        if prog < 0.45 and self.rng.random() < 0.02:          # m4: memory fragments (little frames) drift up and dissolve
            self.frames.append([OX - 1 + self.rng.random() * 14, OY + 8, (self.rng.random() - 0.5) * 0.4, -0.7 - self.rng.random() * 0.4, 1.0])
        self.frames = self._drift(self.frames, self.dt, 0, 0.22, 6)
        for p in self.frames:
            a = 0.28 * min(1.0, p[4])
            extra += [[p[0], p[1], 2.2, 0.25, C['B'], a], [p[0], p[1] + 1.95, 2.2, 0.25, C['B'], a],
                      [p[0], p[1], 0.25, 2.2, C['B'], a], [p[0] + 1.95, p[1], 0.25, 2.2, C['B'], a], [p[0] + 0.6, p[1] + 0.6, 1.0, 1.0, C['P'], a * 0.4]]
        if 0.3 < prog < 1.0:                                   # m4: someone's outline above him; gone after 85 %
            a = min(1.0, (prog - 0.3) / 0.08) * (1.0 if prog < 0.82 else max(0.0, 1 - (prog - 0.82) / 0.1))
            fl = 0.75 + 0.25 * math.sin(t * 2.3) * (0.6 if self.rng.random() < 0.97 else -1)
            if a > 0.01:
                for yy, row in enumerate(KIN):
                    for xx, ch in enumerate(row):
                        if ch == 'X': extra.append([OX + 5 + xx, OY - 9 + yy, 1, 1, C['B'], 0.16 * a * fl])
        if prog > 0.82 and len(self.parts) < 14 and self.rng.random() < 0.3:              # the rain comes back at the end
            self.parts.append([OX - 3 + self.rng.random() * 20, OY - 12 - self.rng.random() * 4, 0.35 + self.rng.random() * 0.3])
        v = s.get('vocal', 0)
        body = [[x, y, w, hh, c, (0.55 + 0.45 * v) if self.is_eye([x, y, w, hh, c, a], eye) else a] for x, y, w, hh, c, a in body]
        return body, extra, [], False

    def m_kendrick(self, body, var, s, t, eye, h, A):
        lvl = s.get('level', 0); now = t
        hard = (h['kick'] or h['punch']) and (s.get('excite', 0) > 0.5 or lvl > 0.85)
        if hard and now >= self.cut_until + 0.25:
            self.cut_until = now + 0.07
            self.jump = (self.rng.choice((-1, 1)) * 0.8, -1.0)
            if var == 'damn': self.flip = not self.flip
        if now < self.cut_until:
            ov = [('letterbox', (0.5,))] if var == 'gnx' else []
            return [], [], ov, True
        jx, jy = self.jump; self.jump = (jx * 0.85, jy * 0.85)
        jx, jy = round(jx * 5) / 5, round(jy * 5) / 5
        eyec = C['X'] if var == 'damn' else C['G']
        out = [r for r in body if not self.is_eye(r, eye)]
        out = self.recolor(out, MONO)
        if self.flip: out = [[2 * (OX + 7) - x - w, y, w, hh, c, a] for x, y, w, hh, c, a in out]
        out = self.shift(out, jx, jy)
        extra = []
        if s.get('excite', 0) > 0.55 or lvl > 0.9:
            for n, k in ((1, 'kick'), (4, 'snare'), (7, 'hat')):
                a = 0.25 + 0.75 * s.get(k, 0)
                extra += self.visor([(n, 4, eyec, a), (n + 1, 4, eyec, a), (n, 5, eyec, a), (n + 1, 5, eyec, a)])
        else:
            if h['vocal']: self.feet = (self.feet + self.rng.choice((-2, -1, 1, 2))) % 9
            c = self.feet
            extra += self.visor([(c, 4, eyec, 1.0), (c + 1, 4, eyec, 1.0), (c, 5, eyec, 1.0), (c + 1, 5, eyec, 1.0)])
        extra = self.shift(extra, jx, jy)
        ov = [('spot', (OX + 7 + jx, 0.05 + 0.10 * max(s.get('vocal', 0), lvl * 0.5), C['P'] if var == 'tpab' else C['B']))]
        if var == 'gnx': ov.append(('letterbox', (0.35 + 0.3 * lvl,)))
        if var == 'morale':
            self.hist.append((jx, jy, out)); self.hist = self.hist[-10:]
            gx, gy, gout = self.hist[0]
            extra = [[x + 3.2, y, w, hh, C['B'], 0.10] for x, y, w, hh, c, a in gout] + extra
        if var == 'gkmc':
            for _ in range(4): extra.append([OX - 2 + self.rng.random() * 18, OY + self.rng.random() * 10, 0.4, 0.4, C['B'], 0.18])
            if h['kick']: out = [[x + (0.6 if int(y) % 3 == 0 else 0), y, w, hh, c, a] for x, y, w, hh, c, a in out]
        if var == 'tpab' and h['snare']:
            for _ in range(3): self.parts.append([OX + 3 + self.rng.random() * 8, OY + 2, (self.rng.random() - 0.5) * 2, -2 - self.rng.random() * 2, 1.0])
        if self.parts:
            keep = []
            for p in self.parts:
                p[0] += p[2] * self.dt; p[1] += p[3] * self.dt; p[2] += math.sin(t * 9 + p[1]) * 0.3; p[4] -= self.dt * 0.6
                if p[4] > 0: keep.append(p); extra.append([p[0], p[1], 0.5, 0.5, C['P'], 0.6 * p[4]])
            self.parts = keep
        return out, extra, ov, False

    def m_grips(self, body, var, s, t, eye, h, A):
        """Disintegration, now by section: loud sections stack everything, rap over noise beds stays a low glitch,
        a cursed cue (song rule) turns him red and lets the Blackwall show through."""
        lvl = s.get('level', 0); sec = s.get('sec_energy', lvl)
        loud = sec > 0.62; calm = sec < 0.45; cursed = self.cursed
        scale = 1.0 if loud else 0.3 if calm else 0.65
        if cursed: scale = max(scale, 0.9)
        if (h['kick'] or h['snare'] or h['punch']) and t - self.step_t >= (0.18 if not calm else 0.4):
            self.step_t = t
            self.blast = max(self.blast, (0.4 + 0.9 * A) * (1.5 if h['punch'] else 1.0) * scale)
            big = (h['punch'] or s.get('excite', 0) > 0.8) and lvl > 0.75
            if big and t - self.cut_until >= 4.0 and not calm: self.blast = 6.0 + 4 * A; self.cut_until = t
            if loud and h['snare'] and self.rng.random() < 0.3: self.flip = not self.flip
            if loud and self.rng.random() < 0.15: self.vanish_until = t + 0.06
        if t < self.vanish_until: return [], [], [], True
        self.blast *= math.exp(-self.dt / (0.30 if self.blast > 3 else 0.07))
        b = self.blast; out = []
        for x, y, w, hh, c, a in body:
            key = (int(x), int(y))
            if key not in self.scatter:
                rnd = random.Random(hash(key) ^ int(self.seed * 1e6))
                ang = rnd.random() * 2 * math.pi; sp = 0.4 + rnd.random()
                self.scatter[key] = (math.cos(ang) * sp, math.sin(ang) * sp - 0.3)
            vx, vy = self.scatter[key]
            out.append([x + vx * b, y + vy * b + (0.08 * b * b if b > 3 else 0), w, hh, c, a * (1 - min(0.6, b / 18))])
        if self.flip: out = [[2 * (OX + 7) - x - w, y, w, hh, c, a] for x, y, w, hh, c, a in out]
        tear_p = (0.08 + 0.25 * lvl * A) * (2.0 if loud else 0.4 if calm else 1.0)
        tears = 1 + int(3 * lvl) + (2 if loud else 0)
        if self.rng.random() < tear_p:
            rows = sorted({int(r[1]) for r in out})
            for row in self.rng.sample(rows, min(len(rows), tears)):
                off = self.rng.choice((-3, -2, 2, 3)) * (0.5 + lvl)
                out = [[x + off, y, w, hh, c, a] if int(y) == row else [x, y, w, hh, c, a] for x, y, w, hh, c, a in out]
        if b > 0.8 or loud:
            out += [[x - 1.2, y, w, hh, C['X'], 0.35] for x, y, w, hh, c, a in out[::5]]
            out += [[x + 1.2, y, w, hh, C['G'], 0.25] for x, y, w, hh, c, a in out[1::7]]
        if cursed:
            out = self.recolor(out, {'#7B4DFF': '#8A1030', '#9D7BFF': '#C0284A', (eye or '').upper(): C['R']})
            if self.rng.random() < 0.08: out = [[x, y, w, hh, C['void'], a] for x, y, w, hh, c, a in out]
        elif b > 0.5 or self.rng.random() < 0.1:
            out = self.recolor(out, {(eye or '').upper(): self.rng.choice((C['X'], C['P'], C['B'], C['G']))})
        extra = []
        if calm:                                                     # noise bed: static around him
            for _ in range(6): extra.append([OX - 3 + self.rng.random() * 20, OY - 2 + self.rng.random() * 13, 0.3, 0.3, self.rng.choice((C['B'], C['dim'], C['P'])), 0.25])
        ov = []
        if b > 6 and self.rng.random() < 0.3: ov.append(('invert', ()))
        if (b > 1 or loud) and self.rng.random() < (0.5 if loud else 0.3):
            ov.append(('tear', (self.rng.uniform(-6, 2), self.rng.uniform(1, 3), self.rng.choice((C['R'], C['X'], C['V'], C['B']) if cursed else (C['X'], C['V'], C['B'])))))
        if cursed and (h['kick'] or h['punch']) and self.rng.random() < 0.5:                 # the Blackwall shows through for a frame
            ov.append(('under', self.mini_rift(t)))
        return out, extra, ov, False

    def m_epic(self, body, var, s, t, eye, h, A):
        """ЭПОС: he stands his ground. Slow sway, wind, embers rising, torch eye, stomp on the big hits, rise-and-hold at the climax."""
        lvl = s.get('level', 0); dt = self.dt
        sw = round(0.35 * math.sin(t * 0.9) * 5) / 5
        body = self.warp(body, lambda x, y: (x + sw * (1 - (y - OY) / 10), y))
        big = (h['kick'] or h['punch']) and lvl > 0.8
        if big and t - self.epic_t > 0.6:
            self.epic_t = t; self.feet_f = 'splay'; self.feet_until = t + 0.15; self.dust_at(t)
        if t - self.epic_t < 0.12: body = self.shift(body, 0, 0.4)
        if s.get('excite', 0) > 0.9 and lvl > 0.92 and self.epic_hold is None: self.epic_hold = t
        if self.epic_hold is not None:
            u = t - self.epic_hold
            if u > 2.4: self.epic_hold = None
            else:
                lift = -2.0 * min(1, u / 0.5) if u < 1.9 else -2.0 * (1 - (u - 1.9) / 0.5)
                body = self.shift(body, 0, round(lift * 5) / 5)
                for _ in range(2): self.embers.append([OX + 7 + (self.rng.random() - 0.5) * 10, OY + 9, (self.rng.random() - 0.5), -3 - self.rng.random() * 3, 1.0])
        extra = []
        if self.rng.random() < 0.12 + 0.3 * lvl:
            self.embers.append([OX - 2 + self.rng.random() * 18, OY + 10, (self.rng.random() - 0.5) * 0.8, -1.2 - self.rng.random() * 1.8, 1.0])
        keep = []
        for p in self.embers:
            p[0] += (p[2] + 0.4 * math.sin(t * 3 + p[1])) * dt; p[1] += p[3] * dt; p[4] -= dt * 0.45
            if p[4] > 0 and p[1] > OY - 14: keep.append(p); extra.append([p[0], p[1], 0.35, 0.35, C['ember'] if p[4] > 0.4 else C['P'], 0.75 * p[4]])
        self.embers = keep[-40:]
        if len(self.wind) < 5 and self.rng.random() < 0.2:
            self.wind.append([OX + 18, OY - 2 + self.rng.random() * 12, 2 + self.rng.random() * 3])
        keep = []
        for p in self.wind:
            p[0] -= dt * (14 + 10 * lvl)
            if p[0] > OX - 8: keep.append(p); extra.append([p[0], p[1], p[2], 0.15, C['B'], 0.22])
        self.wind = keep
        return body, extra + self.dust_fx(), [], False

    def m_kawaii(self, body, var, s, t, eye, h, A):
        """КАВАЙ: tiny hops on the beat, tiptoe feet, ear wiggle, ^ ^ / u u / wink faces, blush, sparkles, little hearts."""
        if h['kick'] and A > 0.3: self.start_hop(t, 0.45)
        extra = []
        if h['snare'] and t - self.heart_t > 0.8 and self.rng.random() < 0.35:
            self.heart_t = t; self.hearts.append([OX + 15 + self.rng.random() * 2, OY + 1, 1.0])
        keep = []
        for p in self.hearts:
            p[1] -= self.dt * 2.2; p[0] += math.sin(t * 4 + p[1]) * self.dt; p[2] -= self.dt * 0.6
            if p[2] > 0:
                keep.append(p)
                for yy, row in enumerate(HEART):
                    for xx, ch in enumerate(row):
                        if ch == 'X': extra.append([p[0] + xx * 0.45, p[1] + yy * 0.45, 0.45, 0.45, C['P'], 0.85 * p[2]])
        self.hearts = keep
        if self.rng.random() < 0.08: self.sparks.append([OX - 2 + self.rng.random() * 18, OY - 2 + self.rng.random() * 10, 1.0])
        keep = []
        for p in self.sparks:
            p[2] -= self.dt * 1.5
            if p[2] > 0:
                keep.append(p); a = 0.7 * p[2]
                extra += [[p[0], p[1], 0.3, 0.3, C['B'], a], [p[0] - 0.3, p[1], 0.3, 0.3, C['P'], a * 0.6], [p[0] + 0.3, p[1], 0.3, 0.3, C['P'], a * 0.6],
                          [p[0], p[1] - 0.3, 0.3, 0.3, C['P'], a * 0.6], [p[0], p[1] + 0.3, 0.3, 0.3, C['P'], a * 0.6]]
        self.sparks = keep
        return body, extra, [], False



    # ---------------------------------------------------------------- m5: ОДЕРЖИМОСТЬ
    def _poss_start(self, t, ritual, forced):
        self.poss = dict(t0=t, ritual=ritual if ritual in RITUALS else 'none', calm=0.0, out=None, t2=None, said=0, forced=forced, flash=0)
        self.shout = [(t, 'ЧТО ЭТО…'), (t + 0.9, 'НЕТ.'), (t + 1.7, 'НЕТ НЕТ НЕТ')]
        log(f'peak: ОДЕРЖИМОСТЬ ({RLABEL[self.poss["ritual"]]}{", preview" if forced else ""})')

    def _visor_clear(self, body):
        keep = (C['V'], C['L'], '#5A3FB0', '#6E5BB4', C['P'], C['D'])
        return [r for r in body if not (OY + 4 <= r[1] < OY + 6 and OX + 2 <= r[0] < OX + 12 and r[4] not in keep)]

    def _dark(self, body, a=1.0):
        """possessed palette: black body; the red outline goes UNDER it (an 'under' overlay)."""
        blk = [[x, y, w, hh, '#07060D' if c != C['D'] else '#000000', al * a] for x, y, w, hh, c, al in body]
        rim = []
        for dx, dy in ((-0.4, 0), (0.4, 0), (0, -0.4), (0, 0.4)):
            rim += [[x + dx, y + dy, w, hh, C['R'], 0.9 * a] for x, y, w, hh, c, al in body[::1]]
        return blk, rim

    def possess(self, body, extra, ov, s, t, h, eye, ctx):
        P = self.poss; u = t - P['t0']; lvl = s.get('level', 0); dt = self.dt
        T1, T2 = (0.9, 1.8) if P['forced'] else (2.5, 4.0)                    # panic / entry ends
        if P['t2'] is None and u >= T2: P['t2'] = t; log('peak: ОДЕРЖИМОСТЬ: inside him')
        if P['out'] is None and P['t2'] is not None:
            P['calm'] = P['calm'] + dt if lvl < 0.65 else 0.0
            if P['calm'] > 1.5 or t - P['t2'] > (9 if P['forced'] else 25): P['out'] = t; log('peak: ОДЕРЖИМОСТЬ: expelled')
        if P['out'] is not None and t - P['out'] > 5.2:
            self.poss = None; self.poss_gap = t + float(ctx.get('possess_gap', 60)); log('peak: ОДЕРЖИМОСТЬ: he gets up'); return body, extra, ov
        rit = P['ritual']
        k = 0.0 if u < T1 else min(1.0, (u - T1) / (T2 - T1 + 2.0))           # ritual build-up 0 → 1
        if P['out'] is not None: k = max(0.0, 1 - (t - P['out']) / 1.5)
        attach, under, rx, rov = self.ritual_layer(rit, k, s, t, h)
        under = list(under)
        # sweat drops while afraid / after
        if (u < T2 or (P['out'] is not None)) and self.rng.random() < 0.25:
            sd = self.rng.choice((-1, 1)); self.sweat.append([OX + 7 + sd * 6, OY + 1, sd * (1 + self.rng.random() * 2), -2.5, 1.0])
        keep = []
        for p in self.sweat:
            p[0] += p[2] * dt; p[1] += p[3] * dt; p[3] += 9 * dt; p[4] -= dt * 1.2
            if p[4] > 0 and p[1] < OY + 10.5: keep.append(p)
        self.sweat = keep[-20:]
        sweat = [[p[0], p[1], 0.35, 0.5, '#8FB0E8', 0.8 * p[4]] for p in self.sweat]
        body = self._visor_clear(body); extra = self._visor_clear(extra)            # the mode's own eye / slit goes too
        e = eye or C['G']
        # ---- 1 panic
        if u < T1:
            trem = round((self.rng.random() - 0.5) * 0.9 * 5) / 5
            back = -round(min(1.6, u * 0.8) * 5) / 5
            dart = 2 if int(t * 9) % 2 else -2
            body = self.shift(body + attach, trem + back, 0)
            eyes = self.shift(self.visor([(4 + dart, 4, C['B'], 1.0), (5 + dart, 4, C['B'], 1.0), (4 + dart, 5, e, 1.0), (5 + dart, 5, e, 1.0)]), trem + back, 0)
            self.fold_until = t + 0.12
            return body + eyes, extra + sweat + rx, ov + rov + [('under', under)]
        # ---- 2 entry: the ghost in the machine crawls in
        if u < T2:
            v = (u - T1) / (T2 - T1)
            gl = [(OX + self.rng.random() * 14, OY - 1 + self.rng.random() * 10, self.rng.choice(GLYPHS), 0.5 + 0.5 * self.rng.random(), C['R'])
                  for _ in range(int(4 + 22 * v))]
            rows = sorted({int(r[1]) for r in body})
            for row in self.rng.sample(rows, min(len(rows), 1 + int(3 * v))):
                off = self.rng.choice((-2, -1, 1, 2))
                body = [[x + off, y, w, hh, c, a] if int(y) == row else [x, y, w, hh, c, a] for x, y, w, hh, c, a in body]
            trem = round((self.rng.random() - 0.5) * 1.2 * 5) / 5; body = self.shift(body, trem, 0)
            if self.rng.random() < 0.25 + 0.6 * v or h['kick'] or h['snare']:
                blk, rim = self._dark(body); body = blk; under += rim
                eyes = self.visor([(4, 4, C['R'], 1.0), (4, 5, C['R'], 1.0)])
            else:
                eyes = self.visor([(4, 4, C['B'], 1.0), (5, 4, C['B'], 1.0), (4, 5, C['B'], 1.0), (5, 5, C['B'], 1.0)])
            if self.rng.random() < 0.3: ov = ov + [('tear', (self.rng.uniform(-6, 3), self.rng.uniform(1, 3), C['R']))]
            return body + attach + eyes, extra + sweat + rx, ov + rov + [('under', under), ('glyphs', gl)]
        # ---- 4/5 expelled → collapse → gets up
        if P['out'] is not None:
            w_ = t - P['out']
            if w_ < 1.2:
                if w_ < 0.1: ov = ov + [('flash', (C['R'], 0.45))]
                ghost, rim = self._dark(self.shift(body, 0, -w_ * 14), max(0.0, 1 - w_ / 1.2))
                ghost = [[x + (y - OY) * 0.0, y - (OY + 10 - y) * w_ * 0.8, wd, hh * (1 + w_), c, a] for x, y, wd, hh, c, a in ghost]
                trem = round((self.rng.random() - 0.5) * 1.4 * 5) / 5
                return self.shift(body, trem, 0) + ghost, extra + sweat, ov + [('under', under + [r[:5] + [r[5] * 0.5] for r in rim])]
            v = w_ - 1.2                                                            # 0 … 4
            flat = 0.5 if v < 3.4 else 0.5 + 0.5 * (v - 3.4) / 0.6
            pant = -0.2 if int(t * 2.2) % 2 and v < 3.4 else 0.0
            body = self.warp(body, lambda x, y: (x, OY + 10 - (OY + 10 - y) * flat + pant))
            dim = 0.35 + 0.4 * (int(t * 5) % 2) if v < 2.5 else 0.9
            eyes = self.warp(self.visor([(4, 5, e, dim), (5, 5, e, dim)]), lambda x, y: (x, OY + 10 - (OY + 10 - y) * flat + pant))
            return body + eyes, extra + sweat, ov + [('under', under)]
        # ---- 3 possessed
        lift = -2.0 - 0.3 * math.sin(t * 2.1); lift = round(lift * 5) / 5
        if h['snare'] or h['kick'] or (h['punch']):
            self.jerk = (self.rng.choice((-2, -1, 1, 2)), t)
        jx = self.jerk[0] if t - self.jerk[1] < 0.12 else 0
        horns = []
        for r in body:
            if row_of(r) == 0 and 0.98 <= r[2] <= 1.02:
                out_ = -1 if col_of(r) <= 6 else 1
                horns += [[r[0] + out_ * 0.5, r[1] - 1, 1, 1, r[4], r[5]], [r[0] + out_, r[1] - 2, 1, 1, r[4], r[5]]]
        body = body + horns
        hw = lambda x, y: (x + (jx if y < OY + 5 else 0) + (0.6 * jx if y < OY + 1 else 0), y + lift + (0.8 if y >= OY + 8 else 0))
        body = self.warp(body, hw); attach = self.warp(attach, hw)
        if self.rng.random() < 0.06: body = [[x + self.rng.choice((-1, 1)), y, w, hh, c, a] if self.rng.random() < 0.3 else [x, y, w, hh, c, a] for x, y, w, hh, c, a in body]
        blk, rim = self._dark(body)
        eyes = self.shift(self.visor([(4, 4, C['R'], 1.0), (4, 5, C['R'], 1.0), (2, 4, C['R'], 0.6), (7, 5, C['R'], 0.6), (6, 4, C['R'], 0.45)]),
                          jx, lift)
        if self.rng.random() < 0.15:
            jaw = self.shift(self.visor([(n, 5, C['B'], 0.9) for n in range(2, 9, 2)]), jx, lift); eyes += jaw
        if t - P['said'] > 3.2 and (h['snare'] or h['kick']):
            P['said'] = t; self.shout = [(t, self.rng.choice(POSSESSED_LINES))]
        ghost = [[x + self.rng.uniform(-1, 1), y, w, hh, C['R'], 0.18] for x, y, w, hh, c, a in blk[::5]] if self.rng.random() < 0.5 else []
        gl = [(OX - 2 + self.rng.random() * 18, OY - 6 + self.rng.random() * 14, self.rng.choice(GLYPHS), 0.25 + 0.4 * self.rng.random(), C['R'])
              for _ in range(6 if rit == 'none' else 3)]
        if h['kick'] and self.rng.random() < 0.5: ov = ov + [('edge', (C['R'], 0.6))]
        return blk + attach + eyes + ghost, extra + rx, ov + rov + [('under', under + rim), ('glyphs', gl)]

