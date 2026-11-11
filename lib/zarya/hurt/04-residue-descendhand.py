

def residue(mem, now):
    """h6: today's dead pixels after it left (cells on his body), [] otherwise."""
    r = mem.d.get('residue') or {}
    if r.get('day') != time.strftime('%F', time.localtime(now)): return []
    return r.get('cells') or []


def true_cells(rects):
    """the big demon: his own cells, rows 6-7 doubled, feet tripled, long horns."""
    body = {(int(round(x - OX)), int(round(y - OY))) for x, y, w, h, c, a in rects if 0.9 <= w <= 1.1 and a >= 0.8}
    rowmap = {}; ny = 0; out = set()
    for r in range(10):
        reps = 2 if r in (6, 7) else 3 if r in (8, 9) else 1
        rowmap[r] = (ny, reps); ny += reps
    for (x, y) in body:
        if y not in rowmap: continue
        y0, reps = rowmap[y]
        for k in range(reps): out.add((x, y0 + k + 7))
    horns = set()
    for hx in sorted({x for x, y in body if y == 0}):
        side = -1 if hx < 7 else 1
        for k in range(1, 9): horns.add((hx + side * (k // 3), 7 - k))
    return dict(cells=out | horns, horns=horns, rows=ny + 7, visor=(rowmap[4][0] + 7, rowmap[5][0] + 7))


def draw_true(cr, T, el, cx, base_y, Hpx, reveal=1.0, alpha=1.0, glow=0.0):
    Q = max(6, int(Hpx / T['rows'])); QX = int(Q * 1.25)
    x0 = cx - 7 * QX; y0 = base_y - T['rows'] * Q
    cells = T['cells']; lw = max(2, Q // 7)
    shown = {(x, y) for (x, y) in cells if (T['rows'] - y) / T['rows'] <= reveal + 0.05 * math.sin(x * 1.7)}
    cr.set_source_rgba(*rgb(INK, 0.98 * alpha))
    for (x, y) in shown: cr.rectangle(x0 + x * QX, y0 + y * Q, QX + 1, Q + 1)
    cr.fill()
    cr.set_source_rgba(*rgb(VDIM, alpha))
    for (x, y) in shown:
        if (x * 3 + y) % 5 == 0 and (x, y) not in T['horns']: cr.rectangle(x0 + x * QX + QX // 3, y0 + y * Q + Q // 3, QX // 3, Q // 3)
    cr.fill()
    cr.set_source_rgba(*rgb(BONE, 0.95 * alpha))
    for (x, y) in shown:
        if (x, y) in T['horns']: cr.rectangle(x0 + x * QX, y0 + y * Q, QX, Q); continue
        X, Y = x0 + x * QX, y0 + y * Q
        if (x - 1, y) not in shown: cr.rectangle(X, Y, lw, Q)
        if (x + 1, y) not in shown: cr.rectangle(X + QX - lw, Y, lw, Q)
        if (x, y - 1) not in shown: cr.rectangle(X, Y, QX, lw)
        if (x, y + 1) not in shown: cr.rectangle(X, Y + Q - lw, QX, lw)
    cr.fill()
    if reveal > 0.6 and glow > 0:
        vy = y0 + T['visor'][0] * Q; ex = x0 + 7 * QX
        cr.set_source_rgba(*rgb(INK, alpha)); cr.rectangle(x0 + 2 * QX, vy, 10 * QX, 2 * Q); cr.fill()
        g = cairo.RadialGradient(ex, vy + Q, 0, ex, vy + Q, Q * (3 + 5 * glow))
        g.add_color_stop_rgba(0, 1.0, 0.36, 0.54, 0.9 * alpha * glow); g.add_color_stop_rgba(1, 1.0, 0.13, 0.27, 0)
        cr.set_source(g); cr.arc(ex, vy + Q, Q * (3 + 5 * glow), 0, 2 * math.pi); cr.fill()
        cr.set_source_rgba(1, 0.95, 0.97, alpha * glow); cr.rectangle(ex - QX * 0.8, vy + Q * 0.2, QX * 1.6, Q * 1.6); cr.fill()
    return Q, x0, y0


# ============================================================ whole-screen events (h2)
class Event:
    """an overlay scene with a timeline. pet(el): hidden = the event draws him itself; otherwise the desk paints his live
    frame ON TOP of the scene (he is never lost behind the cracks / lightning)."""
    kind = ''
    dur = 9.0

    def __init__(self, W, H, pet):
        self.W, self.H, self.p = W, H, pet; self.rng = random.Random(); self.outcome = None
        self.q = max(3, round(H / 240))

    def pet(self, el): return dict(hidden=False)
    def click(self, el): return False


class HandGrab(Event):
    """THE HAND (h2): a rift opens in the top edge near him, the hand comes out of it (no arm: its wrist frays into smoke
    back to the rift), grabs him, pulls. 6 clicks on him = free. Else into the rift, then slammed back."""
    kind = 'hand'
    dur = 9.2
    NEED = 6

    def __init__(self, W, H, pet, why=''):
        super().__init__(W, H, pet)
        self.why = why; self.hand = Hand2(2.7, self.q, seed=11); self.clicks = 0; self.rescued_at = None; self.cracks = None
        side = 1 if pet['cx'] < W / 2 else -1
        self.rx = clamp(pet['cx'] + side * H * 0.35, 80, W - 80)                 # the rift in the top edge
        self.rot = math.atan2(self.rx - pet['cx'], pet['cy']) * 0.9

    def phase(self, el):
        if self.rescued_at is not None: return 'rescue'
        for name, end in (('rift', 0.8), ('descend', 2.6), ('grab', 3.0), ('struggle', 5.5), ('taken', 6.6), ('gone', 7.3), ('slam', 7.7)):
            if el < end: return name
        return 'after'

    def click(self, el):
        if self.phase(el) != 'struggle': return False
        self.clicks += 1
        if self.clicks >= self.NEED:
            self.rescued_at = el; self.outcome = 'rescued'; self.dur = el + 2.0
            log(f'hurt: THE HAND: he broke free ({self.clicks} clicks)')
        return True

    def pet(self, el):
        ph = self.phase(el)
        if ph in ('rift', 'descend'): return dict(hidden=False, react='look' if el < 1.3 else 'hide')
        if ph in ('grab', 'struggle', 'taken', 'gone'): return dict(hidden=True)
        if ph == 'slam': return dict(hidden=el < 7.65, react='flat')
        if ph == 'rescue': return dict(hidden=el - self.rescued_at < 0.25, react='land', shout='НЕ СЕГОДНЯ.' if el - self.rescued_at > 0.3 else None)
        if self.outcome is None: self.outcome = 'crushed'; log('hurt: THE HAND: taken and slammed back')
        return dict(hidden=False, react='flat')

    def hand_xy(self, el):
        p = self.p; gx, gy = self.hand.grip_offset(self.rot)
        tx, ty = p['cx'] - gx, p['cy'] - gy
        top_dist = math.hypot(self.rx - p['cx'], p['cy']) + self.hand.art.ry * self.q * 2.2
        def at(D, wob=0.0): ax, ay = self.hand.along(self.rot, D); return tx + ax + wob, ty + ay
        ph = self.phase(el)
        if ph == 'rift': return (*at(top_dist), 0.0)
        if ph == 'descend':
            u = ease(clamp((el - 0.8) / 1.8)); return (*at(top_dist * (1 - u) + 2.5 * self.q, math.sin(el * 1.4) * 6), 0.0)
        if ph == 'grab': u = (el - 2.6) / 0.4; return (*at(2.5 * self.q * (1 - u)), clamp(u * 1.6))
        if ph == 'struggle': u = (el - 3.0) / 2.5; return (*at((0.8 + 1.4 * u) * p['U'] * 1.6, math.sin(el * 23) * 3), 1.0)
        if ph == 'taken': u = (el - 5.5) / 1.1; return (*at(p['U'] * 3.6 + (u ** 2) * top_dist), 1.0)
        if ph == 'gone': return (*at(top_dist * 1.5), 1.0)
        if ph == 'slam': u = (el - 7.3) / 0.4; return (*at(top_dist * (1 - u ** 3)), 1.0)
        if ph == 'rescue':
            u = el - self.rescued_at
            if u < 0.4: return (*at(p['U'] * 2.6, math.sin(el * 60) * 6), 0.0)
            return (*at(p['U'] * 2.6 + ((u - 0.4) / 1.2) ** 2 * top_dist), 0.0)
        u = (el - 7.7) / 1.4; return (*at(u * top_dist * 0.8), 1.0)

    def draw(self, cr, el):
        W, H, p = self.W, self.H, self.p; ph = self.phase(el)
        env = min(1.0, el / 0.5) * min(1.0, max(0.0, (self.dur - el) / 0.6))
        g = cairo.RadialGradient(p['cx'], p['cy'], 10, p['cx'], p['cy'], H * 0.45)
        sh = 0.5 if ph in ('descend', 'grab', 'struggle') else 0.3
        g.add_color_stop_rgba(0, 0.02, 0.01, 0.04, sh * env); g.add_color_stop_rgba(1, 0.02, 0.01, 0.04, 0)
        cr.set_source(g); cr.paint()
        ra = clamp(el / 0.6) * clamp((self.dur - el) / 0.8)
        rift(cr, self.rx, 0, 34 * self.q * (0.4 + 0.6 * ra), 9 * self.q * ra, el, ra)
        x, y, curl = self.hand_xy(el)
        if ph != 'gone': self.hand.draw(cr, x, y, curl, el, env, rot=self.rot)
        held = ph in ('grab', 'struggle', 'taken') and el >= 2.8
        if held:
            gx, gy = self.hand.grip_offset(self.rot); px, py = x + gx, y + gy
            kick = (int(el * 9) % 2) * 0.4
            rr = [[a, b + (kick if b >= OY + 8 and (int(a) % 2) else 0), c, d, e, f] for a, b, c, d, e, f in p['rects']]
            gx0 = px - (OX + 7) * p['U']; gy0 = py - (OY + 5) * p['U']
            if ph == 'struggle':
                cr.set_source_rgba(*rgb(BONE, 0.9)); cr.rectangle(round(px - 2), round(py + 4 * p['U']), 3, max(1, round(p['cy'] + 6 * p['U'] - py - 4 * p['U']))); cr.fill()
                tx_ = max(px, 9 * p['U'] + 20)
                _shout(cr, 'ПОМОГИ', tx_ + 7 * p['U'], py - 2 * p['U'], int(2.6 * p['U']), 0.6 + 0.4 * (int(el * 4) % 2))
                for k in range(self.NEED):
                    on = k < self.clicks
                    cr.set_source_rgba(*rgb(PINK if on else BONE, 0.95 if on else 0.4))
                    cr.rectangle(round(tx_ + 7 * p['U'] - self.NEED * 7 + k * 14), round(py + 1.2 * p['U']), 10, 6); cr.fill()
            draw_pet(cr, rr, gx0, gy0, p['U'])
            for dy in (2.2, 6.0):                                             # its fingers across him
                cr.set_source_rgba(*rgb(SKIN_D, 0.98)); cr.rectangle(round(gx0 + (OX - 1) * p['U']), round(gy0 + (OY + dy) * p['U']), round(16 * p['U']), round(1.4 * p['U'])); cr.fill()
                cr.set_source_rgba(*rgb(SKIN_LL, 0.9)); cr.rectangle(round(gx0 + (OX - 1) * p['U']), round(gy0 + (OY + dy) * p['U']), round(16 * p['U']), 1); cr.fill()
        if ph == 'after':
            if self.cracks is None:
                r = self.rng; self.cracks = []
                for k in range(9):
                    a = r.uniform(0, 2 * math.pi); pts = [(p['cx'], p['cy'])]; L = r.uniform(80, 260)
                    for j in range(6): pts.append((pts[-1][0] + math.cos(a + r.uniform(-0.5, 0.5)) * L / 6, pts[-1][1] + math.sin(a + r.uniform(-0.5, 0.5)) * L / 6))
                    self.cracks.append(pts)
            fa = clamp(1 - (el - 7.7) / 1.4)
            if el - 7.7 < 0.12: cr.set_source_rgba(1, 1, 1, 0.5); cr.arc(p['cx'], p['cy'], 140, 0, 2 * math.pi); cr.fill()
            for pts in self.cracks:
                cr.move_to(*pts[0])
                for pt in pts[1:]: cr.line_to(*pt)
                cr.set_source_rgba(*rgb(PINK, 0.5 * fa)); cr.set_line_width(5); cr.stroke_preserve()
                cr.set_source_rgba(*rgb(BONE, 0.95 * fa)); cr.set_line_width(1.5); cr.stroke()
        if ph == 'rescue' and el - self.rescued_at < 0.12: cr.set_source_rgba(*rgb(RED, 0.25)); cr.paint()


class DescendHand(Event):
    """ARCHIVED in h3 (not triggered; kept for later). СОШЕСТВИЕ v3: the bottom cracks open under him; the hand climbs out of the crack, takes him and drags him under.
    The crack pulses. Then something climbs back out in his shape: ПОДМЕНЫШ. outcome 'taken' → the desk starts the form."""
    kind = 'descend'
    dur = 11.5

    def __init__(self, W, H, pet, why=''):
        super().__init__(W, H, pet)
        r = self.rng; px = max(2, round(H / 480)); self.px = px
        self.cracks = []
        for x0 in [clamp(pet['cx'] / W, 0.03, 0.97)] + [r.uniform(0.05, 0.95) for _ in range(6)]:
            x = x0 * W; y = H; pts = [(x, y)]
            for _ in range(r.randint(6, 11)):
                x += r.uniform(-0.03, 0.03) * W; y -= r.uniform(0.015, 0.04) * H; pts.append((x, y))
            self.cracks.append(pts)
        self.embers = [(r.uniform(0, W), r.uniform(0.85, 1.25) * H, r.uniform(0.18, 0.35) * H, r.choice((1, 1, 2, 3)) * px, r.random() * 6) for _ in range(180)]
        self.hand = Hand2(2.5, self.q, flip=True, seed=31)
        self.rot = -0.5 if pet['cx'] < W / 2 else 0.5
        self.form = pet.get('form'); self.why = why

    def phase(self, el):
        for name, end in (('open', 1.2), ('rise', 3.8), ('grab', 4.3), ('drag', 6.3), ('below', 7.8), ('climb', 10.2), ('close', 11.5)):
            if el < end: return name
        return 'end'

    def pet(self, el):
        ph = self.phase(el)
        if ph == 'open': return dict(hidden=False, react='look_down' if el > 0.5 else None)
        if ph == 'rise': return dict(hidden=False, react='hide')
        if ph in ('close', 'end') and self.outcome is None: self.outcome = 'taken'; log('hurt: СОШЕСТВИЕ: something came back up in his shape')
        return dict(hidden=True)

    def draw(self, cr, el):
        W, H, p = self.W, self.H, self.p
        u = el / self.dur; env = min(1.0, u / 0.08) * min(1.0, max(0.0, (1 - u) / 0.12))
        if env <= 0: return
        ph = self.phase(el); px = self.px
        flare = 1.6 if ph == 'below' else 1.0
        pulse = (0.75 + 0.25 * math.sin(el * (11 if ph == 'below' else 7))) * flare
        for x0, y0, x1, y1 in ((0, 0, 0, H * 0.25), (0, 0, W * 0.16, 0), (W, 0, W * 0.84, 0)):
            g = cairo.LinearGradient(x0, y0, x1, y1); g.add_color_stop_rgba(0, 0.25 * min(1, pulse), 0.0, 0.04, 0.65 * env); g.add_color_stop_rgba(1, 0.05, 0, 0.02, 0)
            cr.set_source(g); cr.paint()
        g = cairo.LinearGradient(0, H, 0, H * 0.55)
        g.add_color_stop_rgba(0, 1.0, 0.13, 0.27, min(0.8, 0.42 * env * pulse)); g.add_color_stop_rgba(0.5, 0.6, 0.02, 0.1, 0.18 * env); g.add_color_stop_rgba(1, 0.2, 0, 0.05, 0)
        cr.set_source(g); cr.rectangle(0, H * 0.55, W, H * 0.45); cr.fill()
        grow = min(1.0, el / 1.6) * (clamp((self.dur - el) / 1.0))
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
        gx, gy = self.hand.grip_offset(self.rot); tx, ty = p['cx'] - gx, p['cy'] - gy      # palm centre when it holds him
        U = p['U']; side = 1 if p['cx'] < W / 2 else -1
        rx_, ry_ = p['cx'] + side * W * 0.13, H - H * 0.42                     # it towers beside him first, rune toward you
        sx_, sy_ = rx_ + side * W * 0.02, H + H * 0.45
        drop = 0.0
        if ph == 'drag': drop = ((el - 4.3) / 2.0) ** 1.6 * (H - p['cy'] + 14 * U)
        if ph in ('rise', 'grab', 'drag'):
            if ph == 'rise':
                v = ease(clamp((el - 1.2) / 2.4)); hx, hy = sx_ + (rx_ - sx_) * v, sy_ + (ry_ - sy_) * v; curl = 0.0; rot = self.rot * 0.4
            elif ph == 'grab':
                v = ease(clamp((el - 3.8) / 0.4)); hx, hy = rx_ + (tx - rx_) * v, ry_ + (ty - ry_) * v; curl = clamp(v * 1.2); rot = self.rot * (0.4 + 0.6 * v)
            else:
                hx, hy = tx, ty; curl = 1.0; rot = self.rot
            hy += drop or 0
            self.hand.draw(cr, hx, hy, curl, el, env, rot=rot)
            if ph in ('grab', 'drag') and el > 4.1:                           # him, in its grip, going under
                pyo = drop or 0
                rr = [[a, b + ((int(el * 10) % 2) * 0.4 if b >= OY + 8 else 0), c, d, e, f] for a, b, c, d, e, f in p['rects']]
                draw_pet(cr, rr, p['gx0'] + math.sin(el * 30) * 2, p['gy0'] + pyo, U)
                for dy in (2.4, 6.2):
                    cr.set_source_rgba(*rgb(SKIN_D, 0.98)); cr.rectangle(round(p['gx0'] + (OX - 1) * U), round(p['gy0'] + pyo + (OY + dy) * U), round(16 * U), round(1.4 * U)); cr.fill()
                    cr.set_source_rgba(*rgb(SKIN_LL, 0.9)); cr.rectangle(round(p['gx0'] + (OX - 1) * U), round(p['gy0'] + pyo + (OY + dy) * U), round(16 * U), 1); cr.fill()
                if ph == 'drag': _shout(cr, 'НЕТ НЕТ НЕТ', p['cx'] + 8 * U, p['gy0'] + (OY - 3) * U, int(2.4 * U), 0.6 + 0.4 * (int(el * 6) % 2))
            if ph == 'drag':                                                   # scratch marks where he held on
                for k in range(3):
                    x = p['cx'] - 4 * U + k * 4 * U
                    cr.set_source_rgba(*rgb(BONE, 0.7)); cr.rectangle(round(x), round(H - 3 - (el - 4.3) * 30 * U / 10), 2, round((el - 4.3) * 30 * U / 10)); cr.fill()
        if ph == 'below':                                                      # under: his eye flickers green, then red, in the crack
            v = (el - 6.3) / 1.5
            col = '#8FD9A8' if v < 0.45 else RED
            if int(el * 8) % 3: cr.set_source_rgba(*rgb(col, 0.9)); cr.rectangle(round(p['cx'] - U), H - 2 * U, 2 * U, U); cr.fill()
            if v > 0.6:
                for k in range(5):
                    _text(cr, self.rng.choice(GLYPHS), p['cx'] + self.rng.uniform(-60, 60), H - self.rng.uniform(10, 80), 14, RED, 0.6)
        if ph in ('climb', 'close') and self.form is not None:                # something climbs out in his shape
            v = clamp((el - 7.8) / 2.0)
            step = math.floor(v * 7) / 7                                       # jerky, a few frames missing
            rise = (1 - step) * (H - p['gy0'] - OY * U)
            rects, ov = self.form.frame([r[:] for r in p['rects']], {}, 3000 + el, mouse=None, music=False)
            if ph == 'climb' and v < 0.95 and self.rng.random() < 0.15: rise += self.rng.choice((-1, 1)) * U
            if ph == 'close': ov = [o for o in ov if o[0] != 'shout'] + [('shout', ('ЭТО БОЛЬШЕ НЕ ОН.', clamp((11.4 - el) / 0.5)))]
            draw_frame(cr, rects, ov, p['gx0'], p['gy0'] + rise, U)
            if ph == 'climb' and 9.6 < el < 9.75: cr.set_source_rgba(*rgb(RED, 0.25)); cr.paint()
