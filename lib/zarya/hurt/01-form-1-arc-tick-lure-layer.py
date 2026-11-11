class _Form1:     # mixin of Form (v35 split; one class in the original)

    def _arc_tick(self, now, sn, ctx, pos, music, lvl):
        a = self.arc
        if a is not None and not music and not a.get('pv') and a['ph'] in ('smell', 'wind', 'soul'): self.arc = a = None
        if a is None:
            if not music or self.det_max <= 0 and not self.hard: return
            if self.hard and not self.drop_only and not self.smelled and (pos or 0) > 3 and (lvl > 0.5 or self.dg):
                self.smelled = True; self.arc = dict(ph='smell', t=now, frozen=None); self._scatter(now); log(f'hurt: {FORM_NAME} ЧУЕТ'); return
            if self.dets >= self.det_max or now - self.det_t < (25 if self.steroids else 30): return
            lead = 7.0 if self.dg else 4.0
            if self.hard and not self.smelled and self.targets and any(0 < t - (pos or 0) <= lead + 1.5 for t in self.targets):
                self.smelled = True; self.arc = dict(ph='smell', t=now, frozen=None); self._scatter(now); log(f'hurt: {FORM_NAME} ЧУЕТ'); return
            if self.targets:
                if (pos or 0) > 0 and now < self.live_cd: return
                nxt = next((t for t in self.targets if t > (pos or 0) - 0.1 and t not in self.done_t), None)
                if nxt is not None and pos is not None and 0 < nxt - pos <= lead:
                    self.arc = dict(ph='wind', t=now, at=nxt, lead=nxt - pos if nxt - pos < lead else lead, power=self._power(ctx, nxt), k=0.0)
                    log(f'hurt: {FORM_NAME} ЗАВОД (drop at {nxt:.1f}s)')
            elif ctx is None or self.targets == []:                              # h8: no map: build -> gap -> slam, live
                if lvl < 0.78: self.loud_run = now
                if (pos or 0) < 25 or now < self.live_cd: return                    # h11: no live blast on the intro (was 8 s)
                b = self._building(now); flat = self.hard and now - self.loud_run > 2.0
                if b or flat:
                    self.smelled = True
                    self.arc = dict(ph='wind', t=now, at=None, live=True, lead=8.0, power=None, k=0.0, mx=lvl, b_t=now if b else -9, low=None, flat=not b)
                    log(f'hurt: {FORM_NAME} ЗАВОД (live: {"the build" if b else "it stays loud"})')
            return
        ph = a['ph']; el = now - a['t']
        if ph == 'smell':
            if el > 1.5: self.arc = None
        elif ph == 'wind' and a.get('live'):                                   # h8
            prev_mx = a['mx']; a['mx'] = max(a['mx'], lvl); a['k'] = clamp(el / 8.0)
            if self._building(now): a['b_t'] = now; a['flat'] = False
            lows = [l for t, l in self.lv if now - t < 2.0] or [0]
            if self._gap(now, a, lvl):
                a.update(ph='soul', t=now, gap_lvl=lvl); log(f'hurt: {FORM_NAME} ДУША ВОН (the gap)')
            elif self._jump(now, lvl) and (a.get('flat') or lvl >= 1.05 * prev_mx):
                log(f'hurt: {FORM_NAME} the drop came without a gap'); self._boom(now, a, lvl)
            elif self.hard and now - a['b_t'] > 3.0 and el > 3.0 and self.kick_now and lvl >= 0.85 and min(lows) >= 0.75:
                self._boom(now, a, lvl)                                             # flat loud, no build: a big kick
            elif el > 24 or (not a.get('flat') and now - a['b_t'] > 8.0):
                self.arc = None; self.live_cd = now + 8; log(f'hurt: {FORM_NAME} false alarm (no drop)')
        elif ph == 'soul' and a.get('live'):
            if self.kick_now and lvl >= max(0.6, 1.15 * a.get('gap_lvl', 0)): self._boom(now, a, lvl)
            elif el > 3.0: self.arc = None; self.live_cd = now + 8; log(f'hurt: {FORM_NAME} the soul came back (no slam)')
        elif ph == 'wind':
            left = (a['at'] - pos) if a['at'] is not None and pos is not None else a['lead'] - el
            a['k'] = clamp(1 - (left - 0.6) / max(0.1, a['lead'] - 0.6))
            if a['at'] is not None and pos is not None and pos < a['at'] - a['lead'] - 3: self.arc = None; return     # seek back
            if left <= 0.6: a.update(ph='soul', t=now); log(f'hurt: {FORM_NAME} ДУША ВОН')
        elif ph == 'soul':
            left = (a['at'] - pos) if a['at'] is not None and pos is not None else 0.6 - el
            if a['at'] is None: hit_ = left <= 0 or el > 1.4                     # menu preview
            else: hit_ = (-0.4 < left <= 0.45 and self.kick_now and lvl >= 0.7) or left <= -0.4 or el > 2.2   # h8: on the real kick
            if hit_: self._boom(now, a, lvl)
        elif ph == 'boom':
            if el > 1.1: a.update(ph='build', t=now, back=[], plan=self._plan(ctx, a), slam=None, order=self.rng.sample(a['chunks'], len(a['chunks'])))
        elif ph == 'build':
            if a['slam'] is None:
                n = len(a['back'])
                due = el >= a['plan'][n] if a['plan'] and n < len(a['plan']) else (self._hits['kick'] or self._hits['snare'] or el > 0.7 * (n + 1))
                if due and n < len(a['order']): a['back'].append(a['order'][n])
                if len(a['back']) >= len(a['order']) or el > 3.5: a['slam'] = now
            elif now - a['slam'] > 0.4:
                self._done(now, a)

    def _plan(self, ctx, a):
        """the chunks snap back on the drop's own hits (from the map), else on the live kicks (None)."""
        hs = (ctx or {}).get('last_hits') if a.get('at') is not None else None
        if not hs: return None
        ts = sorted(t - 1.1 for t, _ in hs if t > 1.15)
        if not ts: return None
        while len(ts) < len(a['chunks']): ts.append(ts[-1] + ((ts[-1] - ts[-2]) if len(ts) > 1 else 0.4))
        return ts

    def _boom(self, now, a, lvl):
        p = a.get('power')
        size = 'horns' if p is not None and p < 1.8 else 'god' if (p is not None and p >= 2.6) else 'full'
        blk, extra, eyes, rim = self._parts
        cells = [c for c in blk if c[1] < OY] if size == 'horns' else blk
        r = self.rng; sp = 1.5 if size == 'god' else 1.0; seen = set()
        self.shards = []; a['mid'] = self._mid(blk)
        for x, y, w, h, c, al in cells:
            k_ = (round(x * 5), round(y * 5))
            if al < 0.5 or k_ in seen: continue
            seen.add(k_); q = self._q((x, y), a['mid'], size == 'horns'); side = 1 if q % 2 else -1
            self.shards.append([x, y, w, h, c, al, side * r.uniform(5, 14) * sp + r.uniform(-2, 2), -r.uniform(8, 22) * sp, now, q, x, y])
        score = p if p is not None else 2.0 + lvl
        rec = float(self.mem.d.get('record', 0) or 0)
        if score > rec + 0.01:
            self.mem.d['record'] = round(score, 2); self.mem.save(); a['record'] = rec > 0
            if rec > 0: log(f'hurt: {FORM_NAME} РЕКОРД ({score:.2f} > {rec:.2f})')
        a.update(ph='boom', t=now, size=size, chunks=[0, 1] if size == 'horns' else [0, 1, 2, 3])
        self.line = None; self._scatter(now)
        log(f'hurt: {FORM_NAME} ДЕТОНАЦИЯ ({size}{f", power {p:.2f}" if p is not None else ""})')

    def _done(self, now, a):
        self.arc = None; self.shards = []
        if not a.get('pv'):
            self.dets += 1; self.det_t = now
            if a.get('at') is not None: self.done_t.add(a['at'])
            st = self.state()
            if st: st['hunger'] = round(min(1.0, float(st.get('hunger', 0.5)) + 0.08), 2); self.mem.save()
        log(f'hurt: {FORM_NAME} СБОРКА: it put itself back together ({self.dets}/{self.det_max})')

    def _scatter(self, now):
        self.gone = [(x, y, self.rng.choice((-1, 1)) * self.rng.uniform(8, 16), -self.rng.uniform(2, 8), now) for x, y, _ in self.flies]
        self.flies = []; self.fly_t = now

    def _shard_tick(self, now):
        out = []
        for s in self.shards:
            dt = min(0.1, now - s[8]); s[8] = now
            s[7] += 38 * dt; s[0] += s[6] * dt; s[1] += s[7] * dt
            if s[0] < 0: s[0] = 0; s[6] = -0.5 * s[6]
            if s[0] > PW - s[2]: s[0] = PW - s[2]; s[6] = -0.5 * s[6]
            if s[1] > OY + 10 - s[3]: s[1] = OY + 10 - s[3]; s[7] = -0.3 * s[7]; s[6] *= 0.7
            if s[1] < OY - 10: s[1] = OY - 10; s[7] = abs(s[7]) * 0.4
            out.append([round(s[0] * 5) / 5, round(s[1] * 5) / 5, s[2], s[3], s[4], s[5]])
        return out

    @staticmethod
    def _mid(cells):
        xs = sorted(c[0] for c in cells) or [OX + 6.5]; ys = sorted(c[1] for c in cells) or [OY + 4.5]
        return xs[len(xs) // 2] + 0.5, ys[len(ys) // 2] + 0.5

    @staticmethod
    def _q(c, mid, horns):
        return (1 if c[0] >= mid[0] else 0) + (0 if horns else 2 if c[1] >= mid[1] else 0)

    @staticmethod
    def _outline(cells):
        occ = {(int(round(x)), int(round(y))) for x, y, w, h, c, a in cells if w >= 0.9 and h >= 0.9}
        return sorted({(x + dx, y + dy) for x, y in occ for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - occ)

    def _word(self, lyr):
        ws = [w for w in re.split(r'[^\w$\']+', lyr or '') if w]
        if ws:
            w = ws[self.wi % len(ws)]; self.wi += 1
            return ''.join(LOOK.get(c, c) for c in w.upper())
        return self.rng.choice(KRIK_WORDS)

    def _flies(self, now, music):
        hg = self.hunger(); out = []
        if hg < 0.35 and self.arc is None and now - self.fly_t > 10:
            want = 3 + int((0.35 - hg) * 10)
            while len(self.flies) < want: self.flies.append([OX + self.rng.randint(0, 13), OY + self.rng.randint(-3, 8), 0])
        elif hg >= 0.35: self.flies = []
        for f in self.flies:
            if now >= f[2]:
                f[0] = clamp(f[0] + self.rng.choice((-1, 0, 1)), OX - 3, OX + 16); f[1] = clamp(f[1] + self.rng.choice((-1, 0, 1)), OY - 4, OY + 9)
                f[2] = now + self.rng.uniform(0.06, 0.2) * (0.6 if music else 1.0)
            out.append([f[0], f[1], 0.6, 0.6, FLY, 0.9])
        self.gone = [g for g in self.gone if now - g[4] < 0.8]
        for x, y, vx, vy, t0 in self.gone:
            u = now - t0; out.append([round(x + vx * u), round(y + vy * u), 0.6, 0.6, FLY, 0.9 * (1 - u / 0.8)])
        return out

    # ================================================================ h9: ПРИМАНКА
    def _lure_on(self, now): return getattr(self, 'lure', False) or now < getattr(self, 'lure_pv', 0)

    def lure_preview(self, now):
        """right-click > ▶ ПРИМАНКА: 14 s of mask, cracks, strings and two faces, with or without music."""
        self.lure_pv = now + 14; self.cracks = 0; self.face = None; self.mask_off = False; log(f'hurt: {FORM_NAME} ПРИМАНКА preview')

    def _cute(self, now, ctx, lvl, music):
        if now < getattr(self, 'lure_pv', 0) and not self.lure: return int(now / 3) % 2 == 0
        if ctx and ctx.get('aggr') is not None: return ctx['aggr'] < 0.5 and (ctx.get('voice') is None or ctx['voice'] >= 0.4)
        return (lvl < 0.7) if music else True

    def _lure_layer(self, now, ctx, lvl, music, blk, extra, eyes, rim):
        pv = now < getattr(self, 'lure_pv', 0) and not self.lure
        cute = self._cute(now, ctx, lvl, music)
        if self.face is not None and cute != self.face:                                   # ДВА ЛИЦА: no transition
            self.face_t = now
            if not cute: self.cracks = min(6, self.cracks + 1)                             # ТРЕЩИНА: every dark turn
            if cute: self.mask_off = False
            log(f'hurt: {FORM_NAME} ДВА ЛИЦА ({"mask" if cute else "slit"}, cracks {self.cracks})')
        self.face = cute
        kick = self.kick_now or (pv and int(now * 7) % 5 == 0 and not cute)
        dark_hit = kick and (lvl >= 0.8 or pv) and not cute
        # КУКЛА: breakcore chops snap it on strings
        chops = len([t for t in self.rs + getattr(self, 'rh', []) if now - t < 1.0]) + (8 if pv and not cute else 0)
        if chops >= 6:
            if (self.kick_now or self._hits.get('snare') or self._hits.get('hat') or (pv and int(now * 8) % 2 == 0)) and now - self.pose_t > 0.12:
                self.pose_t = now; self.pose = self.rng.choice([(-1, 0), (1, -1), (0, 1), (-2, -1), (2, 0), (0, -1)])
            dx, dy = self.pose
            blk, extra, eyes, rim = [[[x + dx, y + dy, w, h, c, al] for x, y, w, h, c, al in p] for p in (blk, extra, eyes, rim)]
            jerk = 0.6 if now - self.pose_t < 0.05 else 0.0
            for ax, ay in ((OX + 0.4, OY + 5), (OX + 6.4, OY - 3), (OX + 13.4, OY + 5)):
                top = OY - 10; extra.append([ax + dx, top, 0.2, ay + dy - top - jerk, SWEET, 0.65])
        elif self.pose != (0, 0) and now - self.pose_t > 0.5: self.pose = (0, 0)
        # МАСКА (+ ТРЕЩИНА, ДВА ЛИЦА)
        flick = dark_hit and cute is False
        show = cute and not self.mask_off and not (self.kick_now and lvl >= 0.85)
        mid = self._mid(blk); ox_, oy_ = round(mid[0] - (OX + 6.5)), round(mid[1] - (OY + 4.5))
        two = now - self.face_t < 0.08
        if show or two:
            half = (lambda x: x < 7) if two else (lambda x: True)
            mk = []
            for x0, y0, w, h in MASK_EYES:
                if half(x0): mk += [[OX + x0 + ox_ + i, OY + y0 + oy_ + j, 1, 1, BONE, 1.0] for i in range(w) for j in range(h)]
            mk += [[OX + x + ox_, OY + y + oy_, 1, 1, INK, 1.0] for x, y in MASK_PUPILS if half(x)]
            mk += [[OX + x + ox_, OY + y + oy_, 1, 1, BLUSH, 0.95] for x, y in MASK_SMILE if half(x)]
            mk += [[OX + 2 + ox_, OY + 6 + oy_, 1, 1, BLUSH, 0.45]]
            r_ = random.Random(self.song_key or 'pv')
            for crk in r_.sample(CRACKS, min(len(CRACKS), self.cracks)):
                mk += [[OX + x + ox_, OY + y + oy_, 1, 1, INK, 0.95] for x, y in crk if half(x)]
                ex_ = crk[-1]; mk.append([OX + ex_[0] + ox_ + 0.3, OY + ex_[1] + oy_ + 0.3, 0.4, 0.4, RED, 0.9])
            if two: mk += [[OX + 9 + ox_, OY + 4 + oy_, 1, 2, RED, 1.0], [OX + 10.4 + ox_, OY + 4.6 + oy_, 0.6, 0.6, RED, 0.5]]   # the other face
            eyes = mk
        return blk, extra, eyes, rim, flick or dark_hit

