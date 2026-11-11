

class LastStand:
    """Phases: fight (black sun rises, the horde comes in on the hits, he cuts them down on the kicks) → climax (sky red, sun
    full, the horde turns to ash, blade planted, breath steaming, «…ЕЩЁ ДЫШУ.») → after (cape + blade + scratches, rest of the song)."""
    def __init__(self, now, preview=False, horde=True):
        self.t0 = now; self.preview = preview; self.horde = horde; self.rng = random.Random()
        self.phase = 'fight'; self.climax_t = None; self.foes = []; self.kills = 0; self.spray = []; self.ash = []
        self.slash = None; self.prev = dict(kick=0, snare=0, hat=0); self.last_spawn = now; self.last_cut = now; self.said = now
        self.line = None; self.scratches = []; self.steam = []; self.wind = 0.0
        log(f'peak: ПОСЛЕДНИЙ РУБЕЖ ({"preview" if preview else "the song rises"}{", horde" if horde else ""})')

    def done_fighting(self): return self.phase == 'after'

    def tally(self): return 100 if self.phase != 'fight' else min(99, self.kills * 5)

    def tick(self, now, sn):
        sn = sn or {}
        hits = {k: (sn.get(k, 0) or 0) >= 0.5 and (sn.get(k, 0) or 0) > self.prev[k] + 0.2 for k in self.prev}
        self.prev = {k: sn.get(k, 0) or 0 for k in self.prev}
        lvl = sn.get('level', 0) or 0; el = now - self.t0
        if self.preview:                                                   # no ear: a beat every 0.45 s
            b = int(el / 0.45) != int((el - 0.1) / 0.45); hits = dict(kick=b, snare=False, hat=b); lvl = 0.85
        self.wind = 2 + 1.5 * math.sin(now * 2.3) + (1.5 if hits['kick'] else 0)
        if self.phase == 'fight':
            if self.horde:
                alive = [f for f in self.foes if f['die'] is None]
                if (hits['kick'] or hits['snare'] or hits['hat']) and lvl > 0.55 and len(alive) < 6 and now - self.last_spawn > 0.5:
                    self.last_spawn = now; side = 1                         # his left is the edge of the screen: they come from the right
                    self.foes.append(dict(x=-10.0 if side < 0 else self.rng.uniform(44, 64), side=side, die=None, wait=None,
                                          spear=self.rng.random() < 0.4, sp=self.rng.uniform(5, 9)))
                for f in alive:                                            # they close in, step by step on the beat
                    tx = OX - 9.5 if f['side'] < 0 else OX + 15.5
                    if (f['side'] < 0 and f['x'] < tx) or (f['side'] > 0 and f['x'] > tx):
                        if hits['hat'] or hits['kick'] or self.preview: f['x'] += -f['side'] * f['sp'] * 0.12 * (3 if not self.preview else 1)
                        f['x'] = min(f['x'], tx) if f['side'] < 0 else max(f['x'], tx)
                    elif f['wait'] is None: f['wait'] = now
                near = [f for f in alive if f['wait'] is not None]
                if near and hits['kick'] and now - self.last_cut > 0.3:  # he cuts them down on the kick
                    side = near[0]['side']; self.last_cut = now; self.slash = (now, side)
                    for f in near:
                        if f['side'] != side: continue
                        f['die'] = now; self.kills += 1
                        for _ in range(14): self.spray.append([OX + 7 + side * 9, OY + 4, side * self.rng.uniform(4, 14), -self.rng.uniform(3, 12), now])
                    if now - self.said > 6 and self.rng.random() < 0.4: self.said = now; self.line = (self.rng.choice(STAND_LINES), now + 1.0)
                for f in near:                                             # one that waits too long draws blood
                    if f['die'] is None and now - f['wait'] > 2.5:
                        f['wait'] = now; self.scratches.append((self.rng.randint(2, 11), self.rng.randint(1, 7), now))
                self.foes = [f for f in self.foes if f['die'] is None or now - f['die'] < 0.9]
            elif hits['kick'] and now - self.last_cut > 1.2 and self.rng.random() < 0.4:
                self.last_cut = now; self.slash = (now, self.rng.choice((-1, 1)))
            big = (0 <= now - (sn.get('drop_t', -99) or -99) < 0.5) or (sn.get('max_hold', 0) or 0) > 1.0 or ((sn.get('excite', 0) or 0) > 0.95 and lvl > 0.85)
            if (el > 20 and big) or el > 70 or (self.preview and el > 16) or (self.horde and self.kills >= 20 and big):
                self.phase = 'climax'; self.climax_t = now; self.line = ('…ЕЩЁ ДЫШУ.', now + 3.0)
                for f in self.foes:
                    if f['die'] is None: f['die'] = now
                log('peak: ПОСЛЕДНИЙ РУБЕЖ: he is still breathing')
        elif self.phase == 'climax' and now - self.climax_t > 3.6:
            self.phase = 'after'
        if self.phase != 'fight' and self.rng.random() < 0.08:            # breath steam
            self.steam.append([OX + 7 + self.rng.uniform(-1, 1), OY + 4.5, now])
        self.steam = [s for s in self.steam if now - s[2] < 1.6][-20:]
        self.spray = [p for p in self.spray if now - p[4] < 0.9][-120:]

    # ---- drawing helpers
    def _blade(self, out, bx, by, ang, length=17, hl=1.0):
        """a crude iron slab, chipped, bone edge; (bx, by) = grip, ang = radians (0 = up, + = clockwise)."""
        dx, dy = math.sin(ang), -math.cos(ang); px_, py_ = math.cos(ang), math.sin(ang)
        for k in range(int(length * 2)):
            u = k / 2
            for w in (-1.0, -0.5, 0.0, 0.5, 1.0):
                if k < 4 and abs(w) > 0.5: continue                      # the grip
                if k > 6 and ((k * 7 + int(w * 2)) % 13 == 0) and abs(w) == 1.0: continue   # chips in the edge
                col = IRON_D if k < 4 else (BLADE_L if w == 1.0 else BLADE)
                out.append([bx + dx * u + px_ * w, by + dy * u + py_ * w, 0.6, 0.6, col, 1.0 * hl])
        out.append([bx - px_ * 1.6, by - py_ * 1.6, 3.2 * abs(px_) + 0.6, 3.2 * abs(py_) + 0.6, IRON_D, 1.0])   # guard

    def attach(self, rects, ov, now, armed=True):
        """cape behind him, iron palette + hatching, blade, scratches, steam: used in all phases (after: on top of his dance)."""
        body = [r for r in rects if 0.9 <= r[2] <= 1.1 and r[5] >= 0.6]
        if not body: return rects, ov
        xs = [r[0] for r in body]; ys = [r[1] for r in body]; bx0, by0, bx1, by1 = min(xs), min(ys), max(xs) + 1, max(ys) + 1
        under = []
        torn = self.phase != 'fight'
        for k in range(18):                                                 # the cape: a fan from his shoulders, blown up and back
            v = k / 17; ang = math.radians(8 + 62 * v) + 0.12 * math.sin(now * 4 + k * 0.7) * (self.wind / 3)
            L = (7 + 5 * math.sin(v * math.pi)) * (0.8 + 0.15 * self.wind)
            ax = bx0 + 2 + v * 3; ay = by0 + 2.5 - v * 1.5
            for j in range(int(L * 2)):
                u = j / (L * 2); wav = 0.5 * math.sin(now * 7 - j * 0.6 + k) * u
                x = ax + math.cos(ang) * j * 0.5 + wav * 0.3; y = ay - math.sin(ang) * j * 0.5 + wav
                if torn and ((k * 5 + j) % 6 == 0) and j > 4: continue
                if u > 0.82 and (k * 3 + j) % 3 == 0: continue                  # ragged end
                under.append([x, y, 0.7, 0.7, CAPE_R if (k in (0, 17) or u > 0.93) else CAPE, 0.97])
        def recol(x, y, c):
            cu = c.upper()
            if cu in ('#8FD9A8', '#E4E0EA') and OY + 4 <= y < OY + 6 and OX + 2 <= x < OX + 12: return RED      # the eye burns red
            if cu in ('#07060D', '#000000'): return c
            return IRON_L if cu in ('#9D7BFF', '#E4E0EA') else IRON
        rects = [[x, y, w, h, recol(x, y, c), a] for x, y, w, h, c, a in rects]
        extra = []
        for cx, cy in [(r[0], r[1]) for r in body if (int(r[0]) + int(r[1])) % 2 == 0]:   # ink hatching
            extra.append([cx + 0.15, cy + 0.6, 0.35, 0.15, IRON_D, 0.9]); extra.append([cx + 0.5, cy + 0.25, 0.35, 0.15, IRON_D, 0.9])
        for (sx, sy, t) in self.scratches[-8:]:
            extra += [[bx0 + sx, by0 + sy, 0.5, 0.25, RED, 0.9], [bx0 + sx + 0.5, by0 + sy + 0.3, 0.5, 0.25, RED, 0.8]]
        if armed:
            if self.slash and now - self.slash[0] < 0.18:                  # swing
                u = (now - self.slash[0]) / 0.18; side = self.slash[1]
                ang = side * (-0.3 + u * 2.4); self._blade(extra, bx1 - 1 if side > 0 else bx0 + 1, by0 + 5, ang)
                ov = ov + [('paint', ('slash', side, u))]
            elif self.phase == 'climax':
                self._blade(extra, bx1 + 1.5, by1 - 16, 3.14159, 16)                  # planted in the ground, point down
            else:
                self._blade(extra, bx1 - 0.5, by0 + 6, 0.55 if self.phase == 'fight' else 0.35)     # on the shoulder
        for s in self.steam:
            u = now - s[2]; extra.append([s[0] + u * 0.8, s[1] - u * 3, 0.5, 0.5, BONE, 0.6 * (1 - u / 1.6)])
        return rects + extra, [('under', under)] + ov

    def frame(self, rects, ov, now, sn):
        """fight / climax: the scene replaces his dance. Returns (rects, ov)."""
        el = now - self.t0
        bob = 0.2 * math.sin(now * 3) if self.phase == 'fight' else (-0.3 * (1 + math.sin(now * 1.6)) / 2)
        lean = 0.0
        if self.slash and now - self.slash[0] < 0.25: lean = self.slash[1] * 0.8
        rects = [[x + lean, y + bob, w, h, c, a] for x, y, w, h, c, a in rects]
        rects, ov = self.attach(rects, ov, now, armed=True)
        extra = []
        for f in self.foes:                                                 # the horde: black, red eyes, some with spears
            fx = f['x']; d = f['die']
            for yy, row in enumerate(FOE):
                for xx, ch in enumerate(row):
                    if ch == '.': continue
                    x, y = fx + xx, OY + yy
                    if d is not None:
                        u = now - d; x += ((xx - 4) * 0.4 + f['side'] * -1) * u * 3; y -= (yy % 3) * u * 2 - u * u * 6
                        a = max(0.0, 1 - u / 0.9); col = ASH if ch == 'X' else RED
                    else:
                        a = 1.0; col = RED if ch == 'R' else '#050407'
                    extra.append([x, y + (0.3 if d is None and int(now * 4 + fx) % 2 else 0), 1, 1, col, a])
            if f['spear'] and d is None:
                for k in range(10): extra.append([fx + (8 if f['side'] < 0 else 0) + k * 0.5 * -f['side'] * -1, OY + 3 - k * 0.3, 0.5, 0.5, BLADE, 1.0])
        for p in self.spray:
            u = now - p[4]; extra.append([p[0] + p[2] * u, p[1] + p[3] * u + 14 * u * u, 0.5, 0.5, RED, 1 - u / 0.9])
        ov = [('paint', ('sky', self.phase, el, now - (self.climax_t or now)))] + ov
        if self.horde: ov = ov + [('paint', ('tally', self.tally()))]
        if self.line and now < self.line[1]: ov = ov + [('shout', (self.line[0], clamp((self.line[1] - now) / 0.4)))]
        return rects + extra, ov

    def after(self, rects, ov, now):
        rects, ov = self.attach(rects, ov, now, armed=True)
        if self.line and now < self.line[1]: ov = ov + [('shout', (self.line[0], clamp((self.line[1] - now) / 0.4)))]
        return rects, ov


def paint_stand(cr, arg, U, oy, SW, WH):
    """window-space painting for ПОСЛЕДНИЙ РУБЕЖ ('paint' overlays): the red sky + black sun, the slash arc, the tally."""
    kind = arg[0]
    cx, gy = (OX + 7) * U, oy + (OY + 10) * U
    if kind == 'sky':
        _, phase, el, cel = arg
        k = clamp(el / 14) if phase == 'fight' else 1.0
        R = 30 * U
        g = cairo.RadialGradient(cx + 4 * U, gy - 14 * U, 0, cx + 4 * U, gy - 14 * U, R)
        g.add_color_stop_rgba(0, 0.48, 0.03, 0.08, (0.35 + 0.45 * k) * (1.0 if phase != 'climax' else 1.25)); g.add_color_stop_rgba(0.55, 0.18, 0.0, 0.04, 0.45 * k)
        g.add_color_stop_rgba(1, 0.0, 0.0, 0.0, 0)
        cr.set_source(g); cr.arc(cx + 4 * U, gy - 14 * U, R, 0, 2 * math.pi); cr.fill()
        sx = cx + 9 * U; sy = gy - (10 + 18 * k) * U; r = (2.4 + 1.6 * k + (0.8 if phase == 'climax' else 0)) * U
        glow = cairo.RadialGradient(sx, sy, r, sx, sy, r * 3.2)
        glow.add_color_stop_rgba(0, 1.0, 0.13, 0.27, 0.75 if phase == 'climax' else 0.45 * k + 0.1); glow.add_color_stop_rgba(1, 1.0, 0.13, 0.27, 0)
        cr.set_source(glow); cr.arc(sx, sy, r * 3.2, 0, 2 * math.pi); cr.fill()
        cr.set_source_rgba(1.0, 0.25, 0.3, 0.95); cr.arc(sx, sy, r + 1.5, 0, 2 * math.pi); cr.fill()
        cr.set_source_rgba(0.0, 0.0, 0.0, 1.0); cr.arc(sx, sy, r, 0, 2 * math.pi); cr.fill()
        cr.set_source_rgba(0.04, 0.02, 0.05, 0.9); cr.rectangle(0, gy, (OX + 60) * U, max(2, U * 0.6)); cr.fill()   # the ground line
    elif kind == 'slash':
        _, side, u = arg
        cr.save(); cr.translate(cx, oy + (OY + 5) * U)
        a0, a1 = (-2.2, 0.6) if side > 0 else (math.pi - 0.6, math.pi + 2.2)
        cr.arc(0, 0, 11 * U, a0, a0 + (a1 - a0) * u)
        cr.set_source_rgba(0.89, 0.88, 0.92, 0.9 * (1 - u * 0.6)); cr.set_line_width(max(2, U * 0.8)); cr.stroke(); cr.restore()
    elif kind == 'tally':
        _text(cr, f'{arg[1]:02d} / 100', cx + 26 * U, oy + (OY - 26) * U, max(10, int(2.2 * U)), RED, 0.85)


EVENTS = dict(descend=Strike, hand=HandGrab, shadow=Shadow, descend_hand=DescendHand, stand_gold=Stand)     # h5: the gold stand archived     # h3: hand / shadow / descend_hand archived (previews only)
