# ДЕМОН · concept + direction: ШУМ (shum) · built with Claude (Anthropic)
# >>> h17 СМЕНА (mint-pack v44): no more bare cut between ДЕМОН and ПОДМЕНЫШ (ШУМ 2026-11-03: "it just changes, something is missing").
#     Way in (every path: the lightning, ДЕЛИКАТЕС with no screen, the menu): ЗАРАЖЕНИЕ red spreads through him from one cell, rows
#     slice sideways → РАЗРЫВ on a kick every cell bursts out in 3 hard hops (some leave the window, some freeze mid-air) → ВИСИТ one beat,
#     the cloud flickers purple / red with glyph noise → СБОРКА the cells slam back in a new order as ПОДМЕНЫШ, the eyes land last.
#     Way out, by the song (ШУМ: "use the ritual animations on the way back"; Изгнать always plays one):
#       ПРИЗЫВ (metal, black / doom): the circle lights under it, the horned shadow rises and drags it down into the circle on the kicks,
#              ДЕМОН rises out of the circle's light.
#       КУЛЬТ (Death Grips, industrial, experimental hip hop): six hoods close in; each chant hit tears a strip off it, purple underneath.
#       ЯЗЫЧЕСТВО (folk / pagan / viking): the bonfire burns it off from the feet up, the red moon turns white, the antlers fall.
#       ЦИФРА (other hard: dubstep, hard techno): deleted row by row in glyphs and scanline tears, ДЕМОН re-renders.
#       ГНИЛЬ (calm songs, starved, no song): it rots off, then the burst runs backwards into ДЕМОН.
#     Death Grips law: nothing tweens. Every position is a whole cell, every change lands on a step or a kick. Inside his window only.
MORPH_STEP = 0.07                 # its own 16th when no kick leads
MORPH_RITS = ('summon', 'cult', 'pagan', 'none', 'plain')
MORPH_RU = dict(summon='ПРИЗЫВ', cult='КУЛЬТ', pagan='ЯЗЫЧЕСТВО', none='ЦИФРА', plain='ГНИЛЬ')
MORPH_SHADE = ['X.......X', 'XX.....XX', '.XXXXXXX.', 'XXXXXXXXX', 'XX.XXX.XX', 'XXXXXXXXX', '.XXXXXXX.', '..XXXXX..']   # original
MORPH_HOOD = ['.X.', 'XXX', 'X.X', 'XXX', 'XXX', 'XXX', 'X.X']                                                       # original
MORPH_ANTLER = [(0, -1), (0, -2), (-1, -2), (0, -3), (1, -3), (-1, -4), (0, -4), (-2, -4), (1, -5), (-1, -5)]       # original
MORPH_HOODS = [(0.2, OY + 4.4, 0.85), (2.6, OY + 3.6, 0.85), (16.8, OY + 3.6, 0.85), (19.0, OY + 4.4, 0.85), (5.4, OY - 2.2, 0.6), (12.6, OY - 2.2, 0.6)]
EMBER, FLAME, CORE, ROT = '#FF7A1A', '#FF9A5C', '#FFD08A', '#3A0A14'


def form_cells(form, idle, now):
    """ПОДМЕНЫШ's clean body (rim + body) and eyes, solid, from its base frame with no music / glitches / mouse; its state put back."""
    saved = dict(form.__dict__); body, eyes = [], []
    try:
        form._frame([list(r) for r in idle], {}, now, mouse=None, music=False, dance=None)
        blk, extra, ey, rim = form._parts
        body = [list(r) for r in rim] + [list(r) for r in blk]; eyes = [list(r) for r in ey]
    except Exception as e: log(f'hurt: СМЕНА body error: {e!r}')
    finally: form.__dict__.update(saved)
    solid = lambda L: [[x, y, w, h, c, 1.0] for x, y, w, h, c, a in L if a > 0.05]
    return solid(body), solid(eyes)


def _cell_key(r): return (round(r[0] * 2), round(r[1] * 2))


class Morph:
    """one transition. kind 'in' (ДЕМОН → ПОДМЕНЫШ, src = his frame, dst = its body + eyes) or 'out' (src = its body + eyes,
    dst = his live frame each call, rit = the ritual). frame(now, sn, live) -> (rects, ov, done)."""
    def __init__(self, kind, src, dst=None, t0=0.0, eyes=None, rit='plain', infect=True, music=False, seed=None, eye_col=None, why=''):
        self.kind, self.t0, self.rit, self.music, self.why = kind, t0, rit if rit in MORPH_RITS else 'none', music, why
        self.rng = random.Random(seed if seed is not None else int(t0 * 1000) & 0xFFFFFF)
        self.src = [list(r) for r in src if r[5] > 0.05]; self.dst = [list(r) for r in (dst or [])]
        self.eyes = [list(r) for r in (eyes or [])]; self.eye_col = eye_col
        self.kprev = 0.0; self.kick_t = -9.0; self.done = False; self.T1 = None if infect else t0; self.T2 = None
        self.bx, self.by = OX + 7, OY + 5
        r = self.rng
        if kind == 'in':
            seed_c = r.choice(self.src) if self.src else [self.bx, self.by]
            self.order = sorted(range(len(self.src)), key=lambda i: abs(self.src[i][0] - seed_c[0]) + abs(self.src[i][1] - seed_c[1]) + r.random() * 2.5)
            self.parts = [self._particle(c) for c in self.src]
            self.arrive = r.sample(range(len(self.dst)), len(self.dst))
        else:
            self.sink = 0; self.sink_t = -9.0; self.sunk = None; self.strips = None; self.torn = []; self.clear_t = None
            self.burn = None; self.burn_t = -9.0; self.burnt = None; self.parts = [self._particle(c) for c in self.src]

    def _particle(self, c):
        r = self.rng; cx, cy = c[0] + c[2] / 2, c[1] + c[3] / 2
        dx, dy = cx - self.bx + r.uniform(-1.5, 1.5), cy - self.by + r.uniform(-1.5, 1.5)
        n = math.hypot(dx, dy) or 1.0; roll = r.random()
        dist = r.uniform(12, 18) if roll < 0.15 else r.uniform(3, 8)          # some leave the window
        return dict(c=c, dx=dx / n, dy=dy / n, dist=dist, frozen=0.15 <= roll < 0.30)   # some freeze after the first hop

    def _kick(self, now, sn):
        v = (sn or {}).get('kick', 0) or 0
        hit = v >= 0.5 and v > self.kprev + 0.2; self.kprev = v
        if hit: self.kick_t = now
        return hit

    def _at(self, p, hop):
        h = min(hop, 1) if p['frozen'] else hop
        c = p['c']; k = p['dist'] * h / 3
        return [round(c[0] + p['dx'] * k), round(c[1] + p['dy'] * k), c[2], c[3]]

    # ------------------------------------------------------------ way in
    def _in(self, now, sn):
        e = now - self.t0; hit = self._kick(now, sn); ov = []
        if self.T1 is None and ((hit and e >= 0.40) or e >= (0.75 if self.music else 0.55)): self.T1 = now
        if self.T1 is None:                                                   # ЗАРАЖЕНИЕ
            n = int(e / MORPH_STEP); per = max(1, len(self.order) // 7); k = min(len(self.order), (n + 1) * per)
            inf = set(self.order[:k]); new = set(self.order[max(0, k - per):k])
            rr = random.Random(n * 31 + 7); rows = {rr.randint(OY - 1, OY + 9): rr.choice((-1, 1)) for _ in range(rr.randint(1, 2))}
            out, under = [], []
            for i, (x, y, w, h, c, a) in enumerate(self.src):
                sx = rows.get(int(y), 0) if i in inf else 0
                if i in new: out.append([x + sx, y, w, h, RED, 1.0])
                elif i in inf:
                    out.append([x + sx, y, w, h, INK, 1.0])
                    if 0.9 <= w <= 1.1: under += [[x + sx + dx, y + dy, w, h, RED, 0.9] for dx, dy in ((-0.4, 0), (0.4, 0), (0, -0.4), (0, 0.4))]
                else: out.append([x, y, w, h, c, a])
            return out, [('under', under)], False
        b = now - self.T1
        if b < 0.18:                                                          # РАЗРЫВ: three hard hops
            hop = int(b / 0.06) + 1
            out = [self._at(p, hop) + [RED if (i + hop) % 3 == 0 else INK, 1.0] for i, p in enumerate(self.parts)]
            if hop == 1: ov.append(('flash', (RED, 0.7)))
            return out, ov, False
        if self.T2 is None:                                                   # ВИСИТ: one beat
            hb = b - 0.18
            if (hit and hb >= 0.25) or hb >= (0.6 if self.music else 0.35): self.T2 = now
            else: return self._cloud(now, 3), [('glyphs', self._noise(now))], False
        a = now - self.T2; step = int(a / 0.05); frac = min(1.0, (step + 1) / 8)   # СБОРКА: slam back in a new order
        n = int(len(self.dst) * frac); landed = set(self.arrive[:n]); fresh = set(self.arrive[max(0, int(len(self.dst) * step / 8)):n])
        out = self._cloud(now, 3)[:int(len(self.parts) * (1 - frac))]
        out += [[x, y, w, h, RED if i in fresh else c, 1.0] for i, (x, y, w, h, c, al) in enumerate(self.dst) if i in landed]
        if a >= 0.45: out += [list(r) for r in self.eyes]                     # the eyes land last
        if step == 0: ov.append(('flash', (RED, 0.45)))
        if a >= 0.55: self.done = True
        return out, ov, self.done

    def _cloud(self, now, hop, cols=None):
        st = int((now - self.t0) / 0.08); cols = cols or (VIOLET, RED, INK)
        return [self._at(p, hop) + [cols[(i * 7 + st) % len(cols)], 1.0] for i, p in enumerate(self.parts)]

    def _noise(self, now):
        rr = random.Random(int(now / 0.08)); pts = [self._at(p, 3) for p in self.parts] or [[self.bx, self.by, 1, 1]]
        return [(q[0], q[1] - 1, rr.choice(GLYPHS), 0.8, RED) for q in rr.sample(pts, min(5, len(pts)))]

    # ------------------------------------------------------------ way out
    def _src(self): return [list(r) for r in self.src] + [list(r) for r in self.eyes]

    def _out(self, now, sn, live):
        e = now - self.t0; hit = self._kick(now, sn) if self.music else False
        live = [list(r) for r in (live or [])]
        return getattr(self, '_' + self.rit if self.rit != 'none' else '_digital')(now, e, hit, live)

    def _beat(self, now, hit, every, gap=0.25):
        """a step lands on the kick, or on its own clock without one."""
        last = getattr(self, '_bt', -9.0)
        if (hit and now - last >= gap) or now - last >= every: self._bt = now; return True
        return False

    def _summon(self, now, e, hit, live):
        out, under, ov = [], [], []
        cx, cy = OX + 7, OY + 10.3; st = int(e / 0.08)
        glow = 1.0 if now - self.kick_t < 0.1 else 0.75
        dim = 1.0 if self.sunk is None else max(0.0, 1 - int((now - self.sunk) / 0.25) / 3)     # the circle goes out in 3 steps
        n = min(44, (st + 1) * 7)
        for i in range(n):
            a = 2 * math.pi * i / 44
            under.append([cx + 9.5 * math.cos(a) - 0.3, cy + 1.5 * math.sin(a) - 0.2, 0.6, 0.4, RED, 0.75 * glow * dim])
            if i % 2 == 0: under.append([cx + 6.5 * math.cos(a) - 0.2, cy + 1.0 * math.sin(a) - 0.15, 0.4, 0.3, PINK, 0.55 * glow * dim])
        for i in range(min(8, st)):
            a = 2 * math.pi * (i + 0.5) / 8; under.append([cx + 8 * math.cos(a) - 0.3, cy + 1.25 * math.sin(a) - 0.3, 0.6, 0.6, RED, 0.5 * glow * dim])
        for i in range(min(5, max(0, st - 2))):                               # candles
            a = 2 * math.pi * i / 5 - math.pi / 2; x, y = cx + 9.5 * math.cos(a), cy + 1.5 * math.sin(a)
            fl = random.Random(st * 5 + i).random()
            out += [[x - 0.2, y - 1.0, 0.4, 0.9, BONE, 0.9 * dim], [x - 0.2, y - 1.5, 0.4, 0.5, EMBER if fl > 0.4 else CORE, 0.95 * dim]]
        if e >= 0.6:                                                          # the shadow rises in 3 snaps, sinks back in 3
            up = min(3, int((e - 0.6) / 0.15) + 1)
            if self.sunk is not None: up = max(0, 3 - int((now - self.sunk) / 0.15))
            sc = 1.7; top = OY + 9 - len(MORPH_SHADE) * sc - 8 * up / 3
            if up:
                for yy, row in enumerate(MORPH_SHADE):
                    for xx, ch in enumerate(row):
                        if ch == 'X': under.insert(0, [cx - 4.5 * sc + xx * sc, top + yy * sc, sc, sc, '#0A0610', 0.85])
                ey = top + 4 * sc
                under += [[cx - 4.5 * sc + k * sc + 0.3, ey + 0.3, sc - 0.6, sc - 0.6, RED, 0.6 + 0.4 * glow] for k in (2, 6)]
        ground = OY + 10
        if self.sunk is None:
            if e >= 1.0 and self._beat(now, hit, 0.4):                        # dragged down, 2 rows a kick
                self.sink += 2; ov.append(('flash', (RED, 0.5)))
                if self.sink >= 12: self.sunk = now; log('hurt: СМЕНА ПРИЗЫВ: it is under')
            for x, y, w, h, c, a in self._src():
                y2 = y + self.sink
                if y2 + h <= ground: out.append([x, y2, w, h, RED if ground - 1 <= y2 + h <= ground and self.sink else c, a])
            return out, [('under', under)] + ov, False
        rows = int((now - self.sunk) / 0.07) * 2; edge = ground + 1 - rows       # he rises out of the light, bottom up
        for x, y, w, h, c, a in live:
            if y >= edge: out.append([x, y, w, h, BONE if y < edge + 2 else c, a])
        if edge < OY - 4 and now - self.sunk > 0.6: self.done = True
        return out, [('under', under)] + ov, self.done

    def _cult(self, now, e, hit, live):
        out, under, ov, gl = [], [], [], []
        if self.strips is None:
            ys = sorted({int(r[1]) for r in self._src() + live})
            lo, hi = (min(ys), max(ys)) if ys else (OY, OY + 10)
            self.strips = [(y, y + 2) for y in range(lo, hi + 1, 2)]; self.rng.shuffle(self.strips)
        shown = min(6, int(e / 0.15) + 1)
        if self.clear_t is not None: shown = max(0, 6 - int((now - self.clear_t) / 0.1))
        lit = now - self.kick_t < 0.12
        for i, (x0, y0, sc) in enumerate(MORPH_HOODS[:shown]):
            for yy, row in enumerate(MORPH_HOOD):
                for xx, ch in enumerate(row):
                    if ch == 'X': under.append([x0 + xx * sc, y0 + yy * sc, sc, sc, '#120E18', 0.95])
            under.append([x0 + sc, y0 + 2 * sc, sc, sc * 0.6, RED, 1.0 if lit and self.clear_t is None else 0.45])
        if self.clear_t is None and e >= 1.0 and len(self.torn) < len(self.strips) and self._beat(now, hit, 0.35, 0.22):
            self.torn.append((self.strips[len(self.torn)], now)); ov.append(('flash', (RED, 0.35)))
            if len(self.torn) == len(self.strips): self.clear_t = now; log('hurt: СМЕНА КУЛЬТ: torn off')
        gone = lambda y: any(a <= y < b for (a, b), _ in self.torn)
        for x, y, w, h, c, a in self._src():
            if not gone(int(y)): out.append([x, y, w, h, c, a])
        for (a_, b_), t in self.torn:                                         # the torn strip flies up in hops, then rises as chant glyphs
            u = now - t
            if u < 0.18:
                hop = int(u / 0.06) + 1
                out += [[x, y - 2 * hop, w, h, RED if hop == 1 else c, al] for x, y, w, h, c, al in self._src() if a_ <= int(y) < b_]
            elif u < 0.7:
                rr = random.Random(a_ * 13); gl += [(rr.uniform(OX, OX + 13), a_ - 6 - int((u - 0.18) / 0.1), rr.choice(GLYPHS), 0.7, PINK) for _ in range(3)]
        out = [r for r in live if gone(int(r[1]))] + out                       # purple underneath
        if self.clear_t is not None and now - self.clear_t > 0.8: self.done = True
        return out, [('under', under), ('glyphs', gl)] + ov, self.done

    def _pagan(self, now, e, hit, live):
        out, under, ov = [], [], []
        st = int(e / 0.1); grow = min(3, int(e / 0.2) + 1) / 3
        if self.burnt is not None: grow = max(0, 3 - int((now - self.burnt) / 0.2)) / 3
        rr = random.Random(st)
        for x in range(-1, 16):                                               # the bonfire behind it
            mid = 1 - abs(x - 7) / 9; hgt = int((3 + 12 * mid * (0.6 + 0.4 * rr.random())) * grow)
            for yy in range(hgt):
                f = yy / max(1, hgt)
                if rr.random() < 0.12 and f > 0.4: continue
                col = CORE if abs(x - 7) < 3 and f < 0.45 else EMBER if f < 0.5 else RED if f < 0.82 else '#5A0E1E'
                under.append([OX + x - 0.5, OY + 9.6 - yy, 1, 1, col, (0.55 if f < 0.2 else 0.8) * (1 - f * 0.5)])
        for x0, hh in ((0, 9), (18.6, 8)):                                    # standing stones
            under += [[x0, OY + 10 - hh, 1.4, hh, '#3A3450', 0.95], [x0, OY + 10 - hh, 1.4, 0.5, '#6E6787', 0.9]]
        mc = RED if self.burnt is None else BONE                              # the moon: red, then white
        for yy, w in enumerate((2, 4, 5, 5, 4, 2)): under.append([16 - w / 2, OY - 18 + yy, w, 1, mc, 0.6])
        if self.burn is None and e >= 0.6: self.burn = OY + 11
        if self.burn is not None and self.burnt is None and self._beat(now, hit, 0.2, 0.15):
            self.burn -= 1
            if self.burn < OY - 3: self.burnt = now; log('hurt: СМЕНА ЯЗЫЧЕСТВО: burnt off')
        line = self.burn if self.burn is not None else OY + 12
        for x, y, w, h, c, a in live:                                         # he is under it, below the burnt line
            if y > line + 1: out.append([x, y, w, h, c, a])
        for x, y, w, h, c, a in self._src():
            if y < line: out.append([x, y, w, h, c, a])
            elif y <= line + 1: out.append([x, y, w, h, CORE if (int(x) + st) % 2 else EMBER, 1.0])
        if self.burnt is None:
            out += [[OX + 7 + rr.randint(-5, 5), line - rr.randint(1, 3), 0.4, 0.4, FLAME, 0.85] for _ in range(4)]
        fall = 0 if self.burnt is None else int((now - self.burnt) / 0.07) + 1  # its antlers fall off in hops
        if fall <= 3:
            for side, x0 in ((1, OX + 1), (-1, OX + 12)):
                out += [[x0 + dx * side, OY + dy + 3 * fall, 1, 1, '#C2C0C9', 0.95] for dx, dy in MORPH_ANTLER if OY + dy + 3 * fall < line]
        if self.burnt is not None and now - self.burnt > 0.7: self.done = True
        return out, [('under', under)] + ov, self.done

    def _digital(self, now, e, hit, live):
        out, under, gl = [], [], []
        top, bot = OY - 3, OY + 11; n = bot - top + 1
        dele = int(e / MORPH_STEP)                                            # rows deleted top → down
        rr = random.Random(int(e / MORPH_STEP) * 17 + 3)
        if dele <= n:
            cur = top + dele
            for x, y, w, h, c, a in self._src():
                if int(y) > cur: out.append([x, y, w, h, c, a])
                elif int(y) == cur: out.append([x + rr.choice((-2, 2)), y, w, h, RED, 1.0])     # the tear
            gl = [(OX + rr.uniform(0, 13), cur - 1, rr.choice(GLYPHS), 0.85, RED) for _ in range(5)]
            under.append([0, cur + 0.4, 20, 0.25, RED, 0.5])
            return out, [('under', under), ('glyphs', gl)], False
        h0 = n * MORPH_STEP + 0.25                                            # a beat of nothing but noise, then he re-renders
        if e < h0: return [], [('glyphs', [(OX + rr.uniform(0, 13), OY + rr.uniform(0, 9), rr.choice(GLYPHS), 0.6, PINK) for _ in range(6)])], False
        rows = int((e - h0) / 0.05); edge = top + rows
        for x, y, w, h, c, a in live:
            if int(y) < edge - 1: out.append([x, y, w, h, c, a])
            elif int(y) < edge + 1: out.append([x, y, w, h, '#8FD9A8', 1.0])
        if edge < bot + 1: under.append([0, edge + 0.4, 20, 0.25, '#8FD9A8', 0.4])
        if edge > bot + 2: self.done = True
        return out, [('under', under)], self.done

    def _plain(self, now, e, hit, live):
        out, ov = [], []
        if e < 1.0:                                                           # ГНИЛЬ: blocks, darker, dropping off
            n = int(e / 0.1); rr = random.Random(n)
            for i, (x, y, w, h, c, a) in enumerate(self._src()):
                d = random.Random(i * 97).random()
                if d < n / 10:
                    fall = n - int(d * 10)
                    if fall <= 2: out.append([x, y + fall, w, h, ROT, 0.9])
                    continue
                if rr.random() < 0.08 * n: x, y = math.floor(x / 2) * 2, math.floor(y / 2) * 2
                out.append([x, y, w, h, ROT if rr.random() < 0.05 * n else c, a])
            return out, ov, False
        a = e - 1.0                                                           # the burst, backwards, into him
        if a < 0.2:
            return [self._scatter(r, 3) + [VIOLET if int(a / 0.08 + i) % 2 else INK, 1.0] for i, r in enumerate(live)], ov, False
        step = int((a - 0.2) / 0.05); frac = min(1.0, (step + 1) / 8)
        for x, y, w, h, c, al in live:
            k = _cell_key([x, y]); slot = random.Random(k[0] * 131 + k[1]).random()
            eye = self.eye_col and c == self.eye_col
            if (not eye and slot < frac) or (eye and a >= 0.65): out.append([x, y, w, h, c, al])
            elif not eye: out.append(self._scatter([x, y, w, h], 3) + [VIOLET, 1.0])
        if step == 0: ov.append(('flash', ('#9D7BFF', 0.4)))
        if a >= 0.75: self.done = True
        return out, ov, self.done

    def _scatter(self, r, hop):
        k = _cell_key(r); rr = random.Random(k[0] * 7919 + k[1])
        dx, dy = r[0] - self.bx + rr.uniform(-1.5, 1.5), r[1] - self.by + rr.uniform(-1.5, 1.5); nn = math.hypot(dx, dy) or 1.0
        dist = rr.uniform(3, 8) * hop / 3
        return [round(r[0] + dx / nn * dist), round(r[1] + dy / nn * dist), r[2], r[3]]

    # ------------------------------------------------------------
    def frame(self, now, sn=None, live=None):
        if self.done: return [list(r) for r in (live or [])], [], True
        try:
            rects, ov, done = self._in(now, sn) if self.kind == 'in' else self._out(now, sn, live)
        except Exception as e:
            log(f'hurt: СМЕНА frame error: {e!r}'); self.done = True; return [list(r) for r in (live or [])], [], True
        if self.kind == 'in' and now - self.t0 > 4.0: self.done = done = True      # never stuck
        if self.kind == 'out' and now - self.t0 > 9.0: self.done = done = True
        return rects, ov, done


# ---- every way in goes through the burst (the lightning plays it on its final strike; the others in his window)
_morph_start0 = Form.start
def _morph_start(self, now, minutes, why, song=''):
    _morph_start0(self, now, minutes, why, song)
    if time.time() - getattr(self, 'morph_skip', -99) > 30: self.morph_req = now
    self.morph_skip = -99
Form.start = _morph_start


_strike_him0 = Strike._him
def _strike_him(self, cr, el, gx0, gy0, U, jolt):
    """СОШЕСТВИЕ: the final strike bursts him and it assembles out of the pieces (was: a hard swap to its frame)."""
    if self.level >= 1.0 and self.form is not None and self.final is not None:
        m = getattr(self, 'morph', None)
        if m is None and el - self.final < 0.3:
            src = [[x, y, w, h, INK if 0.9 <= w <= 1.1 else c, a] for x, y, w, h, c, a in self.p['rects']]
            body, eyes = form_cells(self.form, self.p['rects'], time.time())
            self.morph = m = Morph('in', src, body, self.final, eyes=eyes, infect=False, music=True)
            self.form.morph_skip = time.time(); log('hurt: СМЕНА in (the lightning)')
        if m is not None and not m.done:
            rects, ov, done = m.frame(el, self.snap() or {})
            if not done:
                if el - self.final < 2.2: ov = ov + [('shout', ('ЭТО БОЛЬШЕ НЕ ОН.', 1.0))]
                draw_frame(cr, rects, ov, gx0 + jolt[0], gy0 + jolt[1], U); return
    return _strike_him0(self, cr, el, gx0, gy0, U, jolt)
Strike._him = _strike_him
