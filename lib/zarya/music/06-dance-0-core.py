

class Dance(_Dance1, _Dance2, _Dance3):
    """Per-song memory. draw() returns (rects, overlays, hide). rects in zarya-daemon's grid: [x, y, w, h, '#hex', alpha];
    overlays are (kind, args) for cairo: spot, ring, letterbox, tear, invert, flash, edge, speed, shout, under, glyphs."""
    def __init__(self):
        self.parts = []; self.hist = []; self.hold = None; self.hold_n = 0; self.cut_until = 0; self.flip = False
        self.jump = (0, 0); self.feet = 0; self.scatter = {}; self.blast = 0.0; self.last_t = 0; self.tick_cells = [None] * 10
        self.step_t = 0; self.seed = random.random(); self.rng = random.Random()
        self.prev = dict(kick=0, snare=0, hat=0, vocal=0, punch=0)
        self.dt = 0.033; self.t_prev = None
        # m2
        self.move_i = 0; self.move_sec = -1; self.move_t = 0; self.hop = None; self.hop_n = 0
        self.ear_side = 0; self.ear_t = 0; self.flick = {}; self.fold_until = 0; self.feet_f = 'stand'; self.feet_until = 0; self.foot = 0
        self.face_until = 0; self.face = None
        self.wparts = []; self.vrain = []; self.cloud = None; self.bolt = None; self.bolt_t = -9; self.sparks = []; self.embers = []; self.hearts = []
        self.wind = []; self.dust = []; self.heart_t = 0
        self.charge = 0.0; self.drop_seen = -99; self.explode_t = -9
        self.trail = []; self.shout = None; self.max_on = False; self.max_t = 0
        self.br = dict(stage=0, t=0, gap_until=0, cracks=[], cset=set(), off={}, shards=[], holes=[], open=0.0, below=0, seal_t=None,
                       scar=None, pull=None, claw_t=-9, eyes=[], snake=0, jag=[], shadow=[], red_at=None, healing=None)
        self.wo_t = None; self.wo_acc = 0.0; self.wo_cool = 0; self.vanish_until = 0; self.epic_hold = None; self.epic_t = -9
        self.cursed = False; self.eyehist = []
        # m4
        self.cath_t = None; self.cath_cool = 0; self.motes = []; self.smoke = []; self.puff_t = 0; self.stars = None
        self.poles = []; self.pole_t = 0; self.petals = []; self.close_until = 0; self.notes = []; self.frames = []
        self.hook_t = None; self.hook_seen = set(); self.last_pos = None; self.run_stop = False; self.run_drop = -99
        self.skyline = None; self.soft = False
        # m5
        self.poss = None; self.poss_gap = 0; self.jerk = (0, 0); self.sweat = []; self.chant = []; self.sparks2 = []

    @staticmethod
    def amp(s):
        """Calm between moments: full only at track start, drops and loud peaks."""
        return max(0.25, min(1.0, 0.25 + 0.75 * max(s.get('excite', 0), (s.get('level', 0) ** 3) * 0.45)))

    def hits(self, s):
        out = {k: s.get(k, 0) >= 0.5 and s.get(k, 0) > self.prev[k] + 0.2 for k in self.prev}
        self.prev = {k: s.get(k, 0) for k in self.prev}
        return out

    # ---------------------------------------------------------------- main
    def draw(self, rects, mode, var, s, t, eye, ctx=None):
        ctx = ctx or {}
        self.dt = 0.033 if self.t_prev is None else max(0.0, min(0.1, t - self.t_prev)); self.t_prev = t
        h = self.hits(s); A = self.amp(s); weather = ctx.get('weather') or ''
        cursed = any(c[1] == 'cursed' and ctx.get('pos', -1) >= c[0] for c in ctx.get('cues') or [])
        if cursed and not self.cursed: log('peak: cursed cue reached')
        self.cursed = cursed
        if mode != getattr(self, '_parts_mode', mode): self.parts = []            # m13: modes keep different particles (rain vs sparks)
        self._parts_mode = mode
        self._move(mode, s, t)
        self._peaks_pre(s, t, h, mode)
        self.soft = mode in CALM or (weather in ('rain', 'dawn') and mode in ('groove', 'nod', 'epic', 'kawaii'))   # m4
        self.ctx = ctx; ctx['_var'] = var
        owns_eye = mode in ('break', 'mosh', 'kendrick', 'grips', 'rest') or self.br['stage'] >= 2
        body = self.lang(list(rects), mode, var, s, t, eye, h, A, weather, owns_eye)
        if self.br['stage'] >= 2:                                         # breaking: the dance pauses, he shakes and cracks
            extra, ov, hide = [], [], False
        else:
            fn = getattr(self, 'm_' + mode, self.m_groove)
            body, extra, ov, hide = fn(body, var, s, t, eye, h, A)
        if mode != 'memory': extra += self.weather_fx(weather, s, t, h, A, ov, ctx)
        if s.get('punch', 0) > 0.05 and mode not in ('memory', 'kendrick') and not self.soft and self.br['stage'] < 2:
            p = s['punch']; jx = round((self.rng.random() - 0.5) * p * 0.8 * 5) / 5            # squash: rows overlap, never split
            body = self.warp(body, lambda x, y: (x + jx, y + 0.8 * p * max(0.0, (OY + 8 - y)) / 8))
            r = (1 - p) * 9 + 1
            ov.append(('ring', (OX + 7, OY + 10, r * 1.6, r * 0.5, C['L'], 0.55 * p)))
        body, extra, ov, hide, nofill = self._peaks_post(body, extra, ov, hide, mode, s, t, h, A, eye, ctx)
        if hide: return [], ov, True
        out = body + extra
        if not nofill and mode != 'grips': gapfill(out)
        return out, ov, False

    # ---------------------------------------------------------------- helpers
    @staticmethod
    def warp(rects, f):
        out = []
        for x, y, w, hh, c, a in rects:
            nx, ny = f(x, y); out.append([nx, ny, w, hh, c, a])
        return out

    @staticmethod
    def shift(rects, dx, dy):
        return [[x + dx, y + dy, w, hh, c, a] for x, y, w, hh, c, a in rects]

    @staticmethod
    def recolor(rects, m):
        return [[x, y, w, h, m.get(c.upper(), m.get(c, c)), a] for x, y, w, h, c, a in rects]

    @staticmethod
    def is_eye(r, eye):
        return r[4].upper() == (eye or '').upper() and OY + 4 <= r[1] <= OY + 5.99

    def visor(self, cells, rows=(4, 5)):
        return [[OX + 2 + n, OY + row, 1, 1, c, a] for n, row, c, a in cells]

    def spectrum(self, s, alpha=0.5, col=None):
        b = s.get('bars') or [0] * 16; out = []
        for n in range(10):
            v = max(b[min(15, int(n * 1.6))], b[min(15, int(n * 1.6) + 1)])
            if v > 0.08: out.append((n, 5, col or C['V'], alpha * min(1, v * 1.4)))
            if v > 0.45: out.append((n, 4, col or C['V'], alpha * min(1, (v - 0.35) * 1.6)))
        return self.visor(out)

    def _move(self, mode, s, t):
        sec = s.get('section', 0)
        if sec != self.move_sec or t - self.move_t > 24:                   # new section (or 24 s): another move
            n = len(MOVES.get(mode, ('x',)))
            if self.move_sec >= 0 and n > 1: self.move_i = (self.move_i + 1 + self.rng.randrange(n - 1)) % n
            self.move_sec = sec; self.move_t = t

    def mv(self, mode):
        m = MOVES.get(mode); return m[self.move_i % len(m)] if m else ''

    def hop_state(self, t):
        """A proper pixel jump: crouch → air → landing. Moves the WHOLE sprite (feet included), so nothing splits."""
        if self.hop is None: return 0.0, ''
        u = t - self.hop
        if u < 0.07: return 0.4, 'splay'
        if u < 0.32: return -1.6 * math.sin(math.pi * (u - 0.07) / 0.25) * self.hop_h, 'tuck'
        if u < 0.42: return 0.3, 'splay'
        self.hop = None; return 0.0, ''

    def start_hop(self, t, height=1.0):
        if self.hop is None: self.hop = t; self.hop_h = height

    # ---------------------------------------------------------------- body language: ears, feet, face, visor
    def lang(self, body, mode, var, s, t, eye, h, A, weather, owns_eye):
        lvl = s.get('level', 0)
        # ---- ears (rows 0-1)
        if h['hat'] and t - self.ear_t > 0.14 and mode not in ('kendrick',) + CALM:
            self.ear_t = t; self.ear_side ^= 1; self.flick[self.ear_side] = t + 0.10
        if mode == 'kendrick' and h['snare'] and self.rng.random() < 0.3: self.flick[self.rng.randrange(2)] = t + 0.12
        if (h['punch'] or (h['kick'] and lvl > 0.9 and s.get('excite', 0) > 0.6)) and mode not in ('kendrick',) + CALM: self.fold_until = t + 0.22
        pinned = mode == 'mosh' and lvl > 0.45 and s.get('kick', 0) > 0.3
        perk = self.charge > 0.3
        droop = (weather == 'rain' or (mode == 'run' and self.run_stop)) and not perk
        wig = (1 if int(t * 4) % 2 else -1) if mode == 'kawaii' else 0
        tip = WCOL.get(weather)
        out = []
        for r in body:
            rw = row_of(r); cl = col_of(r)
            if rw == 0 and 0.98 <= r[2] <= 1.02:
                if t < self.fold_until or pinned: continue                  # ears fold flat
                left = cl <= 6; side = 0 if left else 1
                dx = 0
                if t < self.flick.get(side, 0): dx = -1 if left else 1
                if droop: dx = -1 if left else 1
                if wig: dx = wig if left else -wig
                r = [r[0] + dx, r[1], r[2], r[3], (tip if (tip and r[4] in (C['V'], '#5A3FB0')) else r[4]), r[5]]
            out.append(r)
        if perk:
            for cx in (2, 11):
                out.append([OX + cx - 1, OY - 1, 1, 1, C['P'], 0.85]); out.append([OX + cx, OY - 1, 1, 1, C['V'], 1.0])
        # ---- feet (rows 8-9)
        hy, hf = self.hop_state(t)
        f = self.feet_f if t < self.feet_until else 'stand'
        bpm2 = (s.get('bpm') or 0) * (2 if (s.get('bpm') or 0) < 100 else 1)
        if hf: f = hf
        elif mode == 'mosh': f = 'wide'
        elif mode == 'kawaii': f = 'tiptoe' if int(s.get('phase', 0) * 2) % 2 == 0 else 'stand'
        elif mode == 'kendrick' or mode == 'grips': f = 'stand'
        elif mode == 'memory': f = 'stand' if int(t / 1.2) % 2 else 'alt'
        elif mode == 'rest': f = 'tuck'                                              # m4: sitting
        elif mode == 'drive': f = 'stand'
        elif mode == 'bolero': f = 'stand' if int(t / 1.5) % 2 else 'alt'
        elif mode == 'run': f = 'stand' if self.run_stop else ('stepL' if int(s.get('phase', 0) * 4 if s.get('bpm') else t * 8) % 2 else 'stepR')
        elif mode == 'hum': f = 'stepL' if int(s.get('phase', 0) * 2 if s.get('bpm') else t * 2) % 2 else 'stepR'
        elif mode == 'epic': f = self.feet_f if t < self.feet_until else 'wide'
        elif (mode == 'break' and var != 'liquid') or (bpm2 >= 160 and mode in ('groove', 'break')):
            f = 'stepL' if int(s.get('phase', 0) * 4) % 2 else 'stepR'      # running in place on 16ths
        else:
            if h['kick']: self.foot ^= 1; self.feet_f = 'stepL' if self.foot else 'stepR'; self.feet_until = t + 0.16
            elif h['snare'] and self.rng.random() < 0.5: self.feet_f = 'stepR' if self.foot else 'stepL'; self.feet_until = t + 0.08
            f = self.feet_f if t < self.feet_until else 'stand'
        out = [r for r in out if row_of(r) not in (8, 9) or not (0.98 <= r[2] <= 1.02)]
        for yy, row in enumerate(FEET[f]):
            for xx, ch in enumerate(row):
                if ch == 'V':
                    out.append([OX + xx - 1, OY + 8 + yy, 1, 1, C['P'], 0.85]); out.append([OX + xx, OY + 8 + yy, 1, 1, C['V'], 1.0])
        if hy: out = self.shift(out, 0, round(hy * 5) / 5)
        # ---- face + visor (only when the mode does not own the eye)
        if owns_eye: return out
        vis = self.visor_weather(weather, s, t, mode)
        face = None
        if mode == 'kawaii': face = self.mv('kawaii')
        elif mode == 'epic': face = 'torch'
        elif weather == 'rain' and s.get('excite', 0) < 0.7: face = 'sad'
        if h['kick'] and lvl > 0.9 and s.get('excite', 0) > 0.7 and mode not in ('kawaii',): self.face_until = t + 0.12
        if t < self.face_until: face = 'wide'
        if not face and not vis: return out
        base = [r for r in out if not self.is_eye(r, eye)]
        eyes = [r for r in out if self.is_eye(r, eye)]
        e = eye or C['G']
        if face == 'sad':
            c = min(8, max(0, col_of(eyes[0]) - 2)) if eyes else 4
            eyes = self.visor([(c, 5, e, 0.75), (c + 1, 5, e, 0.75)])
        elif face == 'wide':
            eyes = self.visor([(4, 4, C['B'], 1.0), (5, 4, C['B'], 1.0), (4, 5, C['B'], 1.0), (5, 5, C['B'], 1.0), (3, 4, e, 0.5), (6, 5, e, 0.5)])
        elif face == 'torch':
            fl = self.rng.random()
            eyes = self.visor([(4, 4, C['ember'], 1.0), (5, 4, C['ember'], 1.0), (4, 5, '#FFD08A', 1.0), (5, 5, '#FFD08A', 1.0)])
            eyes += [[OX + 6 + (fl > 0.5), OY + 3 - fl * 0.6, 1, 0.6 + fl * 0.4, C['ember'], 0.55], [OX + 7 - (fl > 0.7), OY + 2.6 - fl, 0.6, 0.6, '#FFD08A', 0.35 * fl]]
        elif face in ('arcs', 'uwu', 'wink'):
            if face == 'arcs': cells = [(1, 5), (2, 4), (3, 5), (6, 5), (7, 4), (8, 5)]                 # ^ ^
            elif face == 'uwu': cells = [(1, 4), (2, 5), (3, 4), (6, 4), (7, 5), (8, 4)]                # u u
            else: cells = [(1, 5), (2, 4), (3, 5), (6, 5), (7, 5), (8, 5)]                              # ^ -
            eyes = self.visor([(n, r, e, 1.0) for n, r in cells]) + self.visor([(0, 5, C['P'], 0.75), (9, 5, C['P'], 0.75)])   # blush
        return base + vis + eyes

    def visor_weather(self, weather, s, t, mode):
        """The visor as a tiny screen: rain inside it, a sun sweep, lightning, a dawn gradient, or a heartbeat."""
        out = []
        if weather == 'rain':
            if self.rng.random() < 0.18: self.vrain.append([self.rng.randrange(10), 3.6])
            keep = []
            for d in self.vrain:
                d[1] += self.dt * 3.2
                if d[1] < 6: keep.append(d); out.append([OX + 2 + d[0], OY + d[1], 0.4, 0.6, WCOL['rain'], 0.55])
            self.vrain = keep
        elif weather == 'clear':
            n = (t * 4) % 16 - 3
            for k in range(3):
                c = int(n) - k
                if 0 <= c <= 9: out += self.visor([(c, 4, WCOL['clear'], 0.45 - k * 0.13), (c, 5, WCOL['clear'], 0.3 - k * 0.09)])
        elif weather == 'storm':
            if self.rng.random() < 0.04 or t - self.bolt_t < 0.08: out += self.visor([(n, r, WCOL['storm'], 0.45) for n in range(10) for r in (4, 5)])
        elif weather == 'dawn':
            p = s.get('progress') or 0.5
            for n in range(10):
                a = 0.12 + 0.4 * p * (1 - abs(n - 4.5) / 6)
                out += self.visor([(n, 5, WCOL['dawn'], a)])
        elif mode in ('groove', 'memory') and 0 < (s.get('bpm') or 0) < 88 and s.get('level', 0) < 0.6:
            per = 60 / s['bpm']; u = (t % per) / per; n = int(u * 12) - 1        # heartbeat blip crossing the visor
            if 0 <= n <= 9: out += self.visor([(n, 4 if n % 3 == 1 else 5, C['P'], 0.5)])
        return out

    # ---------------------------------------------------------------- weather around him
    def weather_fx(self, weather, s, t, h, A, ov, ctx):
        out = []; dt = self.dt
        if weather == 'rain':
            if len(self.wparts) < 9 and self.rng.random() < 0.35:
                self.wparts.append([OX - 3 + self.rng.random() * 20, OY - 10 - self.rng.random() * 4, 0.5 + self.rng.random() * 0.4])
            keep = []
            for p in self.wparts:
                p[1] += dt * 22 * p[2]
                if p[1] < OY + 10: keep.append(p); out.append([p[0], p[1], 0.3, 1.1, WCOL['rain'], 0.32])
                elif self.rng.random() < 0.4: out.append([p[0] - 0.5, OY + 10.3, 1.2, 0.2, WCOL['rain'], 0.25])   # ripple
            self.wparts = keep
        elif weather == 'clear':
            if self.rng.random() < 0.05 + 0.1 * s.get('excite', 0): self.sparks.append([OX - 2 + self.rng.random() * 18, OY - 3 + self.rng.random() * 12, 1.0])
            keep = []
            for p in self.sparks:
                p[2] -= dt * 1.4; p[1] -= dt * 0.8
                if p[2] > 0:
                    keep.append(p); a = 0.6 * p[2]
                    out += [[p[0], p[1], 0.35, 0.35, WCOL['clear'], a], [p[0] - 0.35, p[1], 0.35, 0.35, WCOL['clear'], a * 0.5],
                            [p[0] + 0.35, p[1], 0.35, 0.35, WCOL['clear'], a * 0.5], [p[0], p[1] - 0.35, 0.35, 0.35, WCOL['clear'], a * 0.5],
                            [p[0], p[1] + 0.35, 0.35, 0.35, WCOL['clear'], a * 0.5]]
            self.sparks = keep
        elif weather == 'storm':
            if self.cloud is None: self.cloud = [(x, self.rng.random()) for x in range(-1, 17)]
            drift = (t * 0.6) % 1
            for x, r in self.cloud:
                out.append([OX + x - drift, OY - 6 + (r > 0.6), 1, 1, C['dim'], 0.5])
                if r > 0.3: out.append([OX + x - drift, OY - 5, 1, 1, '#2A2440', 0.55])
            big = h['punch'] or (h['kick'] and s.get('level', 0) > 0.85 and A > 0.55)
            if big and t - self.bolt_t > 1.2:
                self.bolt_t = t; bx = self.rng.choice((OX - 2, OX + 16)); y = OY - 5; pts = []
                while y < OY + 10: pts.append((bx, y)); bx += self.rng.choice((-1, 0, 1)); y += 1
                self.bolt = pts; ov.append(('flash', (WCOL['storm'], 0.22)))
            if self.bolt and t - self.bolt_t < 0.13:
                out += [[x, y, 0.6, 1, C['B'], 0.95] for x, y in self.bolt]
        elif weather == 'dawn':
            prog = s.get('progress'); prog = 0.5 if prog is None else clamp(prog)
            col = C['dim'] if prog < 0.35 else C['P'] if prog < 0.8 else C['B']; w = 4 + 14 * prog
            out.append([OX + 7 - w / 2, OY + 10.6, w, 0.35, col, 0.25 + 0.6 * prog])
        return out

    # ---------------------------------------------------------------- modes
    def m_groove(self, body, var, s, t, eye, h, A):
        k = s.get('kick', 0); ph = s.get('phase', 0); mv = self.mv('groove')
        if mv == 'bob':                                        # body dips into the feet on the kick (overlap, never a gap)
            body = self.warp(body, lambda x, y: (x, y + (round(0.4 * k * A * 5) / 5 if y < OY + 8 else 0)))
        elif mv == 'sway':
            sw = round(0.6 * A * math.sin(ph * math.pi * 2) * 5) / 5
            body = self.warp(body, lambda x, y: (x + sw * (1 - (y - OY) / 10), y))
        elif mv == 'steptouch':
            body = self.shift(body, 1 if int(ph * 2 + (s.get('section', 0))) % 2 else 0, 0)
        elif mv == 'hop' and h['kick'] and A > 0.4:
            self.hop_n += 1
            if self.hop_n % 2 == 0: self.start_hop(t, 0.6 + 0.6 * A)
        return body, self.spectrum(s, 0.22), [], False

    def m_nod(self, body, var, s, t, eye, h, A):
        k = s.get('kick', 0); ph = s.get('phase', 0); mv = self.mv('nod')
        if var == 'loose' or mv == 'lean':
            off = max(0.0, math.cos((ph - 0.5) * 2 * math.pi)) ** 3
            lean = 0.5 * math.sin(ph * math.pi) * A
            body = self.warp(body, lambda x, y: (x + lean * (1 - (y - OY) / 10), y - (round(0.5 * off * A * 5) / 5 if y < OY + 8 else 0)))
            gapfill(body)
        elif mv == 'bounce':                                   # whole sprite up on the off-beat
            off = max(0.0, math.cos((ph - 0.5) * 2 * math.pi)) ** 4
            body = self.shift(body, 0, -round(0.6 * off * A * 5) / 5)
        else:
            nod = (0.6 + 1.2 * A) * k
            body = self.warp(body, lambda x, y: (x + (0.4 * nod if y < OY + 2 else 0), y + (nod if y < OY + 4 else nod * 0.6 if y < OY + 8 else 0)))
            if mv == 'earbob' and k > 0.3: self.flick[int(t * 2) % 2] = t + 0.08
        sub = s.get('sub', 0)
        vis = self.visor([(n, r, C['G'], 0.15 + 0.5 * sub) for n in range(10) for r in (4, 5) if sub > 0.3 and abs(n - 4.5) <= sub * 5])
        return body, vis, [], False

    def m_mosh(self, body, var, s, t, eye, h, A):
        lvl = s.get('level', 0); k = max(s.get('kick', 0), s.get('snare', 0) * 0.8); mv = self.mv('mosh')
        if lvl < 0.45: return body, [], [], False
        full = lvl > 0.8 and A > 0.72
        bang = k * (1.0 + 1.3 * A)
        shake = (self.rng.random() - 0.5) * 1.6 * k if full else 0.0
        cx = cy = 0.0
        if mv == 'swaybang': cx = 0.7 * A * math.sin(s.get('phase', 0) * math.pi)
        if mv == 'circle': a = s.get('phase', 0) * 2 * math.pi; cx, cy = 0.7 * A * math.cos(a), 0.4 * A * math.sin(a)
        if mv == 'stomp':
            if h['kick'] and A > 0.4: self.feet_f = 'splay'; self.feet_until = t + 0.12; self.dust_at(t)
            bang *= 0.5
        def f(x, y):
            yy = y - OY
            if yy >= 8: return x, y
            d = bang * (1.0 if yy < 4 else 0.55) + cy
            return x + (0.8 * bang if yy < 2 else 0) + shake + cx, y + d
        body = self.warp(body, f)
        if full:
            body = self.recolor(body, {(eye or '').upper(): C['X']})
            if k > 0.5: body += [[x - 1, y, w, hh, C['P'], 0.3] for x, y, w, hh, c, a in body[::7] if c not in (C['P'],)]
        body = [r for r in body if not self.is_eye(r, eye) and not (full and r[4] == C['X'] and OY + 4 <= r[1] <= OY + 6)]
        slit = self.visor([(n, 4, C['X'] if full else (eye or C['G']), 1.0) for n in range(3, 7)])
        return body, self.warp(slit, f) + self.dust_fx(), [], False

    def dust_at(self, t):
        for _ in range(6): self.dust.append([OX + 7 + (self.rng.random() - 0.5) * 14, OY + 10, (self.rng.random() - 0.5) * 6, -1 - self.rng.random() * 2, 1.0])

    def dust_fx(self):
        keep, out = [], []
        for p in self.dust:
            p[0] += p[2] * self.dt; p[1] += p[3] * self.dt; p[3] += 6 * self.dt; p[4] -= self.dt * 2
            if p[4] > 0: keep.append(p); out.append([p[0], p[1], 0.4, 0.4, C['B'], 0.5 * p[4]])
        self.dust = keep
        return out

    def m_break(self, body, var, s, t, eye, h, A):
        if var == 'liquid':
            bpm = s.get('bpm') or 172
            ph = t * bpm / 60
            gx, gy = round(0.7 * A * math.sin(ph * math.pi / 4) * 5) / 5, round(0.45 * math.sin(ph * math.pi / 2) * 5) / 5
            ghost = self.hist[0] if self.hist else None
            self.hist.append((gx, gy)); self.hist = self.hist[-8:]
            out = self.shift(body, gx, gy)
            trail = []
            if ghost:
                trail = [[x + ghost[0], y + ghost[1], w, hh, C['L'], 0.16] for x, y, w, hh, c, a in body if c in (C['V'], C['L'])]
            out = [r for r in out if not self.is_eye(r, eye)]
            wave = self.visor([(n, 5, C['G'], 0.35 + 0.55 * (0.5 + 0.5 * math.sin(n * 0.8 - t * 5)) * (0.4 + 0.6 * s.get('level', 0))) for n in range(10)])
            lid = self.visor([(n, 5, eye or C['G'], 1.0) for n in (4, 5)])
            return trail + out, self.shift(wave + lid, gx, gy), [], False
        # jungle / breakcore: stutter, frame holds, running feet, breakbeat ticker + m2 glitches
        if t < self.vanish_until: return [], [], [], True                      # vanished for a beat
        if self.rng.random() < 0.025 * A: return [], [], [], True              # dropped frame
        if self.hold_n > 0 and self.hold is not None:
            self.hold_n -= 1
            if self.hold_n == 0: self.jump = (self.jump[0] * 2.2, self.jump[1] * 2.2)    # lag: frozen, then jumps ahead
            return self.hold[0], self.hold[1], [], False
        if h['snare'] or h['hat']:
            self.jump = (self.rng.choice((-1, 0, 0, 1)) * A, self.rng.choice((-1, 0, 0)) * A)
            if h['snare'] and self.rng.random() < 0.35 * A: self.hold_n = self.rng.choice((2, 3))
            if h['snare'] and self.rng.random() < 0.10 + 0.12 * A: self.vanish_until = t + 0.07
        jx, jy = self.jump; self.jump = (jx * 0.7, jy * 0.7)
        jx, jy = round(jx * 5) / 5, round(jy * 5) / 5
        out = self.shift(body, jx, jy)
        bpm = s.get('bpm') or 172; bpm = bpm * 2 if bpm < 120 else bpm
        step = 60 / bpm / 4
        if t - self.step_t >= step:
            self.step_t = t
            self.tick_cells = self.tick_cells[1:] + [C['G'] if s.get('kick', 0) > 0.5 else C['P'] if s.get('snare', 0) > 0.5 else C['L'] if s.get('hat', 0) > 0.5 else None]
        tick = self.visor([(n, 5 if c == C['G'] else 4, c, 0.9) for n, c in enumerate(self.tick_cells) if c])
        self.eyehist.append((jx, jy)); self.eyehist = self.eyehist[-4:]
        ex, ey = self.eyehist[0]                                              # the visor lags behind the body (desync)
        extra = self.shift(tick, ex, ey)
        self.hold = (out, extra)
        return out, extra, [], False
