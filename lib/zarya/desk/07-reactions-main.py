

class Reactions:
    """d17: ОГОНЬ (catches fire, then charcoal + smoke), СДУЛО (the drop's air pushes him off the left edge; he walks back
    into the wind). d18: МУРАШКИ (horns grow, outline bristles), КАДР (the frame freezes on the climax, letterbox + speed
    lines), СЛЕЗА (one tear runs out of the visor on a sad climax), ИСКРЫ (static arcs between the horns on fast hats), ОБИДА
    (you skipped a song mid-peak: he turns his back), louder volume at a peak = СДУЛО, rare godlike epic peak = ВОЗНЕСЕНИЕ.
    At most one per kind per song, REACT_GAP s between any two. Drawn over whatever his dance made."""
    DUR = dict(fire=8.5, blown=6.4, goose=2.8, frame=2.4, tear=4.2, spark=3.0, back=8.0)
    ASCEND_GAP = 3 * 3600

    def __init__(self):
        self.cur = None; self.last = -1e9; self.done = set(); self.key = None
        self.lvl = []; self.hot_since = None; self.rng = random.Random()
        self.hats = []; self.hot_t = -1e9; self.prog = 0.0; self.vol_up = -1e9; self.ascend_t = -1e9; self.snapshot = None

    def track_change(self, now, key):
        """d18: a song skipped in the middle of a peak (before 85 %, hot in the last 4 s) → ОБИДА on the next one."""
        skipped = self.key is not None and key is not None and 0.1 < self.prog < 0.85 and now - self.hot_t < 4
        self.song(key); self.prog = 0.0
        if skipped and not self.busy(now): self.start('back', now, 'you skipped it mid-peak')

    def song(self, key):
        if key != self.key: self.key = key; self.done = set(); self.lvl = []; self.hot_since = None

    def busy(self, now): return self.cur is not None and now - self.cur[1] < self.DUR[self.cur[0]]

    def start(self, kind, now, why):
        self.cur = (kind, now); self.last = now; self.done.add(kind); self.snapshot = None
        if kind == 'frame' and why != 'preview': self.say = ('ВОТ ОНО.', now + 2.0)                    # d23: godlike only
        log(f'react: {kind} ({why})')

    def tick(self, now, sn, epic, soft, progress):
        """decides from the ear snapshot; called while he dances to a song. Returns 'ascend' for a godlike epic peak."""
        if self.cur and not self.busy(now): self.cur = None; self.snapshot = None
        lvl = sn.get('level', 0) or 0; self.prog = progress or 0
        self.lvl = [(t, l) for t, l in self.lvl if now - t < 1.0] + [(now, lvl)]
        hat = sn.get('hat', 0) or 0
        if hat >= 0.5 and (not self.hats or self.hats[-1][1] < 0.5): self.hats.append((now, hat))
        elif self.hats and hat < 0.5: self.hats.append((now, hat))
        self.hats = [h for h in self.hats if now - h[0] < 2.0][-60:]
        drop = 0 <= now - (sn.get('drop_t', -99) or -99) < 0.4
        mx = (sn.get('max_hold', 0) or 0); ex = sn.get('excite', 0) or 0
        hype = ex > 0.9 and lvl > 0.8
        if hype or mx > 0.5: self.hot_t = now
        if epic and mx > 2.5 and self.prog > 0.5 and now - self.ascend_t > self.ASCEND_GAP * getattr(self, 'gap_mult', 1.0) and not self.cur:
            self.ascend_t = now; self.last = now; self.say = ('…СЛЫШИШЬ?', now + 2.4); log('react: ВОЗНЕСЕНИЕ (godlike moment)'); return 'ascend'
        why_ = DIRECTOR.react_gate(self, now)                                                      # d28: the director's gate
        if why_: DIRECTOR.react_wanted(self, why_, now, sn, epic, soft, lvl, ex, mx, drop); return
        self.hot_since = (self.hot_since or now) if (hype or mx > 0.5) else None
        if not soft and lvl > 0.75 and now - self.vol_up < 1.2 and 'blown' not in self.done:
            return self.start('blown', now, 'you turned it up at the peak')
        if soft and 'tear' not in self.done and self.prog > 0.55 and lvl > 0.6 and ex > 0.7:
            if self.rng.random() < 0.7: return self.start('tear', now, 'the sad part')
            self.done.add('tear')
        if epic and 'frame' not in self.done and mx > 2.0 and self.prog > 0.5:
            return self.start('frame', now, 'the climax')
        if epic and 'goose' not in self.done and drop and (sn.get('build', 0) or 0) > 0.3:
            return self.start('goose', now, 'goosebumps')
        if not soft and 'spark' not in self.done and lvl > 0.7 and ex > 0.8 and sum(1 for t, v in self.hats if v >= 0.5) >= 7:
            if self.rng.random() < 0.5: return self.start('spark', now, 'the hats are electric')
            self.done.add('spark')
        if epic and 'fire' not in self.done and self.hot_since and now - self.hot_since > 1.5 and (progress or 0) > 0.2:
            return self.start('fire', now, 'the song is on fire')
        if not epic and not soft and 'blown' not in self.done and (mx > 1.2 or (drop and lvl > 0.85)):
            if self.rng.random() < 0.6: return self.start('blown', now, 'the drop hit too hard')
            self.done.add('blown')

    def apply(self, rects, ov, now, sn, eye):
        if not self.busy(now): return rects, ov
        kind, t0 = self.cur; e = now - t0
        try: return getattr(self, '_' + kind)(rects, ov, e, sn or {}, eye or '#8FD9A8')
        except Exception as ex:
            if str(ex) != getattr(self, 'err', None): self.err = str(ex); log(f'react: frame error: {ex!r}')
            return rects, ov

    # ---- ОГОНЬ: flames climb him on the epic part, he keeps dancing unbothered; then he is charcoal, blinks, coughs smoke.
    def _fire(self, rects, ov, e, sn, eye):
        burn = 5.5
        if e < burn:
            env = min(1.0, e / 0.6) * min(1.0, (burn - e) / 0.5)
            lvl = sn.get('level', 0.7) or 0.7
            front, back = [], []
            for col in range(-2, 18):
                x = OX + col; ph = col * 1.7
                hgt = (7 + 9 * (0.5 + 0.5 * math.sin(e * 9 + ph)) * (0.6 + 0.6 * lvl)) * env
                if col in (-2, 17): hgt *= 0.5
                n = int(hgt)
                for k in range(n):
                    f = k / max(1, n); c = FLAME[min(4, int(f * 4.6))]
                    if k == n - 1 and self.rng.random() < 0.5: continue
                    cell = [x, OY + 10 - k, 1, 1, c, (0.95 - 0.35 * f) * env]
                    (back if (col in (-2, -1, 15, 16, 17) or k > 8) else front).append(cell)
                if self.rng.random() < 0.25 * env:                         # sparks
                    back.append([x + self.rng.uniform(-0.5, 0.5), OY + 10 - n - self.rng.uniform(0, 3), 0.4, 0.4, FLAME[1], 0.9])
            front = [r for r in front if self.rng.random() < 0.55]         # he shows through the fire
            return rects + front, [('under', back)] + ov
        k = min(1.0, (e - burn) / 0.3) * min(1.0, max(0.0, (self.DUR['fire'] - e) / 0.8))
        out = list(rects)
        out += [[x, y, w, h, CHAR, a * k] for x, y, w, h, c, a in rects]   # charcoal over him, fades back at the end
        if 0.9 < e - burn < 1.05 or 1.25 < e - burn < 1.4:                 # blink
            out.append([OX + 2, OY + 4, 10, 2, '#07060D', 1.0])
        else:
            out += [[OX + 4, OY + 4.4, 1, 1, '#F4EEF7', 0.9 * k], [OX + 9, OY + 4.4, 1, 1, '#F4EEF7', 0.9 * k]]
        for i in range(2):                                                 # cough: two smoke rings rise
            u = (e - burn - 0.8 - i * 0.7) / 1.6
            if 0 < u < 1: ov = ov + [('ring', (OX + 7.5 + u * 1.5, OY + 6 - u * 7, 1.2 + u * 1.6, 0.5 + u * 0.6, '#8A8499', 0.8 * (1 - u)))]
        for _ in range(3):
            if self.rng.random() < 0.5 * k:
                out.append([OX + self.rng.uniform(2, 13), OY - self.rng.uniform(0, 3), 0.6, 0.6, '#5A5463', 0.6 * k])
        return out, ov

    # ---- helpers (d18)
    @staticmethod
    def _body_col(rects):
        n = {}
        for x, y, w, h, c, a in rects:
            if a >= 0.95: n[c] = n.get(c, 0) + w * h                     # solid body pixels only (not the pink ghost layer)
        return max(n, key=n.get) if n else '#C9C3D6'

    def _horn_tips(self, rects):
        top = [r for r in rects if r[1] < OY + 2]
        if not top: top = rects
        left = min((r for r in top if r[0] < OX + 7.5), key=lambda r: r[1], default=[OX, OY])
        right = min((r for r in top if r[0] >= OX + 7.5), key=lambda r: r[1], default=[OX + 14, OY])
        return (left[0] + 0.5, left[1]), (right[0] + 0.5, right[1])

    # ---- МУРАШКИ: the hair on his neck, his way: horns grow a cell, his outline bristles with tiny spikes, then settles.
    def _goose(self, rects, ov, e, sn, eye):
        k = min(1.0, e / 0.25) * min(1.0, max(0.0, (self.DUR['goose'] - e) / 0.6))
        out = list(rects)
        if k > 0.5: out += [[x, y - 1, w, h, c, a] for x, y, w, h, c, a in rects if y < OY + 2]
        occ = {(round(x), round(y)) for x, y, w, h, c, a in rects if a > 0.3}
        col = self._body_col(rects); fl = int(e * 14) % 2
        for (cx, cy) in occ:
            if (cx + cy + fl) % 2: continue
            for dx, dy in ((-1, 0), (1, 0), (0, -1)):
                if (cx + dx, cy + dy) not in occ:
                    out.append([cx + (0.6 if dx < 0 else 1.0 if dx > 0 else 0.3) + dx * 0.6 * k - (0.4 if dx < 0 else 0),
                                cy + (0.3 if dy == 0 else -0.4 * k), 0.4, 0.4, col, 0.9 * k])
        return out, ov

    # ---- КАДР: the climax freezes like a held frame: letterbox bars, speed lines behind him, his eye at full glow.
    def _frame(self, rects, ov, e, sn, eye):
        if self.snapshot is None: self.snapshot = [list(r) for r in rects]
        k = min(1.0, e / 0.15) * min(1.0, max(0.0, (self.DUR['frame'] - e) / 0.3))
        lines = []
        for i in range(18):
            y = OY - 4 + (i * 7 % 18); ln = 4 + i % 5
            x = OX + 24 - ((e * 60 + i * 13) % 40)
            lines.append([round(x * 5) / 5, y + 0.3, ln, 0.2, '#9D7BFF' if i % 3 else '#E4E0EA', 0.45 * k])
        out = [[x, y, w, h, c, min(1.0, a * 1.15) if c == eye else a] for x, y, w, h, c, a in self.snapshot]
        return out, [('under', lines), ('letterbox', (0.85 * k,))] + ov

    # ---- СЛЕЗА: on the sad climax one tear runs out of the visor and down his body; he wipes it (a quick visor flick).
    def _tear(self, rects, ov, e, sn, eye):
        out = [[x, y, w, h, c, a * 0.55 if c == eye else a] for x, y, w, h, c, a in rects]
        if 3.0 < e < 3.2: out = [r for r in out if not (r[4] == eye and OY + 3 <= r[1] < OY + 7)]      # the wipe
        if e < 3.0:
            u = min(1.0, max(0.0, (e - 0.4) / 2.4))
            ty = OY + 6 + u * u * 3.5
            out += [[OX + 9.4, round(ty * 5) / 5, 0.6, 0.8, '#8FB0E8', 1.0], [OX + 9.6, round((ty - 0.6) * 5) / 5, 0.4, 0.6, '#B8D0F5', 0.6 * u]]
        return out, ov

    # ---- ИСКРЫ: static: a jagged violet arc jumps between his horn tips on the hats, small sparks at the tips.
    def _spark(self, rects, ov, e, sn, eye):
        k = min(1.0, e / 0.2) * min(1.0, max(0.0, (self.DUR['spark'] - e) / 0.4))
        (x0, y0), (x1, y1) = self._horn_tips(rects)
        out = list(rects); seed = int(e * 12); r = random.Random(seed)
        if (sn.get('hat', 0) or 0) >= 0.4 or seed % 3 != 0:
            n = 14
            for i in range(n + 1):
                u = i / n; x = x0 + (x1 - x0) * u; y = y0 + (y1 - y0) * u - 2.2 * math.sin(math.pi * u) + r.uniform(-0.6, 0.6)
                out.append([round(x * 5) / 5, round(y * 5) / 5, 0.4, 0.4, '#E4E0EA' if r.random() < 0.3 else '#9D7BFF', 0.95 * k])
        for tx, ty in ((x0, y0), (x1, y1)):
            for _ in range(2):
                out.append([round((tx + r.uniform(-1, 1)) * 5) / 5, round((ty - r.uniform(0, 1.2)) * 5) / 5, 0.4, 0.4, '#9D7BFF', 0.8 * k])
        return out, ov

    # ---- ОБИДА: you skipped a song he was into: he turns his back (no visor, no eye) for a few seconds, then turns around.
    def _back(self, rects, ov, e, sn, eye):
        if e > self.DUR['back'] - 0.4: return rects, ov
        col = self._body_col(rects)
        out = []
        for x, y, w, h, c, a in rects:
            if OY + 3 <= y < OY + 7 and OX + 1 <= x < OX + 13 and (c == eye or c in ('#07060D', '#0C0A14')): c = col
            out.append([x + (0.2 if e < 0.3 and int(e * 20) % 2 else 0), y, w, h, c, a])
        return out, ov

    # ---- СДУЛО: the drop's air hits him from the right: he braces, is pushed off the left edge, the wind keeps blowing, he
    #      walks back in leaning into it, visor narrowed, gets shoved back once, then straightens up and shakes it off.
    def _blown(self, rects, ov, e, sn, eye):
        ground = max((y + h for x, y, w, h, c, a in rects), default=OY + 11)
        def px(v): return round(v * 5) / 5
        def lean(rs, k):                                                   # + = top towards the right (into the wind)
            return [[x + px((ground - y) * 0.16 * k), y, w, h, c, a] for x, y, w, h, c, a in rs]
        def squint(rs):                                                    # the visor narrows to a slit against the air
            out = []
            for x, y, w, h, c, a in rs:
                if c == eye and OY + 3 <= y < OY + 7: out.append([x, y + h * 0.4, w, h * 0.4, c, a])
                else: out.append([x, y, w, h, c, a])
            return out
        def move(rs, dx, dy=0.0): return [[x + px(dx), y + px(dy), w, h, c, a] for x, y, w, h, c, a in rs]
        wind = 0.0 if e > 6.0 else min(1.0, e / 0.25) * (1.0 if e < 5.4 else (6.0 - e) / 0.6)
        streaks = []                                                       # the air itself: thin lines rushing left
        for i in range(14):
            ph = (i * 0.37) % 1.0; ln = 2.5 + (i * 7 % 5)
            x = OX + 34 - ((e * (26 + i % 4 * 6) + ph * 40) % 44)
            y = OY - 3 + (i * 5 % 14)
            streaks.append([px(x), y + 0.4, ln, 0.2, '#C9C3D6' if i % 3 else '#9D7BFF', 0.35 * wind])
        if e < 0.4:                                                        # it hits: he braces, leaning back
            out = squint(lean(rects, -min(1.0, e / 0.2) * 0.8))
        elif e < 1.15:                                                     # pushed out past the left edge
            u = (e - 0.4) / 0.75
            out = squint(lean(move(rects, -(OX + 17) * u * u, -0.8 * math.sin(math.pi * u)), -0.8))
        elif e < 1.9:                                                      # gone, only the wind
            out = []
        elif e < 5.4:                                                      # back in, leaning into it, step by step
            u = e - 1.9
            gust = max(0.0, 1 - abs(u - 2.0) / 0.35) * 1.6                 # one gust shoves him back a little
            x = -(OX + 15) + min(OX + 15, 0.9 * (u * 5.2 - math.sin(u * 7.8) * 0.9)) - gust
            step = 0.2 if int(u * 6) % 2 else 0.0                          # small, hard steps
            out = squint(lean(rects, 0.9 + 0.3 * math.sin(u * 3.1)))
            out = [[x_, y_ - (step if y_ >= ground - 2 and (x_ < OX + 7) == bool(int(u * 6) % 2) else 0), w_, h_, c_, a_]
                   for x_, y_, w_, h_, c_, a_ in move(out, min(0.0, x))]
        else:                                                              # the air drops: he straightens, shakes it off
            u = (e - 5.4) / 1.0
            out = lean(rects, 0.9 * max(0.0, 1 - u * 2))
            if 0.4 < u < 0.85: out = move(out, 0.2 if int(e * 24) % 2 else -0.2)
        return out + streaks, ov
# <<< d16 reactions


# >>> d16 grey English next to Cyrillic menu labels
EN = {'ДНЕВНИК': 'diary', 'ДЕМОН': 'demon', 'ПАМЯТЬ': 'memory', 'КИВОК': 'nod', 'МОШ': 'mosh', 'КЕНДРИК': 'kendrick',
      'РАСПАД': 'decay', 'ГРУВ': 'groove', 'ЭПОС': 'epic', 'КАВАЙ': 'kawaii', 'БРЕЙК': 'breakbeat', 'ПРИВАЛ': 'rest',
      'ТРАССА': 'highway', 'БОЛЕРО': 'bolero', 'БЕГ': 'run', 'НАПЕВ': 'hum', 'ОДЕРЖИМОСТЬ': 'possession', 'ПРИЗЫВ': 'summoning',
      'КУЛЬТ': 'cult', 'ЯЗЫЧЕСТВО': 'pagan', 'ВОЗНЕСЕНИЕ': 'ascension', 'ПОДМЕНЫШ': 'changeling', 'ПОСЛЕДНИЙ РУБЕЖ': 'last stand',
      'ОГОНЬ': 'fire', 'СДУЛО': 'blown away', 'МУРАШКИ': 'goosebumps', 'КАДР': 'freeze frame', 'СЛЕЗА': 'tear', 'ИСКРЫ': 'static', 'ОБИДА': 'offended', 'ОПЯТЬ': 'again', 'ДОЖДЬ': 'rain', 'ЯСНО': 'clear', 'ГРОЗА': 'storm',
      'РАССВЕТ': 'dawn', 'ЖИДКИЙ': 'liquid', 'ДЖАНГЛ': 'jungle', 'СВОБОДНО': 'loose', 'СОШЕСТВИЕ': 'descent',
      'ИЗГНАТЬ': 'drive out', 'ИЗГНАТЬ ПОДМЕНЫШ': 'drive it out'}
CYR = re.compile(r'[А-ЯЁа-яё][А-ЯЁа-яё-]*(?: [А-ЯЁ][А-ЯЁ-]*)*')
GREY = '#8A8499'


def en_markup(t):
    if not CYR.search(t): return None
    esc = GLib.markup_escape_text; out = ''; pos = 0
    gr = lambda x: f'<span foreground="{GREY}">{x}</span>'
    for m in CYR.finditer(t):
        if m.start() < pos: continue
        out += esc(t[pos:m.end()]); pos = m.end(); rest = t[pos:]
        if rest.startswith((' · ', ' (')) and not CYR.search(rest):        # an English tail is already there: grey it
            out += '  ' + gr(esc(rest[3:] if rest.startswith(' · ') else rest[1:])); pos = len(t); break
        if rest.startswith(' · '): out += esc(' · '); pos += 3; continue
        en = EN.get(m.group(0).upper())
        if en and en.lower() not in rest.lower(): out += '  ' + gr(esc(en))
    return out + esc(t[pos:])


def gray_menu(menu):
    for it in menu.get_children():
        if isinstance(it, Gtk.SeparatorMenuItem): continue
        lab = it.get_child()
        if isinstance(lab, Gtk.Label):
            mk = en_markup(lab.get_text())
            if mk: lab.set_markup(mk)
        sm = it.get_submenu()
        if sm: gray_menu(sm)
# <<< d16 grey English


def save_report(kind, text, snap):
    """d7: one JSON per report + one line in index.log. Returns (id, number)."""
    import json
    os.makedirs(REPORTS, exist_ok=True)
    rid = time.strftime('%Y%m%d-%H%M%S'); path = f'{REPORTS}/{rid}.json'; k = 1
    while os.path.exists(path): k += 1; path = f'{REPORTS}/{rid}-{k}.json'
    rid = os.path.basename(path)[:-5]
    n = len(glob.glob(f'{REPORTS}/*.json')) + 1
    rec = dict(id=rid, n=n, kind=kind, text=text, **snap)
    with open(path + '.tmp', 'w', encoding='utf-8') as f: json.dump(rec, f, ensure_ascii=False, indent=1)
    os.replace(path + '.tmp', path)
    now = snap.get('now') or {}
    line = ' | '.join([rid, kind, f"{now.get('title') or '-'} — {', '.join(now.get('artists') or []) or '-'}",
                       f"{now.get('mode') or '-'}{':' + now['variant'] if now.get('variant') else ''}", text.replace('\n', ' ')[:120]])
    with open(f'{REPORTS}/index.log', 'a', encoding='utf-8') as f: f.write(line + '\n')
    return rid, n


def main():
    if '--version' in sys.argv: print(VERSION); return
    # one instance only
    lock = f'{CACHE}/desk.lock'; os.makedirs(CACHE, exist_ok=True)
    import fcntl
    fd = open(lock, 'w')
    try: fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError: print('ДЕМОН is already on the desktop'); return
    css = Gtk.CssProvider()
    css.load_from_data(b'''menu, .menu { background-color: rgba(7,6,13,0.96); border: 1px solid #7B4DFF; border-radius: 0; padding: 4px 0; }
        menuitem { color: #C9C3D6; font-family: "JetBrainsMono Nerd Font", monospace; padding: 6px 14px; }
        menuitem:hover { background-color: rgba(123,77,255,0.28); color: #E4E0EA; }
        menu separator { background-color: #3A3450; min-height: 1px; margin: 3px 0; }
        window.zarya-report { background-color: #07060D; border: 1px solid #7B4DFF; }
        window.zarya-report, window.zarya-report label, window.zarya-report radiobutton label { color: #C9C3D6; font-family: "JetBrainsMono Nerd Font", monospace; font-size: 10pt; }
        window.zarya-report .rep-title { color: #E4E0EA; font-weight: bold; font-size: 15pt; letter-spacing: 3px; }
        window.zarya-report .rep-head { color: #9D7BFF; font-weight: bold; letter-spacing: 2px; margin-top: 6px; }
        window.zarya-report .rep-dim { color: #6E6787; font-size: 9pt; }
        window.zarya-report radiobutton radio { background-image: none; box-shadow: none; color: transparent; background-color: #0C0A14; border: 1px solid #5A3FB0; border-radius: 0; min-width: 10px; min-height: 10px; }
        window.zarya-report radiobutton radio:checked { background-color: #7B4DFF; border-color: #9D7BFF; -gtk-icon-source: none; }
        window.zarya-report textview, window.zarya-report textview text { background-color: #0C0A14; color: #E4E0EA; font-family: "JetBrainsMono Nerd Font", monospace; caret-color: #8FD9A8; }
        window.zarya-report .rep-text { border: 1px solid #3A3450; }
        window.zarya-report button { background-image: none; background-color: #0C0A14; color: #C9C3D6; border: 1px solid #3A3450; border-radius: 0; padding: 5px 16px; box-shadow: none; text-shadow: none; }
        window.zarya-report button:hover { border-color: #7B4DFF; color: #E4E0EA; }
        window.zarya-report button.rep-save { background-color: #7B4DFF; border-color: #9D7BFF; color: #07060D; font-weight: bold; }
        window.zarya-report button.rep-save:hover { background-color: #9D7BFF; }''')
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    w = Demon(); w.show_all()
    signal.signal(signal.SIGTERM, lambda *a: Gtk.main_quit())
    Gtk.main(); log('quit')
    if w.journal: w.journal.end(time.time(), 'quit')                       # d10


import signal
if __name__ == '__main__':
    main()
