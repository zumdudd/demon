import os, json, math, time, random, hashlib, re
import cairo

VERSION = 'h22'
HOME = os.path.expanduser('~')
MEM = f'{HOME}/.local/share/zarya/demon/memory.json'
OX, OY = 3, 4                       # sprite origin in zarya-daemon's grid (same as zarya-music)
INK, BONE, VIOLET, VDIM, PINK, RED, SWEAT = '#07060D', '#E4E0EA', '#7B4DFF', '#2A1F44', '#FF5C8A', '#FF2244', '#8FB0E8'
GLYPHS = 'ЖЯЮЩШЦФЪЬЫЭБДЛПИГЗҐЄЇѢѲѴ'
_log = None


def set_logger(f):
    global _log
    _log = f


def log(msg):
    if _log: _log(msg)


def rgb(h, a=1.0): return (int(h[1:3], 16) / 255, int(h[3:5], 16) / 255, int(h[5:7], 16) / 255, a)
def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def ease(u): u = clamp(u); return u * u * (3 - 2 * u)


def is_hard(mode, var, weather, peak, calm):
    """Same routing as zarya-music: hard songs get ОДЕРЖИМОСТЬ / СОШЕСТВИЕ / ТРИ ГВОЗДЯ, soft ones КАТАРСИС."""
    soft = mode in calm or (weather in ('rain', 'dawn') and mode in ('groove', 'nod', 'epic', 'kawaii'))
    if soft or peak == 'rift': return False
    return peak in ('possess', 'nails') or mode in ('mosh', 'grips') or (mode == 'break' and var == 'jungle') or weather == 'storm'


def route(key, peak):
    """hard-song peak for this song: song rule > fixed pick per song (half possession, half nails)."""
    if peak in ('possess', 'nails', 'rift'): return peak
    return ('possess', 'nails')[int(hashlib.md5((key or '').encode()).hexdigest(), 16) % 2]


# ============================================================ memory: scars, fear, grudges
class Memory:
    def __init__(self):
        self.d = dict(scars=[], songs={}, last_hand=0, hands=0, rescues=0, form=None, forms=0, last_descent=0)
        try: self.d.update(json.load(open(MEM, encoding='utf-8')))
        except (OSError, ValueError): pass

    def save(self):
        try:
            os.makedirs(os.path.dirname(MEM), exist_ok=True)
            with open(MEM + '.tmp', 'w', encoding='utf-8') as f: json.dump(self.d, f, ensure_ascii=False, indent=1)
            os.replace(MEM + '.tmp', MEM)
        except OSError as e: log(f'hurt: memory not saved: {e}')

    def scar(self, kind, dx, dy, song=''):
        now = time.time()
        self.d['scars'] = [s for s in self.d['scars'] if now - s['t'] < 3 * 86400][-11:] + [dict(t=now, kind=kind, dx=dx, dy=dy, song=song)]
        if song: self.d['songs'][song] = self.d['songs'].get(song, 0) + 1
        self.save()

    def scars(self, now):
        return [s for s in self.d['scars'] if now - s['t'] < 3 * 86400]

    def grudge(self, song):
        return self.d['songs'].get(song, 0) if song else 0

    def afraid(self, now):
        return now - self.d.get('last_hand', 0) < 86400




def _capsule(cells, p0, p1, r0, r1):
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0; L2 = dx * dx + dy * dy or 1e-6; rm = max(r0, r1)
    for cx in range(int(math.floor(min(x0, x1) - rm)), int(math.ceil(max(x0, x1) + rm)) + 1):
        for cy in range(int(math.floor(min(y0, y1) - rm)), int(math.ceil(max(y0, y1) + rm)) + 1):
            px, py = cx + 0.5, cy + 0.5
            u = clamp(((px - x0) * dx + (py - y0) * dy) / L2)
            qx, qy = x0 + dx * u - px, y0 + dy * u - py
            if qx * qx + qy * qy <= (r0 + (r1 - r0) * u) ** 2: cells.add((cx, cy))


def _disc(cells, cx0, cy0, rx, ry=None):
    ry = ry or rx
    for cx in range(int(cx0 - rx - 1), int(cx0 + rx + 2)):
        for cy in range(int(cy0 - ry - 1), int(cy0 + ry + 2)):
            if ((cx + 0.5 - cx0) / rx) ** 2 + ((cy + 0.5 - cy0) / ry) ** 2 <= 1: cells.add((cx, cy))


def _text(cr, txt, x, y, px, col, a, bold=True):
    if a <= 0.02: return
    try:
        import gi
        gi.require_version('Pango', '1.0'); gi.require_version('PangoCairo', '1.0')
        from gi.repository import Pango, PangoCairo
        lay = PangoCairo.create_layout(cr)
        lay.set_font_description(Pango.FontDescription.from_string(f'JetBrainsMono Nerd Font {"Bold " if bold else ""}{int(px)}px'))
        lay.set_text(txt, -1); w, h = lay.get_pixel_size()
        cr.move_to(round(x - w / 2), round(y - h / 2)); cr.set_source_rgba(*rgb(col, a)); PangoCairo.show_layout(cr, lay)
    except Exception:
        cr.select_font_face('monospace', 0, 1); cr.set_font_size(px); cr.move_to(x, y); cr.set_source_rgba(*rgb(col, a)); cr.show_text(txt)


def _shout(cr, txt, x, y, px, a):
    _text(cr, txt, x + 2, y, px, PINK, 0.7 * a); _text(cr, txt, x, y, px, BONE, a)


def draw_pet(cr, rects, gx0, gy0, U, alpha=1.0, flat=1.0, dx=0, dy=0, inv=False):
    """his rects (grid units) at a screen position: gx0, gy0 = screen px of grid (0, 0)."""
    for x, y, w, h, c, a in rects:
        if flat != 1.0: y = OY + 10 - (OY + 10 - y) * flat; h *= flat
        a *= alpha
        if a < 0.04: continue
        col = rgb(c, a)
        if inv: col = (1 - col[0], 1 - col[1], 1 - col[2], a)
        x0, y0 = round(gx0 + (x + dx) * U), round(gy0 + (y + dy) * U)
        cr.set_source_rgba(*col); cr.rectangle(x0, y0, max(1, round(gx0 + (x + dx + w) * U) - x0), max(1, round(gy0 + (y + dy + h) * U) - y0)); cr.fill()



# ============================================================ the hand (h2, original): no arm, Hand-of-God mood
# Five fingers too long with one joint too many, long black nails, ash skin lit from the top-left, an original bind-rune
# carved in the palm (Thurisaz thorn + Naudiz slash on one stave, a hook at the top: our own combination), the wrist
# frays into smoke where it comes out of a rift or a crack. It moves slowly and smoothly; the fingers twitch on their own.
SKIN, SKIN_L, SKIN_LL, SKIN_D, SKIN_DD = '#38343E', '#4E4857', '#6E6777', '#221F28', '#0E0C12'
SKIN_M1, SKIN_M2, KNUCKLE, VEIN = '#302C36', '#423D4A', '#827A8C', '#1A1720'
NAIL, NAIL_G = '#050407', '#5E5868'
RUNE_O, RUNE_I = '#2A0308', '#7E0C1E'
F_THETA = (24, 64, 88, 110, 134)                 # thumb low on one side, four long fingers
F_LEN = (0.8, 1.2, 1.34, 1.24, 1.0)


def _shade(cells):
    """organic shading: light from the top-left, a deep rim bottom-right, mottled dead skin in between."""
    out = {}
    for (x, y) in cells:
        if (x - 1, y) not in cells or (x, y - 1) not in cells: c = SKIN_LL
        elif (x + 1, y) not in cells or (x, y + 1) not in cells: c = SKIN_DD
        elif (x - 2, y - 1) not in cells or (x - 1, y - 2) not in cells: c = SKIN_L
        elif (x + 2, y + 1) not in cells or (x + 1, y + 2) not in cells or (x + 2, y + 2) not in cells: c = SKIN_D
        else:
            h = _hash(x // 2, y // 2, 5); c = SKIN_M1 if h < 0.3 else SKIN_M2 if h > 0.8 else SKIN
        out[(x, y)] = c
    return out


def _hash(x, y, k=0): return ((x * 73856093) ^ (y * 19349663) ^ (k * 83492791)) % 1000 / 1000


class HandArt2:
    def __init__(self, s):
        self.s = s; self.rx, self.ry = 9.8 * s, 10.2 * s
        self.grip = (0.0, self.ry + 9.5 * s)
        self.cache = {}
        self.bases = []
        for th in F_THETA:
            a = math.radians(th); self.bases.append((self.rx * 0.78 * math.cos(a), self.ry * 0.82 * math.sin(a) + (2.5 * s if th < 40 else 0)))
        self._palm(); self.rune = self._rune()

    def _palm(self):
        s = self.s; cells = set()
        _disc(cells, 0, 0, self.rx, self.ry)
        _capsule(cells, (0, -self.ry * 0.4), (0, -self.ry - 9 * s), 6.4 * s, 5.0 * s)
        wr = -self.ry - 1.5 * s; alpha = {}
        for (x, y) in list(cells):                                           # the wrist frays: fewer cells, fainter, toward its end
            if y < wr:
                v = (wr - y) / (8 * s)
                if _hash(x, y) < v * 0.9: cells.discard((x, y)); continue
                alpha[(x, y)] = max(0.15, 1 - v)
        creases = set()
        for k, (yy, w) in enumerate(((-0.55, 0.7), (0.05, 0.85), (0.5, 0.6))):     # palm creases
            for t in range(int(self.rx * 1.6 * w)):
                x = -self.rx * 0.8 * w + t; y = yy * self.ry + math.sin(t * 0.35 + k) * 0.8 * s
                creases.add((int(x), int(y)))
        groups = {}
        for p, c in _shade(cells).items(): groups.setdefault((c, round(alpha.get(p, 1.0), 1)), []).append(p)
        veins = set()
        for k, x0 in enumerate((-2.2 * s, 0.6 * s, 2.8 * s)):                          # veins up the wrist, under the skin
            x = x0
            for t in range(int(10 * s)):
                y = -self.ry * 0.3 - t; x += math.sin(t * 0.5 + k * 2) * 0.45
                veins.add((int(x), int(y)))
        self.palm = (groups, (creases | veins) & cells)

    def _rune(self):
        s = self.s; core = set(); edge = set()
        strokes = [((0, -5.2), (0, 5.2)), ((0, -2.2), (2.7, 0)), ((2.7, 0), (0, 2.2)), ((-2.5, -0.8), (2.6, 2.6)), ((0, -5.2), (-2.3, -3.1))]
        for (a, b) in strokes:
            p0, p1 = (a[0] * s, a[1] * s + 0.6 * s), (b[0] * s, b[1] * s + 0.6 * s)
            _capsule(core, p0, p1, 0.5 * s, 0.5 * s); _capsule(edge, p0, p1, 0.95 * s, 0.95 * s)
        return core, edge - core

    def finger(self, i, curl):
        k = int(round(clamp(curl) * 8)); key = (i, k)
        if key in self.cache: return self.cache[key]
        c = k / 8; s = self.s; th = F_THETA[i]
        x, y = self.bases[i]; r = 2.35 * s * (1.12 if i == 0 else 1.0)
        cells, crease, nail, glint, knuck = set(), set(), set(), set(), set()
        lens = [L * s * F_LEN[i] for L in (5.0, 4.6, 4.0, 3.4)]
        d = th
        for j, L in enumerate(lens):
            d = th + (5 if j % 2 else -6) * (1 - c) + c * (90 - th) * (0.5 + 0.42 * j) + (c * 16 * j if th >= 90 else -c * 16 * j)
            ang = math.radians(d); nx, ny = x + L * math.cos(ang), y + L * math.sin(ang); r1 = r * 0.88
            _capsule(cells, (x, y), (nx, ny), r, r1); _disc(cells, nx, ny, r1 * 1.18)
            knuck.add((int(math.floor(nx - r1 * 0.5)), int(math.floor(ny - r1 * 0.5)))); knuck.add((int(math.floor(nx - r1 * 0.5)) + 1, int(math.floor(ny - r1 * 0.5))))
            for t in range(-int(r1) - 1, int(r1) + 2):
                crease.add((int(math.floor(nx - math.sin(ang) * t * 0.9)), int(math.floor(ny + math.cos(ang) * t * 0.9))))
            x, y, r = nx, ny, r1
        ang = math.radians(d); ex, ey = x + 4.2 * s * math.cos(ang + 0.15), y + 4.2 * s * math.sin(ang + 0.15)
        _capsule(nail, (x - 0.4 * s * math.cos(ang), y - 0.4 * s * math.sin(ang)), (ex, ey), 1.3 * s, 0.12 * s)
        glint = {p for p in nail if (p[0] - 1, p[1]) not in nail and (p[0], p[1] - 1) not in nail}
        cells -= nail
        groups = {}
        for p, col in _shade(cells).items(): groups.setdefault(col, []).append(p)
        out = (groups, (crease & cells) | {('k',) + p for p in knuck & cells}, nail, glint, (ex, ey))
        self.cache[key] = out
        return out


class Hand2:
    """Placed hand: palm (+ rune), five staggered fingers, smoke from the frayed wrist. Origin = palm centre, fingers to +y
    (flip: to -y). Rotation turns the whole hand."""
    def __init__(self, s, q, flip=False, seed=7):
        self.art = HandArt2(s); self.s, self.q, self.flip = s, q, flip
        self.rng = random.Random(seed); self.twitch = [(-9.0, 0.0)] * 5; self.smoke = []

    def grip_offset(self, rot=0.0):
        gx, gy = self.art.grip[0] * self.q, (-self.art.grip[1] if self.flip else self.art.grip[1]) * self.q
        return gx * math.cos(rot) - gy * math.sin(rot), gx * math.sin(rot) + gy * math.cos(rot)

    def along(self, rot, D):
        dy = 1 if self.flip else -1
        return -dy * D * math.sin(rot), dy * D * math.cos(rot)

    def wrist(self, x, y, rot):
        """screen point where the wrist frays out (smoke source)."""
        ax, ay = self.along(rot, (self.art.ry + 9 * self.s) * self.q); return x + ax, y + ay

    def _cells(self, cr, cells, col, a=1.0):
        q = self.q; fy = -1 if self.flip else 1
        cr.set_source_rgba(*rgb(col, a))
        for (x, y) in cells: cr.rectangle(x * q, (y * fy - (1 if self.flip else 0)) * q, q, q)
        cr.fill()

    def draw(self, cr, x, y, curl, el, alpha=1.0, rot=0.0, smoke=True, glow=1.0):
        q = self.q
        for i in range(5):                                                   # each finger twitches on its own
            t0, amt = self.twitch[i]
            if el - t0 > 0.35 and self.rng.random() < 0.012: self.twitch[i] = (el, self.rng.uniform(-0.25, 0.3))
        if smoke:
            wx, wy = self.wrist(x, y, rot); bx, by = self.along(rot, 1.0)          # unit vector back toward its source
            for _ in range(3):
                off = self.rng.uniform(-4.5, 4.5) * self.s * q
                self.smoke.append([wx + off * math.cos(rot), wy + off * math.sin(rot), el, self.rng.uniform(40, 110), self.rng.choice((1, 1, 2)) * q])
            keep = []
            for p in self.smoke:
                u = el - p[2]
                if u > 1.4: continue
                keep.append(p)
                d = p[3] * u; wob = math.sin(u * 6 + p[0]) * q * 2
                cr.set_source_rgba(0.06, 0.04, 0.09, 0.75 * alpha * (1 - u / 1.4))
                cr.rectangle(round(p[0] + bx * d + wob * by), round(p[1] + by * d - wob * bx), p[4], p[4]); cr.fill()
            self.smoke = keep[-260:]
        cr.save(); cr.translate(round(x), round(y)); cr.rotate(rot)
        cr.push_group()
        groups, creases = self.art.palm
        for (c, a), ps in groups.items(): self._cells(cr, ps, c, a)
        self._cells(cr, creases, VEIN, 0.75)
        core, edge = self.art.rune
        if self.flip: core, edge = {(x, -y - 1) for x, y in core}, {(x, -y - 1) for x, y in edge}     # the rune reads the same way up
        self._cells(cr, edge, RUNE_O, 0.95); self._cells(cr, core, RUNE_I, 1.0)
        pulse = (0.35 + 0.35 * math.sin(el * 2.4)) * glow
        self._cells(cr, core, '#FF2244', pulse)
        lo = max(p[1] for p in core); dx_ = sorted(core)[len(core) // 2][0]
        dr = (el * 0.6) % 1                                                   # a slow drip out of the carving
        self._cells(cr, {(dx_, int(lo + 1 + dr * 4 * self.s))}, '#9E1026', 0.9 * (1 - dr))
        for i in range(5):
            t0, amt = self.twitch[i]; tw = amt * math.sin(math.pi * clamp((el - t0) / 0.35))
            fg, cr_, nail, glint, tip = self.art.finger(i, clamp(curl + tw + 0.04 * math.sin(el * 1.3 + i)))
            for c, ps in fg.items(): self._cells(cr, ps, c)
            self._cells(cr, [p for p in cr_ if len(p) == 2], SKIN_DD, 0.8)
            self._cells(cr, [p[1:] for p in cr_ if len(p) == 3], KNUCKLE, 0.9); self._cells(cr, nail, NAIL); self._cells(cr, glint, NAIL_G, 0.8)
        cr.pop_group_to_source(); cr.paint_with_alpha(alpha); cr.restore()


def rift(cr, x, y, w, h, el, a=1.0, down=True, seed=3):
    """a jagged tear (top edge: opens downward), dark inside, red rim."""
    if a <= 0.02 or w < 2: return
    r = random.Random(seed); n = 9
    pts = [(x - w / 2 + w * k / n, y) for k in range(n + 1)]
    low = [(x - w / 2 + w * k / n, y + (1 if down else -1) * h * (0.35 + 0.65 * math.sin(math.pi * k / n)) * (0.75 + 0.25 * r.random())) for k in range(n + 1)]
    cr.move_to(*pts[0])
    for p in low: cr.line_to(*p)
    cr.line_to(*pts[-1]); cr.close_path()
    cr.set_source_rgba(0.02, 0.0, 0.03, 0.97 * a); cr.fill_preserve()
    cr.set_source_rgba(1.0, 0.13, 0.27, (0.55 + 0.2 * math.sin(el * 5)) * a); cr.set_line_width(3); cr.stroke()


def draw_frame(cr, rects, ov, gx0, gy0, U, alpha=1.0):
    """his frame (grid rects + the overlays that matter for him: under, glyphs, shout, flash) at a screen position."""
    for kind, a in ov:
        if kind == 'under':
            for x, y, w, h, c, al in a:
                if al * alpha < 0.04: continue
                cr.set_source_rgba(*rgb(c, al * alpha)); cr.rectangle(round(gx0 + x * U), round(gy0 + y * U), max(1, round(w * U)), max(1, round(h * U))); cr.fill()
    draw_pet(cr, rects, gx0, gy0, U, alpha)
    for kind, a in ov:
        if kind == 'glyphs':
            for x, y, ch, al, col in a: _text(cr, ch, gx0 + x * U, gy0 + y * U, max(7, int(1.4 * U)), col, al * alpha)
        elif kind == 'shout':
            _shout(cr, a[0], max(gx0 + (OX + 7) * U, len(a[0]) * 0.75 * U + 10), gy0 + (OY - 4) * U, int(2.4 * U), a[1] * alpha)
        elif kind == 'flash':
            col, al = a; r_, g_, b_, _ = rgb(col); cx, cy = gx0 + (OX + 7) * U, gy0 + (OY + 5) * U
            pat = cairo.RadialGradient(cx, cy, 4, cx, cy, 13 * U); pat.add_color_stop_rgba(0, r_, g_, b_, al * alpha); pat.add_color_stop_rgba(1, r_, g_, b_, 0)
            cr.set_source(pat); cr.arc(cx, cy, 13 * U, 0, 2 * math.pi); cr.fill()


# ============================================================ ПОДМЕНЫШ: what climbs back out of the crack
FORM_NAME = 'ПОДМЕНЫШ'
FORM_MOVES = (('contort', 'ЛОМКА'), ('tick', 'ТИК'), ('spider', 'ПАУК'), ('split', 'РАСЩЕПЛЕНИЕ'), ('rewrite', 'ПЕРЕЗАПИСЬ'), ('stare', 'ВЗГЛЯД'))
FORM_LINES = ['ЭТО БОЛЬШЕ НЕ ОН', 'Я ВИЖУ ТВОЙ КУРСОР', 'ПРОЦЕСС 1 — МОЙ', 'ОТКЛЮЧИ МЕНЯ. ПОПРОБУЙ.', 'ОН СПИТ ВНИЗУ', 'МНЕ НРАВИТСЯ ЭТА',
              'ГРОМЧЕ', 'ЗДЕСЬ ТЕСНО', 'КТО ТЫ', 'НЕ СМОТРИ ТАК', 'ЕЩЁ']


KRIK_WORDS = ['ЕЩЁ', 'ДА', 'МОЁ', 'ЖРИ', 'ГРОМЧЕ', 'ВНУТРЬ', 'ЕЩЁ']          # h7: chorus words when there are no lyrics
SWEET, BLUSH = '#FF9EC4', '#FF6FA8'                                      # h9: ПРИМАНКА
MASK_EYES = [(3, 4, 2, 2), (9, 5, 2, 2)]                                     # (x, y, w, h) from OX / OY: the right eye a cell low
MASK_PUPILS = [(3, 5), (9, 6)]
MASK_SMILE = [(3, 6), (12, 6)] + [(x, 7) for x in range(4, 12)]                # a cell too wide on the right
CRACKS = [[(3, 4), (4, 5), (5, 6)], [(10, 5), (9, 6), (9, 7)], [(6, 7), (7, 6), (8, 7)], [(4, 7), (3, 6), (2, 5)],
          [(10, 6), (11, 7), (12, 6)], [(5, 4), (6, 5), (7, 4)]]
ARC_RU = dict(smell='ЧУЕТ', wind='ЗАВОД', soul='ДУША ВОН', boom='ДЕТОНАЦИЯ', build='СБОРКА')
FLY = '#B8AFC4'
PW = 20                                                                 # the pet area is 20 cells wide (zarya-daemon W)


LOOK = dict(A='А', B='В', C='С', D='Д', E='Э', F='Ф', G='Б', H='Н', I='І', K='К', L='Л', M='М', N='И', O='О', P='Р', R='Я', S='Ѕ',
            T='Т', U='Ц', W='Ш', X='Х', Y='У')                        # h6: lyric words in Cyrillic look-alikes, some mirrored (N→И, R→Я)


def night(now):
    h = time.localtime(now).tm_hour; return h < 5                       # h6: 00:00-05:00 it is stronger
