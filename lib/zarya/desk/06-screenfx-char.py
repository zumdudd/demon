

class ScreenFX(Gtk.Window):
    """d8: a click-through, focus-less overlay over the whole monitor for one event, then it destroys itself."""
    def __init__(self, kind, geo, abort, done, dur=None, ev_obj=None, painter=None):
        super().__init__(type=Gtk.WindowType.POPUP)
        vis = self.get_screen().get_rgba_visual()
        if vis: self.set_visual(vis)
        self.set_app_paintable(True); self.kind = kind; self.abort = abort; self.done = done; self.dur = dur or (9.0 if kind == 'descend' else 13.0)
        self.ev = ev_obj                                                        # d10: zarya-hurt event (d11: hand / descend v3 / shadow)
        self.painter = painter                                                  # d11: paints him in front of the scene
        self.W, self.H = geo.width, geo.height; self.move(geo.x, geo.y); self.set_default_size(self.W, self.H); self.resize(self.W, self.H)
        self.connect('draw', self._draw)
        self.connect('realize', lambda *_: self.input_shape_combine_region(cairo.Region()))
        r = random.Random(); self.motes = new_motes(r, self.W, self.H) if kind != 'descend' else new_descend(r, self.W, self.H)
        self.t0 = time.time(); self.show_all(); self.input_shape_combine_region(cairo.Region())
        GLib.timeout_add(33 if self.ev is not None else 66, self._tick)

    def _draw(self, w, cr):
        el = time.time() - self.t0
        hidden = False
        if self.ev is None: draw_screen(cr, self.kind, self.W, self.H, el, self.dur, self.motes)
        else:
            cr.set_operator(cairo.OPERATOR_SOURCE); cr.set_source_rgba(0, 0, 0, 0); cr.paint(); cr.set_operator(cairo.OPERATOR_OVER)
            try: self.ev.draw(cr, el); hidden = self.ev.pet(el).get('hidden')
            except Exception as e:
                if not getattr(self, '_err', None): self._err = repr(e); log(f'screen: {self.kind} frame error: {e!r}')
        if self.painter and not hidden:
            try: self.painter(cr)
            except Exception as e:
                if not getattr(self, '_perr', None): self._perr = repr(e); log(f'screen: painter error: {e!r}')

    def _tick(self):
        if self.ev is not None: self.dur = self.ev.dur
        if time.time() - self.t0 > self.dur or self.abort():
            if self.abort(): log(f'screen: {self.kind} stopped (fullscreen / game)')
            self.destroy(); self.done(); return False
        self.queue_draw(); return True


def new_motes(r, W, H):
    px = max(2, round(H / 480))                                            # pixel size: 3 px at 1440p
    return [(r.uniform(0, W), r.uniform(0.55, 1.15) * H, r.uniform(0.03, 0.11) * H, r.choice((1, 1, 2, 2, 3)) * px, r.random() * 6,
             r.random() < 0.7) for _ in range(240)]


def new_descend(r, W, H):
    """d9: cracks along the bottom edge, embers, claw shapes for both sides."""
    px = max(2, round(H / 480))
    cracks = []
    for _ in range(7):
        x = r.uniform(0.05, 0.95) * W; y = H; pts = [(x, y)]
        for _ in range(r.randint(6, 11)):
            x += r.uniform(-0.03, 0.03) * W; y -= r.uniform(0.015, 0.04) * H; pts.append((x, y))
        cracks.append(pts)
    embers = [(r.uniform(0, W), r.uniform(0.85, 1.25) * H, r.uniform(0.18, 0.35) * H, r.choice((1, 1, 2, 3)) * px, r.random() * 6) for _ in range(180)]
    claws = [(side, r.uniform(0.45, 0.62) * H, [r.uniform(0.8, 1.2) for _ in range(4)]) for side in (-1, 1)]
    return dict(px=px, cracks=cracks, embers=embers, claws=claws)


def draw_descend(cr, W, H, el, dur, D):
    """СОШЕСТВИЕ (original): the bottom of the screen cracks open with red light, embers fly up, shadow claws reach in from
    both edges and pull back, a red pulse. The desktop stays visible underneath."""
    u = el / dur; env = min(1.0, u / 0.1) * min(1.0, max(0.0, (1 - u) / 0.25))
    if env <= 0: return
    px = D['px']; pulse = 0.75 + 0.25 * math.sin(el * 7.0)
    for x0, y0, x1, y1 in ((0, 0, 0, H * 0.25), (0, 0, W * 0.16, 0), (W, 0, W * 0.84, 0)):
        g = cairo.LinearGradient(x0, y0, x1, y1); g.add_color_stop_rgba(0, 0.25 * pulse, 0.0, 0.04, 0.65 * env); g.add_color_stop_rgba(1, 0.05, 0, 0.02, 0)
        cr.set_source(g); cr.paint()
    g = cairo.LinearGradient(0, H, 0, H * 0.55)
    g.add_color_stop_rgba(0, 1.0, 0.13, 0.27, 0.42 * env * pulse); g.add_color_stop_rgba(0.5, 0.6, 0.02, 0.1, 0.18 * env); g.add_color_stop_rgba(1, 0.2, 0, 0.05, 0)
    cr.set_source(g); cr.rectangle(0, H * 0.55, W, H * 0.45); cr.fill()
    grow = min(1.0, el / 1.6)
    for pts in D['cracks']:
        n = max(2, int(len(pts) * grow))
        for lw, col, al in ((18 * px / 3, (1.0, 0.13, 0.27), 0.30 * pulse), (5 * px / 3, (1.0, 0.36, 0.54), 0.95), (2, (1.0, 0.92, 0.92), 0.95)):
            cr.move_to(*pts[0])
            for q in pts[1:n]: cr.line_to(*q)
            cr.set_source_rgba(*col, al * env); cr.set_line_width(lw); cr.stroke()
    for x, y0, sp, sz, ph in D['embers']:
        y = H * 1.05 - ((H * 1.25 - y0) + sp * el) % (H * 0.85)               # they keep coming up
        if y < H * 0.2 or y > H: continue
        a = env * (0.5 + 0.4 * math.sin(el * 5 + ph)) * min(1.0, (y - H * 0.2) / (H * 0.25))
        cr.set_source_rgba(1.0, 0.45 + 0.3 * math.sin(ph), 0.1, a); cr.rectangle(round(x + math.sin(el * 2 + ph) * sz * 4), round(y), sz, sz); cr.fill()
    reach = math.sin(math.pi * min(1.0, max(0.0, (el - 1.0) / (dur - 2.6)))) * env
    reach *= 0.92 + 0.08 * math.sin(el * 11)                                # they twitch
    q = 4 * px
    for side, cy, lens in D['claws']:
        inward = 1 if side < 0 else -1; base = 0 if side < 0 else W
        cr.set_source_rgba(0.03, 0.01, 0.04, 0.9 * env)                       # the hand at the edge
        cr.rectangle(0 if side < 0 else W - q * 6, cy - H * 0.11, q * 6, H * 0.22); cr.fill()
        for i, L in enumerate(lens):
            fy = cy + (i - 1.5) * H * 0.05; length = W * 0.22 * L * reach
            steps = int(length / q); bend = (1 if i < 2 else -1) * 0.5
            for k in range(steps):
                w = q * (4.2 - 3.4 * k / max(1, steps)); x = base + inward * (q * 6 + k * q); yy = fy + (k / max(1, steps)) ** 2 * H * 0.06 * bend
                cr.set_source_rgba(0.03, 0.01, 0.04, 0.9 * env); cr.rectangle(round(x - (q if inward < 0 else 0)), round(yy - w / 2), q, max(q, round(w))); cr.fill()
            if steps:
                tip = base + inward * (q * 6 + steps * q); yy = fy + H * 0.06 * bend
                cr.set_source_rgba(1.0, 0.13, 0.27, 0.9 * env); cr.rectangle(round(tip - (q if inward < 0 else 0)), round(yy - q / 2), q, q); cr.fill()


def draw_screen(cr, kind, W, H, el, dur, motes):
    if kind == 'descend':
        cr.set_operator(cairo.OPERATOR_SOURCE); cr.set_source_rgba(0, 0, 0, 0); cr.paint(); cr.set_operator(cairo.OPERATOR_OVER)
        return draw_descend(cr, W, H, el, dur, motes)
    return draw_ascend(cr, kind, W, H, el, dur, motes)


def draw_ascend(cr, kind, W, H, el, dur, motes):
    """ВОЗНЕСЕНИЕ (original): the screen dims at the edges, a warm dusk rises from the bottom, a pale horizon line and a low sun,
    hundreds of small pixel lights drift up, then everything fades. The desktop stays visible underneath."""
    cr.set_operator(cairo.OPERATOR_SOURCE); cr.set_source_rgba(0, 0, 0, 0); cr.paint(); cr.set_operator(cairo.OPERATOR_OVER)
    u = el / dur
    env = min(1.0, u / 0.15) * min(1.0, max(0.0, (1 - u) / 0.22))
    if env <= 0: return
    for x0, y0, x1, y1 in ((0, 0, 0, H * 0.22), (0, H, 0, H * 0.78), (0, 0, W * 0.12, 0), (W, 0, W * 0.88, 0)):     # dim edges
        g = cairo.LinearGradient(x0, y0, x1, y1); g.add_color_stop_rgba(0, 0.03, 0.02, 0.05, 0.55 * env); g.add_color_stop_rgba(1, 0.03, 0.02, 0.05, 0)
        cr.set_source(g); cr.paint()
    hy = H * 0.72
    g = cairo.LinearGradient(0, H, 0, H * 0.40)                            # dusk from below
    g.add_color_stop_rgba(0, 1.0, 0.48, 0.10, 0.30 * env); g.add_color_stop_rgba(0.45, 0.95, 0.60, 0.70, 0.16 * env); g.add_color_stop_rgba(1, 0.29, 0.19, 0.54, 0)
    cr.set_source(g); cr.rectangle(0, H * 0.40, W, H * 0.60); cr.fill()
    rise = min(1.0, u / 0.6)
    cr.save(); cr.rectangle(0, 0, W, hy); cr.clip()                         # low sun above the horizon
    sy = hy + H * 0.10 * (1 - rise)
    g = cairo.RadialGradient(W / 2, sy, 0, W / 2, sy, H * 0.22)
    g.add_color_stop_rgba(0, 0.97, 0.84, 0.55, 0.30 * env); g.add_color_stop_rgba(1, 0.97, 0.84, 0.55, 0)
    cr.set_source(g); cr.arc(W / 2, sy, H * 0.22, 0, 2 * math.pi); cr.fill(); cr.restore()
                                                                            # d16: no horizon line (shum: the line across the screen)
    for x, y0, sp, sz, ph, pale in motes:                                   # the lights going up
        y = y0 - sp * el
        if y < -10: continue
        a = env * (0.35 + 0.35 * math.sin(el * 2.2 + ph)) * min(1.0, max(0.0, (y0 - y) / (H * 0.06)))
        if y < H * 0.25: a *= max(0.0, y / (H * 0.25))
        if a < 0.02: continue
        xx = x + math.sin(el * 0.7 + ph) * sz * 3
        cr.set_source_rgba(*((0.96, 0.93, 0.97) if pale else (0.95, 0.60, 0.70)), a)
        cr.rectangle(round(xx), round(y), sz, sz); cr.fill()


# >>> d16 reactions (mint-pack v23; d17 / v24: ШОК removed, СДУЛО = pushed off the edge): ДЕМОН reacts to the song like a side character, short and rare
REACT_GAP = 75                                                    # seconds between two reactions, any kind
OX, OY = 3, 4                                                     # sprite origin in zarya-daemon's grid (as in zarya-hurt)
FLAME = ('#FFF1B0', '#FFC23A', '#FF7A1A', '#FF2D55', '#9E1238')
CHAR = '#26222B'
