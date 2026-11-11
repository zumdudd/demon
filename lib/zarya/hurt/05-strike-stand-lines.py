

class Strike(Event):
    """СОШЕСТВИЕ v4 (h3): the bottom of the screen cracks open under him; red lightning arcs up out of the cracks and strikes him
    on the song's hits (or every ~0.9 s without music). Every strike rewrites part of him black and red; the last one, all
    bolts at once, finishes it: ПОДМЕНЫШ. He is drawn in front of the lightning the whole time. outcome 'taken'."""
    kind = 'descend'
    dur = 9.0
    STRIKES = 4

    def __init__(self, W, H, pet, why=''):
        super().__init__(W, H, pet)
        r = self.rng; px = max(2, round(H / 480)); self.px = px; self.why = why
        self.cracks = []
        for x0 in [clamp(pet['cx'] / W, 0.03, 0.97), clamp(pet['cx'] / W + 0.06, 0.03, 0.97), clamp(pet['cx'] / W - 0.03, 0.02, 0.97)] + [r.uniform(0.1, 0.95) for _ in range(5)]:
            x = x0 * W; y = H; pts = [(x, y)]
            for _ in range(r.randint(6, 11)):
                x += r.uniform(-0.03, 0.03) * W; y -= r.uniform(0.015, 0.04) * H; pts.append((x, y))
            self.cracks.append(pts)
        self.embers = [(r.uniform(0, W), r.uniform(0.85, 1.25) * H, r.uniform(0.18, 0.35) * H, r.choice((1, 1, 2, 3)) * px, r.random() * 6) for _ in range(180)]
        self.form = pet.get('form'); self.snap = pet.get('snap') or (lambda: {})
        self.hits = []; self.prev = 0.0; self.last = 0.9; self.final = None; self.level = 0.0          # first strike waits for a hit (timer after ~1 s)
        U = pet['U']; cx = pet['cx']                                          # bolts come up from right under / beside him
        self.src = [(cx + dx * U, H) for dx in (-9, -3, 4, 11)] + [pt for pts in self.cracks[:3] for pt in pts[1:4] if pt[1] > pet['cy'] + 6 * U]

    def phase(self, el):
        if el < 1.2: return 'open'
        if self.final is None: return 'strikes'
        if el < self.final + 0.5: return 'final'
        if el < self.dur - 1.0: return 'after'
        return 'close'

    def _tick(self, el):
        """decide strikes: on a kick / snare onset of the real song, else on a timer."""
        if el < 1.4 or self.final is not None: return
        sn = self.snap() or {}
        k = max(sn.get('kick', 0) or 0, sn.get('snare', 0) or 0)
        onset = k >= 0.5 and k > self.prev + 0.2; self.prev = k
        due = (onset and el - self.last > 0.55) or el - self.last > 0.95
        if due:
            self.last = el
            if len(self.hits) < self.STRIKES - 1:
                r = self.rng
                self.hits.append((el, r.choice(self.src), r.random()))
                self.level = len(self.hits) / self.STRIKES
            else:
                self.final = el; self.level = 1.0; self.dur = max(self.dur, el + 3.0)

    def pet(self, el):
        self._tick(el)
        if self.phase(el) == 'open': return dict(hidden=False, react='look_down' if el > 0.4 else None)
        if self.phase(el) in ('after', 'close') and self.outcome is None:
            self.outcome = 'taken'; log('hurt: СОШЕСТВИЕ: the lightning rewrote him')
        return dict(hidden=True)

    def _bolt(self, cr, a, b, el, seed, width, alpha):
        r = random.Random(seed * 1000 + int(el * 20)); pts = [a]; n = 10
        for k in range(1, n):
            u = k / n; jit = (1 - abs(0.5 - u) * 1.4) * 0.35 * math.hypot(b[0] - a[0], b[1] - a[1])
            pts.append((a[0] + (b[0] - a[0]) * u + r.uniform(-jit, jit), a[1] + (b[1] - a[1]) * u + r.uniform(-jit * 0.3, jit * 0.3)))
        pts.append(b)
        for lw, col, al in ((width * 5, (1.0, 0.13, 0.27), 0.35), (width * 2, (1.0, 0.36, 0.54), 0.95), (max(1.5, width * 0.7), (1.0, 0.95, 0.97), 1.0)):
            cr.move_to(*pts[0])
            for p_ in pts[1:]: cr.line_to(*p_)
            cr.set_source_rgba(*col, al * alpha); cr.set_line_width(lw); cr.set_line_join(cairo.LINE_JOIN_ROUND); cr.stroke()
        if r.random() < 0.7:                                                  # a side fork
            k = r.randint(2, 6); fx, fy = pts[k]
            cr.move_to(fx, fy); cr.line_to(fx + r.uniform(-1, 1) * self.p['U'] * 6, fy + r.uniform(-1, 0.5) * self.p['U'] * 4)
            cr.set_source_rgba(1.0, 0.36, 0.54, 0.8 * alpha); cr.set_line_width(max(1, width)); cr.stroke()

    def _him(self, cr, el, gx0, gy0, U, jolt):
        """his frame, cell by cell rewritten as far as the strikes got (red rim under the rewritten cells)."""
        p = self.p; lv = self.level
        rr = [r[:] for r in p['rects']]
        if lv >= 1.0 and self.form is not None:
            rects, ov = self.form.frame([r[:] for r in p['rects']], {}, 4000 + el, music=False)
            if self.phase(el) == 'after' and el - self.final < 2.2: ov = [o for o in ov if o[0] != 'shout'] + [('shout', ('ЭТО БОЛЬШЕ НЕ ОН.', 1.0))]
            draw_frame(cr, rects, ov, gx0 + jolt[0], gy0 + jolt[1], U); return
        under, out = [], []
        for x, y, w, h, c, a in rr:
            if _hash(int(x * 3), int(y * 3), 9) < lv and 0.9 <= w <= 1.1:
                out.append([x, y, w, h, INK, a])
                for dx, dy in ((-0.4, 0), (0.4, 0), (0, -0.4), (0, 0.4)): under.append([x + dx, y + dy, w, h, RED, 0.9])
            else: out.append([x, y, w, h, c, a])
        draw_frame(cr, out, [('under', under)], gx0 + jolt[0], gy0 + jolt[1], U)

    def draw(self, cr, el):
        W, H, p = self.W, self.H, self.p
        self._tick(el)
        env = min(1.0, el / 0.7) * min(1.0, max(0.0, (self.dur - el) / 1.0))
        if env <= 0: return
        px = self.px; ph = self.phase(el); U = p['U']
        recent = [h for h in self.hits if 0 <= el - h[0] < 0.22] + ([(self.final, None, 0)] if self.final is not None and 0 <= el - self.final < 0.5 else [])
        pulse = 0.75 + 0.25 * math.sin(el * 7.0) + (0.6 if recent else 0)
        for x0, y0, x1, y1 in ((0, 0, 0, H * 0.25), (0, 0, W * 0.16, 0), (W, 0, W * 0.84, 0)):
            g = cairo.LinearGradient(x0, y0, x1, y1); g.add_color_stop_rgba(0, 0.25 * min(1, pulse), 0.0, 0.04, 0.65 * env); g.add_color_stop_rgba(1, 0.05, 0, 0.02, 0)
            cr.set_source(g); cr.paint()
        g = cairo.LinearGradient(0, H, 0, H * 0.55)
        g.add_color_stop_rgba(0, 1.0, 0.13, 0.27, min(0.85, 0.42 * env * pulse)); g.add_color_stop_rgba(0.5, 0.6, 0.02, 0.1, 0.18 * env); g.add_color_stop_rgba(1, 0.2, 0, 0.05, 0)
        cr.set_source(g); cr.rectangle(0, H * 0.55, W, H * 0.45); cr.fill()
        grow = min(1.0, el / 1.2)
        for pts in self.cracks:
            n = max(2, int(len(pts) * grow))
            for lw, col, al in ((18 * px / 3, (1.0, 0.13, 0.27), 0.30 * min(1, pulse)), (5 * px / 3, (1.0, 0.36, 0.54), 0.95), (2, (1.0, 0.92, 0.92), 0.95)):
                cr.move_to(*pts[0])
                for qq in pts[1:n]: cr.line_to(*qq)
                cr.set_source_rgba(*col, al * env); cr.set_line_width(lw); cr.stroke()
        for x, y0, sp, sz, ph_ in self.embers:
            y = H * 1.05 - ((H * 1.25 - y0) + sp * el) % (H * 0.85)
            if y < H * 0.2 or y > H: continue
            a = env * (0.5 + 0.4 * math.sin(el * 5 + ph_)) * min(1.0, (y - H * 0.2) / (H * 0.25))
            cr.set_source_rgba(1.0, 0.45 + 0.3 * math.sin(ph_), 0.1, a); cr.rectangle(round(x + math.sin(el * 2 + ph_) * sz * 4), round(y), sz, sz); cr.fill()
        tgt = (p['cx'], p['cy'] + 3 * U)
        jolt = (0, 0)
        for t0, src, sd in self.hits:                                         # each strike: a bolt into him, he jolts
            u = el - t0
            if 0 <= u < 0.22: self._bolt(cr, src, tgt, el, int(sd * 999), 2.2 * px, 1 - u / 0.22); jolt = (self.rng.choice((-2, 2)) * px, -U * (1 - u / 0.22))
        if self.final is not None and 0 <= el - self.final < 0.5:            # the last one: every crack at once, white flash
            u = el - self.final
            for k, a_ in enumerate(self.src): self._bolt(cr, a_, tgt, el, 50 + k, 3 * px, 1 - u / 0.5)
            if u < 0.12: cr.set_source_rgba(1, 1, 1, 0.55 * (1 - u / 0.12)); cr.paint()
            jolt = (self.rng.choice((-3, 3)) * px, -2 * U * (1 - u / 0.5))
        if ph in ('strikes', 'final', 'after', 'close'):                      # him, in front of all of it
            if recent:
                c_ = cairo.RadialGradient(tgt[0], tgt[1] - 3 * U, 0, tgt[0], tgt[1] - 3 * U, 14 * U)
                c_.add_color_stop_rgba(0, 1.0, 0.36, 0.54, 0.55); c_.add_color_stop_rgba(1, 1.0, 0.13, 0.27, 0)
                cr.set_source(c_); cr.arc(tgt[0], tgt[1] - 3 * U, 14 * U, 0, 2 * math.pi); cr.fill()
            self._him(cr, el, p['gx0'], p['gy0'], U, jolt)
            if recent and self.level < 1:
                for _ in range(6): _text(cr, self.rng.choice(GLYPHS), tgt[0] + self.rng.uniform(-9, 9) * U, tgt[1] - self.rng.uniform(0, 12) * U, 14, RED, 0.8)


class Shadow(Event):
    """ТЕНЬ: while he is ПОДМЕНЫШ, at the hardest moment the big demon (his true shape) rises half-transparent behind him
    from the bottom of the screen, opens its burning eye, and sinks back. He stays in front of it."""
    kind = 'shadow'
    dur = 7.5

    def __init__(self, W, H, pet, why=''):
        super().__init__(W, H, pet); self.T = true_cells(pet['rects']); self.why = why

    def draw(self, cr, el):
        W, H, p = self.W, self.H, self.p
        rise = ease(clamp(el / 2.2)) * (1 - ease(clamp((el - 5.4) / 2.0)))
        Hpx = H * 0.62; QX = int(max(6, int(Hpx / self.T['rows'])) * 1.25)
        cx = max(p['cx'] + 2 * p['U'], 7 * QX + 10)
        base = H + Hpx * 0.06 + (1 - rise) * Hpx * 1.05
        glow = clamp((el - 2.4) / 0.4) * clamp((5.6 - el) / 0.5)
        g = cairo.LinearGradient(0, H, 0, H * 0.4); g.add_color_stop_rgba(0, 0.4, 0.02, 0.08, 0.35 * rise); g.add_color_stop_rgba(1, 0.4, 0.02, 0.08, 0)
        cr.set_source(g); cr.rectangle(0, H * 0.4, cx + 9 * QX, H * 0.6); cr.fill()
        draw_true(cr, self.T, el, cx, base, Hpx, alpha=0.55 * rise + 0.001, glow=glow)

    def pet(self, el): return dict(hidden=False)


GOLD, GOLD_L, GOLD_W, BRONZE = '#F7D58C', '#FFE9B0', '#FFF7E0', '#B8863B'


def _star(cr, x, y, r, a, rot=0.0, thin=0.08):
    """a four-point glint (long thin rays + a soft core)."""
    if a <= 0.02 or r < 1: return
    cr.save(); cr.translate(x, y); cr.rotate(rot)
    for ang in (0, math.pi / 2):
        cr.save(); cr.rotate(ang)
        g = cairo.LinearGradient(-r, 0, r, 0)
        g.add_color_stop_rgba(0, 1, 0.95, 0.8, 0); g.add_color_stop_rgba(0.5, 1, 0.98, 0.9, a); g.add_color_stop_rgba(1, 1, 0.95, 0.8, 0)
        cr.set_source(g); cr.move_to(-r, 0); cr.line_to(0, -r * thin); cr.line_to(r, 0); cr.line_to(0, r * thin); cr.close_path(); cr.fill()
        cr.restore()
    g = cairo.RadialGradient(0, 0, 0, 0, 0, r * 0.3); g.add_color_stop_rgba(0, 1, 0.98, 0.9, a); g.add_color_stop_rgba(1, 1, 0.9, 0.6, 0)
    cr.set_source(g); cr.arc(0, 0, r * 0.3, 0, 2 * math.pi); cr.fill(); cr.restore()


class Stand(Event):
    """ПОСЛЕДНИЙ РУБЕЖ (the last stand, h4): for epic songs, the opposite of ПОДМЕНЫШ. Gold light comes down, time slows, he
    plants a spear of light and braces; on the song's next big hit he leaps toward the light, a star flare at the top, time
    holds, he comes down and the impact bursts into gold motes; he kneels, gets up: «…ЕЩЁ НЕ ВСЁ.» Blessed (gold rim) after.
    Original design (mood: a lone hunter under a sky that bursts into light); the scene draws him itself."""
    kind = 'stand'
    dur = 12.0

    def __init__(self, W, H, pet, why=''):
        super().__init__(W, H, pet)
        r = self.rng; self.why = why; self.snap = pet.get('snap') or (lambda: {})
        self.motes = [(r.uniform(0, W), r.uniform(-0.1, 1.0) * H, r.uniform(6, 22), r.choice((1, 1, 2, 2, 3)) * max(1, H // 480), r.random() * 6, r.random() < 0.12) for _ in range(260)]
        self.rays = [(r.uniform(-0.1, 1.1) * W, r.uniform(0.04, 0.1) * W, r.uniform(0.08, 0.2), r.random() * 6) for _ in range(9)]
        self.leap = None; self.prev = 0.0; self.burst = []; self.impact = None

    def phase(self, el):
        if el < 2.0: return 'dawn'
        if self.leap is None: return 'brace'
        u = el - self.leap
        if u < 0.7: return 'leap'
        if u < 1.5: return 'apex'
        if u < 1.8: return 'fall'
        if u < 5.0: return 'kneel'
        return 'fade'

    def _tick(self, el):
        if self.leap is not None or el < 3.6: return
        sn = self.snap() or {}
        k = max(sn.get('kick', 0) or 0, sn.get('snare', 0) or 0)
        onset = k >= 0.5 and k > self.prev + 0.2 and (sn.get('level', 1) or 0) > 0.6; self.prev = k
        if onset or el > 6.0:
            self.leap = el; self.dur = el + 6.6

    def pet(self, el):
        self._tick(el)
        if self.phase(el) == 'fade' and self.outcome is None: self.outcome = 'stood'; log('peak: ПОСЛЕДНИЙ РУБЕЖ: he got back up')
        return dict(hidden=True)

    def _him(self, cr, el, dy, flat=1.0, spear=1.0, spear_up=False, glow=0.0, dx=0.0):
        p = self.p; U = p['U']
        rr = [r[:] for r in p['rects']]
        rr = [[x, y, w, h, GOLD_W if (OY + 4 <= y < OY + 6 and c.upper() not in ('#07060D', '#7B4DFF', '#9D7BFF', '#5A3FB0', '#6E5BB4')) else c, a] for x, y, w, h, c, a in rr]
        if flat != 1.0: rr = [[x, OY + 10 - (OY + 10 - y) * flat, w, h * flat, c, a] for x, y, w, h, c, a in rr]
        rim = []
        for ox, oy_ in ((-0.4, 0), (0.4, 0), (0, -0.4), (0, 0.4)):
            rim += [[x + ox, y + oy_, w, h, GOLD, 0.85] for x, y, w, h, c, a in rr if a > 0.5]
        if spear > 0:                                                       # a spear of light, built bottom-up, pennant at the top
            sx = OX + 15.5; top = OY - 7 if not spear_up else OY - 11
            n = int((OY + 10 - top) * spear)
            for k in range(n): rim.append([sx, OY + 10 - k - 1, 0.6, 1, GOLD_L if k % 3 else GOLD_W, 0.95])
            if spear >= 1:
                rim += [[sx - 0.4, top - 1, 1.4, 1, GOLD_W, 1.0], [sx - 0.1, top - 2, 0.8, 1, GOLD_W, 1.0]]
                wave = math.sin(el * 6) * 0.5
                for k in range(4): rim.append([sx + 0.6, top + 0.5 + k * 0.5, 2.2 - k * 0.4 + wave * (k / 4), 0.5, BRONZE if k % 2 else GOLD, 0.95])
        gx0, gy0 = p['gx0'] + dx, p['gy0'] + dy
        if glow > 0:
            cx, cy = gx0 + (OX + 7) * U, gy0 + (OY + 5) * U
            g = cairo.RadialGradient(cx, cy, 0, cx, cy, 18 * U); g.add_color_stop_rgba(0, 1, 0.92, 0.6, 0.5 * glow); g.add_color_stop_rgba(1, 1, 0.85, 0.5, 0)
            cr.set_source(g); cr.arc(cx, cy, 18 * U, 0, 2 * math.pi); cr.fill()
        draw_frame(cr, rr, [('under', rim)], gx0, gy0, U)

    def draw(self, cr, el):
        W, H, p = self.W, self.H, self.p; U = p['U']; self._tick(el)
        ph = self.phase(el)
        env = min(1.0, el / 1.5) * min(1.0, max(0.0, (self.dur - el) / 1.4))
        frozen = ph == 'apex'
        tm = el if self.leap is None else (self.leap + min(el - self.leap, 0.7) + max(0.0, el - self.leap - 1.5) * 0.4)   # time holds at the top
        cr.set_source_rgba(0.95, 0.76, 0.38, 0.30 * env); cr.paint()                       # warm wash: the screen turns to old gold
        g = cairo.LinearGradient(0, 0, 0, H * 0.75); g.add_color_stop_rgba(0, 1.0, 0.86, 0.5, 0.55 * env); g.add_color_stop_rgba(1, 1.0, 0.86, 0.5, 0)
        cr.set_source(g); cr.rectangle(0, 0, W, H * 0.75); cr.fill()
        for x, w, a, ph_ in self.rays:                                          # god rays
            sway = math.sin(tm * 0.3 + ph_) * W * 0.02
            g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgba(0, 1, 0.93, 0.7, a * env); g.add_color_stop_rgba(1, 1, 0.93, 0.7, 0)
            cr.set_source(g); cr.move_to(x + sway, 0); cr.line_to(x + sway + w, 0); cr.line_to(x + sway * 3 + w * 2.2, H); cr.line_to(x + sway * 3 - w * 0.6, H); cr.close_path(); cr.fill()
        for x, y0, sp, sz, ph_, glint in self.motes:                           # slow drifting light (stops while time holds)
            y = (y0 + sp * tm) % (H * 1.05); xx = x + math.sin(tm * 0.6 + ph_) * 12
            a = env * (0.35 + 0.35 * math.sin(tm * 1.7 + ph_))
            if glint and a > 0.3: _star(cr, xx, y, sz * 7, a, 0.0, 0.07)
            else: cr.set_source_rgba(1, 0.95, 0.78, a); cr.rectangle(round(xx), round(y), sz, sz); cr.fill()
        lift = 0.0; drift = 0.0; flat = 1.0; spear = clamp((el - 2.0) / 1.2); spear_up = False; glow = 0.0
        LX = min(W * 0.14, 46 * U)                                             # he leaps up and in, toward the light
        if ph == 'dawn': flat = 1.0
        elif ph == 'brace': flat = 0.86 + 0.02 * math.sin(el * 3); glow = 0.3
        elif ph == 'leap':
            u = (el - self.leap) / 0.7; lift = -ease(u) * H * 0.24; drift = ease(u) * LX; spear_up = True; glow = 0.6
        elif ph == 'apex':
            lift = -H * 0.24 - math.sin((el - self.leap - 0.7) / 0.8 * math.pi) * U * 2; drift = LX; spear_up = True; glow = 1.0
        elif ph == 'fall':
            u = (el - self.leap - 1.5) / 0.3; lift = -H * 0.24 * (1 - u ** 2); drift = LX * (1 - u); spear_up = False; glow = 0.8
        elif ph == 'kneel':
            if self.impact is None:
                self.impact = el; cx, cy = p['cx'], p['cy'] + 5 * U; r = self.rng
                self.burst = [(cx, cy, math.cos(a) * s_, math.sin(a) * s_ * 0.6 - r.uniform(40, 160), r.choice((2, 3, 4)), r.random() < 0.15)
                              for a, s_ in ((r.uniform(math.pi, 2 * math.pi) if r.random() < 0.8 else r.uniform(0, math.pi), r.uniform(80, 620)) for _ in range(320))]
            u = el - self.leap - 1.8; flat = 0.72 if u < 2.0 else 0.72 + 0.28 * clamp((u - 2.0) / 0.8); glow = max(0.0, 0.8 - u * 0.3)
        else: glow = 0.1
        if self.impact is not None:                                             # impact: a gold ring along the ground + the burst
            u = el - self.impact; cx, cy = p['cx'], p['cy'] + 5 * U
            if u < 0.15: cr.set_source_rgba(1, 0.97, 0.88, 0.5 * (1 - u / 0.15)); cr.paint()
            if u < 1.2:
                cr.save(); cr.translate(cx, cy); cr.scale(1, 0.18); cr.arc(0, 0, u * W * 0.45, 0, 2 * math.pi); cr.restore()
                cr.set_source_rgba(1, 0.9, 0.6, 0.8 * (1 - u / 1.2)); cr.set_line_width(4); cr.stroke()
            for x, y, vx, vy, sz, glint in self.burst:
                t_ = u; xx = x + vx * t_ * (1 - t_ * 0.18); yy = y + vy * t_ + 60 * t_ * t_ - 30 * t_
                a = max(0.0, 1 - t_ / 3.2) * env
                if glint: _star(cr, xx, yy, sz * 6, a, 0.0, 0.08)
                else: cr.set_source_rgba(1, 0.93, 0.7, a); cr.rectangle(round(xx), round(yy), sz, sz); cr.fill()
        self._him(cr, el, lift, flat, spear, spear_up, glow, drift)
        if ph in ('leap', 'apex', 'fall'):                                      # the star flare at the top
            u = el - self.leap; k = clamp((u - 0.5) / 0.25) * clamp((1.75 - u) / 0.3)
            fx, fy = p['cx'] + drift + 2 * U, p['cy'] + lift - 4 * U
            g = cairo.RadialGradient(fx, fy, 0, fx, fy, H * 0.35); g.add_color_stop_rgba(0, 1, 0.97, 0.85, 0.75 * k); g.add_color_stop_rgba(1, 1, 0.9, 0.6, 0)
            cr.set_source(g); cr.arc(fx, fy, H * 0.35, 0, 2 * math.pi); cr.fill()
            _star(cr, fx, fy, H * 0.55 * k, 0.95 * k, -0.45, 0.025); _star(cr, fx, fy, H * 0.3 * k, 0.8 * k, 0.35, 0.03)
            cr.save(); cr.translate(fx, fy); cr.scale(1, 0.85); cr.arc(0, 0, H * 0.09 * k, -0.4, 2.2); cr.restore()
            cr.set_source_rgba(1, 0.95, 0.8, 0.8 * k); cr.set_line_width(3); cr.stroke()
        if ph == 'brace' and el > 2.6: _shout(cr, 'Я ОСТАЮСЬ.', max(p['cx'] + 2 * U, 90), p['gy0'] + (OY - 9) * U, int(2.6 * U), clamp((el - 2.6) / 0.3) * env)
        if ph == 'kneel' and el - self.impact > 1.0: _shout(cr, '…ЕЩЁ НЕ ВСЁ.', max(p['cx'] + 2 * U, 100), p['gy0'] + (OY - 9) * U, int(2.6 * U), clamp((el - self.impact - 1.0) / 0.4))


# ============================================================ ПОСЛЕДНИЙ РУБЕЖ (h5): dark-epic last stand, inside his own window
# Black, bone and blood red; ink hatching. Mood reference only (Berserk's hundred-man fight and its red sky): no Brand, no
# Dragonslayer silhouette, no armour, no characters. Grid units like the sprite (x 0-127, y down to -41 above the sprite).
IRON, IRON_L, IRON_D, CAPE, CAPE_R, BLADE, BLADE_L, ASH = '#2E2A33', '#4A4552', '#16141A', '#0B0910', '#5A0A14', '#57525E', '#8C8794', '#3A3640'
FOE = ['...XXX...', '..XXXXX..', '..XRXRX..', '..XXXXX..', '.XXXXXXX.', 'X.XXXXX.X', 'X.XXXXX.X', '..XXXXX..', '..XX.XX..', '..X...X..']
STAND_LINES = ['ЕЩЁ.', 'ПОДХОДИ.', 'МАЛО.', 'СЛЕДУЮЩИЙ.']
