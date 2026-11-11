class _Dance3:     # mixin of Dance (v35 split; one class in the original)

    def _peaks_post(self, body, extra, ov, hide, mode, s, t, h, A, eye, ctx):
        nofill = False; lvl = s.get('level', 0)
        if self.soft and self.br['stage'] == 0:                    # m4: calm / sad song: no МАКС, breach, ВОДОВОРОТ or drop ring
            self.charge = 0.0; self.max_on = False; self.shout = None
            body, extra, ov = self.catharsis(body, extra, ov, s, t, h, eye, mode)
            return body, extra, ov, hide, nofill
        hard = ctx.get('peak') != 'rift' and (ctx.get('peak') in ('possess', 'nails', 'descend') or mode in ('mosh', 'grips') or
                                             (mode == 'break' and var_of(ctx) == 'jungle') or (ctx.get('weather') == 'storm'))
        fp = ctx.get('force_possess')
        if self.poss is None and self.br['stage'] == 0 and ((hard and ctx.get('peak') not in ('nails', 'descend', 'stand') and s.get('max_hold', 0) > 2.0 and t >= self.poss_gap) or fp):
            self._poss_start(t, fp or ctx.get('ritual') or 'none', bool(fp))
        if self.poss is not None:                                  # m5: ОДЕРЖИМОСТЬ owns the peak while it runs
            body, extra, ov = self.possess(body, extra, ov, s, t, h, eye, ctx)
            if self.shout:
                cur = [x for x in self.shout if x[0] <= t]
                if cur:
                    st_, txt = cur[-1]; a_ = clamp(1 - (t - st_) / 1.1)
                    if a_ > 0: ov = ov + [('shout', (txt, a_))]
                    elif cur[-1] is self.shout[-1]: self.shout = None
            return body, extra, ov, hide, True
        # ---- build → drop entrance: charge (visor fills from the edges, shaking, pixels pulled in), then explode
        if self.charge > 0.15 and t - self.explode_t > 0.6 and self.br['stage'] < 2:
            c = self.charge; n = int(round(c * 5))
            fill = self.visor([(k, r, C['L'] if k % 2 else C['G'], 0.85) for k in list(range(n)) + list(range(10 - n, 10)) for r in (4, 5)])
            sh = round((self.rng.random() - 0.5) * c * 0.8 * 5) / 5
            body = self.warp(body, lambda x, y: (x + sh + round((OX + 7 - x) * c * 0.12 * 5) / 5, y))
            extra = extra + self.shift(fill, sh, 0)
        u = t - self.explode_t
        if 0 <= u < 0.5:
            k = (1 - u / 0.5) ** 2 * 2.2; nofill = True
            def boom(x, y):
                dx, dy = x - (OX + 7), y - (OY + 5); L = math.hypot(dx, dy) or 1
                return x + dx / L * k, y + dy / L * k
            body = self.warp(body, boom); extra = self.warp(extra, boom)
            ov.append(('ring', (OX + 7, OY + 6, 4 + u * 30, 2 + u * 14, C['B'], 0.8 * (1 - u / 0.5))))
            if u < 0.08: ov.append(('flash', (C['B'], 0.35)))
        # ---- МАКС: hype overload
        mh = s.get('max_hold', 0); on = mh > 1.0
        if on and not self.max_on: self.max_on = True; self.max_t = t; self.shout = [(t, 'ТИШЕ…'), (t + 0.7, 'НЕТ.'), (t + 1.4, 'ГРОМЧЕ.')]; log('peak: МАКС on')
        elif not on and self.max_on and mh <= 0.2: self.max_on = False
        if self.max_on and self.br['stage'] < 3:
            m = clamp(mh / 3)
            sx, sy = round((self.rng.random() - 0.5) * 0.8 * m * 5) / 5, round((self.rng.random() - 0.5) * 0.6 * m * 5) / 5
            body = self.shift(body, sx, sy)
            self.trail.append(body); self.trail = self.trail[-7:]
            if len(self.trail) > 6:
                extra = [[x - 0.8, y, w, hh, C['P'], 0.16] for x, y, w, hh, c, a in self.trail[-4] if a > 0.9][::2] + \
                        [[x + 0.8, y, w, hh, C['G'], 0.12] for x, y, w, hh, c, a in self.trail[0] if a > 0.9][::2] + extra
            for _ in range(int(2 + 4 * m)):
                y = OY + self.rng.random() * 10; L = 1.5 + self.rng.random() * 3
                x = self.rng.choice((OX - 3 - L - self.rng.random() * 2, OX + 16 + self.rng.random() * 2))
                extra.append([x, y, L, 0.15, C['B'], 0.5])
            if h['kick'] or h['punch']:
                ov.append(('edge', (C['P'] if self.rng.random() < 0.5 else C['B'], 0.7)))
                if t - self.max_t > 2.2 and self.rng.random() < 0.25: self.shout = [(t, 'ГРОМЧЕ.')]
        if self.shout:
            cur = [x for x in self.shout if x[0] <= t]
            if cur:
                st, txt = cur[-1]; a = clamp(1 - (t - st) / 0.9)
                if a > 0: ov.append(('shout', (txt, a)))
                elif cur[-1] is self.shout[-1]: self.shout = None
        # ---- the breach: strain → crack → shatter → Blackwall rift → seal
        if hard and self.br['stage'] == 0: nf = False                               # m5: hard songs get ОДЕРЖИМОСТЬ, not the rift
        else: body, extra, ov, nf = self.breach(body, extra, ov, mode, s, t, h, eye, ctx)
        nofill = nofill or nf
        # ---- ВОДОВОРОТ: over-chromed cyberware overload at peak chaos (metal / Death Grips)
        if self.br['stage'] == 0 and mode in ('mosh', 'grips'):
            if s.get('chaos', 0) > 0.7 and lvl > 0.88: self.wo_acc += self.dt
            else: self.wo_acc = max(0.0, self.wo_acc - self.dt)
            if self.wo_t is None and self.wo_acc > 1.0 and t > self.wo_cool: self.wo_t = t; self.wo_cool = t + 60; log('peak: ВОДОВОРОТ')
        if self.wo_t is not None:
            u = t - self.wo_t
            if u > 4.0: self.wo_t = None
            else:
                body, extra, ov = self.maelstrom(body, extra, ov, u, t, h, eye); nofill = True
        return body, extra, ov, hide, nofill

    def maelstrom(self, body, extra, ov, u, t, h, eye):
        """ВОДОВОРОТ (original design): chrome body, a cluster of red optics, a jaw plate, cables, stencil-black outline, hazard-orange flash."""
        if u < 0.3 or u > 3.7:                                               # glitch in / out
            rows = sorted({int(r[1]) for r in body})
            for row in self.rng.sample(rows, min(3, len(rows))):
                off = self.rng.choice((-2, -1, 1, 2))
                body = [[x + off, y, w, hh, c, a] if int(y) == row else [x, y, w, hh, c, a] for x, y, w, hh, c, a in body]
            if self.rng.random() < 0.5: return body, extra, ov
        m = {'#7B4DFF': C['chrome'], '#9D7BFF': C['chromeL'], '#5A3FB0': C['chrome'], '#6E5BB4': C['chromeL'], '#F29AB4': C['orange']}
        out = []
        for x, y, w, hh, c, a in body:
            if self.is_eye([x, y, w, hh, c, a], eye) or c in (C['X'],): continue
            out.append([x, y, w, hh, m.get(c.upper(), c), a])
        dx = (sum(r[0] for r in body) / len(body) - (OX + 6.5)) if body else 0
        outline = [[x + 1, y + 0.2, w, hh, '#000000', 0.8] for x, y, w, hh, c, a in out if c in (C['chrome'], C['chromeL'])]
        optics = [(1, 4), (3, 4), (4, 5), (6, 4), (7, 5), (8, 4), (5, 4)]
        for i, (n, r) in enumerate(optics):
            on = (int(t * 7 + i * 1.7) % 4) != 0
            out.append([OX + 2 + n + dx + 0.15, OY + r + 0.15, 0.7, 0.7, C['R'] if on else '#5A0018', 1.0])
        for n in range(3, 11):                                               # jaw plate with teeth
            out.append([OX + n + dx, OY + 6, 1, 1, '#1A1A1E', 1.0])
            if n % 2: out.append([OX + n + dx + 0.2, OY + 7, 0.6, 0.5, C['B'], 0.9])
        for k, cx in enumerate((1, 12, 13)):                                 # cables hanging from the head, swinging
            for j in range(5):
                sx = math.sin(t * 6 + k + j * 0.6) * 0.3 * j
                out.append([OX + cx + dx + sx, OY + 2 + j * 1.2, 0.35, 1.2, '#2A2A30', 1.0])
            if self.rng.random() < 0.3: extra.append([OX + cx + dx + self.rng.random(), OY + 7.5, 0.3, 0.3, C['orange'], 0.9])
        if u < 0.4 or h['kick'] or h['snare']: ov.append(('flash', (C['orange'], 0.30 if u < 0.4 else 0.16)))
        return outline + out, extra, ov

    # ---- the breach -------------------------------------------------------------
    def breach(self, body, extra, ov, mode, s, t, h, eye, ctx):
        B = self.br; lvl = s.get('level', 0); mh = s.get('max_hold', 0); dt = self.dt; nofill = False
        gap = float(ctx.get('breach_gap', 45))
        if B['stage'] == 0:
            if self.max_on and mh > 1.5 and t >= B['gap_until'] and self.wo_t is None and gap >= 0: self._crack_start(body, t); B['stage'] = 1; log('breach: strain')
            if B['scar'] and t < B['scar'][2]:
                extra = extra + [[B['scar'][0], B['scar'][1], 1, 1, C['R'], 0.9 if int(t * 3) % 2 else 0.5]]
            return body, extra, ov, nofill
        if B['stage'] in (1, 2) and (lvl < 0.7 and mh < 0.3):             # energy left before the shatter: the cracks heal
            if B['healing'] is None: B['healing'] = t
        else: B['healing'] = None
        if B['healing'] is not None and t - B['healing'] > 1.0:
            B['stage'] = 0; B['gap_until'] = t + 10; log('breach: healed before the shatter'); return body, extra, ov, nofill
        heal = 1 - clamp((t - B['healing']) / 1.0) if B['healing'] is not None else 1.0
        if B['stage'] == 1:                                                  # strain: jitter, flicking pixels, a hairline crack
            out = []
            for r in body:
                if 0.98 <= r[2] <= 1.02 and self.rng.random() < 0.03 * heal:
                    r = [r[0] + self.rng.choice((-1, 1)) * 0.6, r[1] + self.rng.choice((-1, 1)) * 0.6, 1, 1, r[4], r[5]]
                out.append(r)
            body = self.shift(out, round((self.rng.random() - 0.5) * 0.4 * 5) / 5, 0)
            extra = extra + self._crack_lines(B['cracks'][:1], 0.5 * heal, 4)
            if mh > 3.0: B['stage'] = 2; B['t'] = t; log('breach: crack')
            return body, extra, ov, nofill
        if B['stage'] == 2:                                                  # crack: branches, slipped tiles, RGB split
            grow = clamp((t - B['t']) / 0.6)
            body = self._slip(body, heal)
            extra = extra + self._crack_lines(B['cracks'], 0.9 * heal, int(3 + 7 * grow))
            body = self.shift(body, round((self.rng.random() - 0.5) * 0.6 * 5) / 5, 0)
            big = h['punch'] or (h['kick'] and lvl > 0.95)
            if (big and grow >= 1) or t - B['t'] > 5: self._shatter(body, t); B['stage'] = 3; log(f'breach: shatter ({len(B["holes"])} pixels) → Blackwall rift')
            return body, extra, ov, True
        # stage 3+: shattered; the rift opens behind him after 0.4 s; seals when the energy drops
        nofill = True
        if B['seal_t'] is None:
            B['below'] = B['below'] + dt if lvl < 0.7 else 0.0
            if (B['below'] > 1.5 and t - B['t'] > 2.5) or t - B['t'] > 30: B['seal_t'] = t; log('breach: sealing')
        sealing = B['seal_t'] is not None
        su = clamp((t - B['seal_t']) / 1.2) if sealing else 0.0
        if not sealing: B['open'] = clamp((t - B['t'] - 0.4) / 0.5)
        else: B['open'] = 1 - su
        if sealing and su >= 1:                                              # sealed: scar pixel for 10 s, cooldown
            cells = [r for r in body if 0.98 <= r[2] <= 1.02 and r[4] in (C['V'], C['L'])]
            if cells:
                r = self.rng.choice(cells); B['scar'] = (r[0], r[1], t + 10)
            B.update(stage=0, gap_until=t + gap, shards=[], holes=[], open=0.0, seal_t=None, pull=None, red_at=None)
            return body, extra, ov + [('flash', (C['B'], 0.3))], nofill
        holes = set(B['holes'])
        keep = [r for r in body if not ((col_of(r), row_of(r)) in holes and 0.98 <= r[2] <= 1.02)]
        static = []
        for (cx, cy) in B['holes']:                                         # the holes show red static: he is a window into the Blackwall
            if sealing and self.rng.random() < su: continue
            static.append([OX + cx, OY + cy, 1, 1, self.rng.choice((C['R'], C['void'], C['X'], '#2A0010', C['R'])), 0.92])
        shards = []
        for sh in B['shards']:
            if sealing:                                                      # rewind: the shards fly back home
                k = 1 - (1 - su) ** 2
                x = sh['x'] + (sh['ox'] - sh['x']) * k; y = sh['y'] + (sh['oy'] - sh['y']) * k
                shards.append([x, y, 1, 1, sh['c'], 1.0])
            else:
                sh['vy'] += 26 * dt; sh['x'] += sh['vx'] * dt; sh['y'] = min(OY + 11.5, sh['y'] + sh['vy'] * dt)
                if sh['y'] >= OY + 11.5: sh['vx'] *= 0.8; sh['life'] -= dt * 0.7
                if sh['life'] > 0: shards.append([sh['x'], sh['y'], 1, 1, sh['c'], clamp(sh['life'])])
        if sealing:
            for sh in B['shards']:
                if not sh.get('fx'): sh['fx'] = True
        # eye goes red after 8 s with the rift open
        if B['open'] >= 1 and not sealing and B['red_at'] is None: B['red_at'] = t + 8
        if B['red_at'] and t >= B['red_at']: keep = self.recolor(keep, {(eye or '').upper(): C['R']})
        # rare: the rift pulls him halfway in, he claws back out
        if B['pull'] is None and B['open'] >= 1 and not sealing:
            B['pull'] = t if self.rng.random() < 0.05 else -1
            if B['pull'] > 0: log('breach: the rift pulls him in (rare)')
        if B['pull'] and B['pull'] > 0:
            u = t - B['pull']
            if u < 3.0:
                k = math.sin(math.pi * min(1, u / 2.6)); keep = [[x, y - 3 * k, w, hh, c, a * (1 - 0.7 * k if y > OY + 5 else 1)] for x, y, w, hh, c, a in keep]
                if u > 2.6: keep = self.shift(keep, (1 if int(t * 20) % 2 else -1) * 0.4, 0)
        under = self.rift(t, B['open'], sealing, su, h, lvl, keep)
        ov.append(('under', under))
        if B['open'] > 0.3: ov.append(('glyphs', self.glyphs(t, B['open'])))
        if sealing and su > 0.85: ov.append(('flash', (C['B'], 0.25)))
        jitter = round((self.rng.random() - 0.5) * 0.4 * 5) / 5
        return self.shift(keep, jitter, 0) + static, extra + shards, ov, nofill

    def _crack_start(self, body, t):
        B = self.br; B['t'] = t
        cells = {(col_of(r), row_of(r)) for r in body if 0.98 <= r[2] <= 1.02 and r[4] in (C['V'], C['L'], C['D'], '#5A3FB0', '#6E5BB4')}
        B['cells'] = cells; paths = []
        for k in range(3):
            p = [(6 + k % 2, 4)]; d = self.rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)])
            for _ in range(self.rng.randrange(5, 10)):
                if self.rng.random() < 0.35: d = self.rng.choice([(d[0], 0), (0, d[1]), (d[0] or 1, d[1] or 1)])
                nx, ny = p[-1][0] + (d[0] or 0), p[-1][1] + (d[1] or 0)
                if (nx, ny) not in cells: break
                p.append((nx, ny))
            paths.append(p)
        B['cracks'] = paths; B['cset'] = {c for p in paths for c in p}
        B['off'] = {c: (self.rng.choice((-0.2, 0.2)), self.rng.choice((-0.2, 0, 0.2))) for p in paths for c in p}
        B['jag'] = [self.rng.choice((-1, 0, 0, 1)) for _ in range(40)]
        B['eyes'] = [(self.rng.uniform(-2.5, 2.5), self.rng.uniform(-12, 6), self.rng.random() * 6) for _ in range(7)]

    def _crack_lines(self, paths, a, n):
        out = []
        for p in paths:
            for (x1, y1), (x2, y2) in list(zip(p, p[1:]))[:n]:
                for k in range(3):
                    f = k / 3
                    out.append([OX + x1 + 0.4 + (x2 - x1) * f, OY + y1 + 0.4 + (y2 - y1) * f, 0.25, 0.25, C['B'], a])
        return out

    def _slip(self, body, heal):
        B = self.br; out = []
        for r in body:
            c = (col_of(r), row_of(r))
            if c in B['off'] and 0.98 <= r[2] <= 1.02:
                ox, oy = B['off'][c]
                out.append([r[0] + ox * heal, r[1] + oy * heal, 1, 1, r[4], r[5]])
                out.append([r[0] - 0.2, r[1], 1, 1, C['X'], 0.3 * heal]); out.append([r[0] + 0.2, r[1], 1, 1, C['G'], 0.25 * heal])
            else: out.append(r)
        return out

    def _shatter(self, body, t):
        B = self.br; B['t'] = t; B['below'] = 0.0
        cells = [r for r in body if 0.98 <= r[2] <= 1.02 and r[5] >= 0.9 and r[4] != C['P']]
        seeds = [self.rng.choice(sorted(B['cset'])) for _ in range(2)] if B['cset'] else [(6, 4)]
        holes, shards = [], []
        for r in cells:
            c = (col_of(r), row_of(r))
            if c[1] >= 8: continue                                           # the feet stay
            near = c in B['cset'] or min(abs(c[0] - sx) + abs(c[1] - sy) for sx, sy in seeds) <= 2
            if near and self.rng.random() < 0.85:
                holes.append(c)
                ang = math.atan2(c[1] - 4.5, c[0] - 6.5) + self.rng.uniform(-0.6, 0.6); sp = 3 + self.rng.random() * 5
                shards.append(dict(x=r[0], y=r[1], ox=r[0], oy=r[1], vx=math.cos(ang) * sp, vy=math.sin(ang) * sp - 4, c=r[4], life=1.6))
        B['holes'] = holes; B['shards'] = shards

    def rift(self, t, open_, sealing, su, h, lvl, body):
        """The Blackwall rift behind him: pixel-stepped tear, red rim with bloom, void, blinking eyes, something drifting, claws."""
        B = self.br; cx = OX + 7; top, bot = OY - 13, OY + 9
        out = []; rows = list(range(top, bot + 1)); n = len(rows)
        zip_k = su if sealing else 0.0
        for i, y in enumerate(rows):
            u = i / (n - 1)
            if sealing and (u < zip_k * 0.5 or u > 1 - zip_k * 0.5): continue    # zips shut from both ends
            prof = math.sin(math.pi * u) ** 0.7
            w = open_ * (1.5 + 3.2 * prof) + (B['jag'][i % len(B['jag'])] if open_ > 0.2 else 0) * 0.6
            if w <= 0.3: continue
            x0 = cx - w + B['jag'][(i * 3) % len(B['jag'])] * 0.5
            out.append([x0 - 1.4, y, 2 * w + 2.8, 1, C['R'], 0.16 * open_])            # bloom
            out.append([x0 - 0.6, y, 2 * w + 1.2, 1, C['R'], 0.9])                    # rim
            out.append([x0 + 0.2, y, 2 * w - 0.4, 1, C['void'], 0.96])                # void
            if self.rng.random() < 0.25: out.append([x0 + 0.2 + self.rng.random() * (2 * w - 0.6), y + 0.4, 0.3, 0.2, C['R'], 0.6])   # red static
        if open_ > 0.6:
            for ex, ey, ph in B['eyes']:
                if top + 2 < OY + ey < bot - 1 and (t * 0.9 + ph) % 3 > 0.35:
                    out += [[cx + ex - 0.3, OY + ey, 0.35, 0.3, C['R'], 0.9], [cx + ex + 0.25, OY + ey, 0.35, 0.3, C['R'], 0.9]]
            B['snake'] = (B['snake'] + self.dt * 1.6)
            base = (bot - (B['snake'] % (bot - top + 8)))
            for j in range(9):                                               # something drifting up inside
                sy = base + j * 0.8
                if top < sy < bot: out.append([cx + math.sin(t * 1.3 + j * 0.7) * 1.4 - 0.4, sy, 0.8, 0.8, '#5A0018', 0.85])
            if top < base < bot: out.append([cx + math.sin(t * 1.3) * 1.4 - 0.1, base + 0.1, 0.3, 0.3, C['R'], 1.0])
            if body:                                                          # his shadow inside, out of sync
                B['shadow'].append(body); B['shadow'] = B['shadow'][-14:]
                sh = B['shadow'][0]
                out += [[x + 0.6, y - 1.2, w, hh, '#3A0012', 0.55] for x, y, w, hh, c, a in sh[::2] if abs(x - cx) < 3.2 and top < y - 1.2 < bot and 0.98 <= w <= 1.02]
        if (h['punch'] or (h['kick'] and lvl > 0.96)) and open_ >= 1 and not sealing: B['claw_t'] = t
        if t - B['claw_t'] < 0.3:                                            # claws reach the rim, never past it
            for k, (sx, sy) in enumerate(((-1, -6), (0.5, -2), (-0.5, 3))):
                for j in range(4):
                    out.append([cx + sx + j * (0.5 if k % 2 else -0.5), OY + sy - j * 0.4, 0.4, 0.4, C['B'] if j == 3 else '#C8C2D0', 0.9])
        return out

    def mini_rift(self, t):
        cx = OX + 7 + self.rng.uniform(-4, 4); out = []
        for i in range(5):
            w = 0.5 + math.sin(math.pi * i / 4) * 1.2
            out += [[cx - w - 0.4, OY + 1 + i, 2 * w + 0.8, 1, C['R'], 0.8], [cx - w, OY + 1 + i, 2 * w, 1, C['void'], 0.9]]
        return out

    def glyphs(self, t, open_):
        """Corrupted Cyrillic scrolling down inside the rift (drawn as text by the desk)."""
        out = []; cx = OX + 7
        for k in range(6):
            y = OY - 12 + ((t * 2.5 + k * 3.7) % 20)
            ch = CYR[int(t * 8 + k * 13) % len(CYR)]
            out.append((cx - 1.5 + (k % 3) * 1.2, y, ch, 0.45 * open_, C['R'] if k % 2 else C['X']))
        return out

