

# ============================================================ in his window: nails, flinches, limp, scars, moods
class Hurt:
    """Per-desk state for everything that happens to his body inside his own window."""
    HUNT_MAX = 32.0

    def __init__(self):
        self.mem = Memory(); self.rng = random.Random()
        self.nails = []                       # stuck: dict(dx, dy, side, t, why)
        self.fly = None                       # incoming: dict(t0, arrive, row, side, dodge, preview)
        self.hunt = None                      # dict(t0, why, hits, dodges, preview, last_spawn)
        self.flinch_t = -9; self.flinch_side = 1
        self.hand_due = None                  # (t, why) after the third nail: 0.5 s of silence, then THE HAND
        self.collapse_until = 0; self.smug_until = 0; self.crash_until = 0; self.nervous_until = 0; self.fear_t = -9
        self.shout = None                     # (text, until)
        self.stabs = []; self.sudo = []
        self.nail_draw = []; self.box = None; self.prev = dict(kick=0, snare=0)
        self.song = ''; self.falling = []; self.expel_t = -99; self.blessed = False; self.motes = []

    # --- triggers
    def start_hunt(self, now, why, preview=False):
        if self.hunt or self.hand_due: return False
        self.hunt = dict(t0=now, why=why, hits=len(self.nails), dodges=0, preview=preview, last_spawn=now - 2)
        log(f'peak: ТРИ ГВОЗДЯ ({why}{", preview" if preview else ""})')
        return True

    def _stick(self, now, why, cell=None, side=None):
        if self.box is None: return
        bx, by, bw, bh = self.box
        if cell is None:
            cell = (self.rng.randint(2, 11), self.rng.randint(1, 7))
        side = side or self.rng.choice((-1, 1))
        self.nails.append(dict(dx=cell[0], dy=cell[1], side=side, t=now, why=why))
        self.flinch_t = now; self.flinch_side = side
        n = len(self.nails); log(f'hurt: nail {n} ({why})')
        if n >= 3 and self.hand_due is None:
            self.hand_due = (now + 0.55, why); self.hunt = None

    def stab(self, now, gx, gy):
        if self.box is None: return False
        bx, by, bw, bh = self.box
        if not (bx - 0.5 <= gx <= bx + bw + 0.5 and by - 0.5 <= gy <= by + bh + 0.5): return False
        self.stabs = [t for t in self.stabs if now - t < 25] + [now]
        self._stick(now, 'you', (int(gx - bx), int(gy - by)), 1 if gx > bx + bw / 2 else -1)
        return True

    def sudo_fail(self, now):
        self.sudo = [t for t in self.sudo if now - t < 90] + [now]
        self._stick(now, 'sudo')
        self.shout = ('ОТКАЗАНО.', now + 1.0)

    def pull(self, now, gx, gy):
        best = None
        for i, x, y in self.nail_draw:
            d = math.hypot(gx - x, gy - y)
            if d < 1.8 and (best is None or d < best[0]): best = (d, i)
        if best is None: return False
        n = self.nails.pop(best[1])
        self.falling.append([n, now]); self.flinch_t = now; self.flinch_side = -n['side']
        log(f'hurt: you pulled a nail out ({len(self.nails)} left)')
        if len(self.nails) < 3 and self.hand_due and now < self.hand_due[0]: self.hand_due = None; log('hurt: hand called off')
        return True

    def take_hand(self, now):
        if self.hand_due and now >= self.hand_due[0]:
            why = self.hand_due[1]; self.hand_due = None; return why
        return None

    def silence(self, now):
        return self.hand_due is not None

    def after_hand(self, outcome, now, song):
        self.hand_due = None                                                 # nails that came in while it held him go with it
        self.mem.d['last_hand'] = now; self.mem.d['hands'] = self.mem.d.get('hands', 0) + 1
        for n in self.nails: self.falling.append([n, now])
        self.nails = []
        if outcome == 'rescued':
            self.mem.d['rescues'] = self.mem.d.get('rescues', 0) + 1
            self.mem.scar('hand-escaped', self.rng.randint(3, 10), self.rng.randint(2, 6), song)
        else:
            self.collapse_until = now + 4.5
            self.mem.scar('hand', self.rng.randint(3, 10), self.rng.randint(1, 6), song)
            self.mem.scar('hand', self.rng.randint(3, 10), self.rng.randint(1, 6), '')
        log(f'hurt: after the hand: {outcome}')

    def expel(self, now):
        """ПОДМЕНЫШ leaves him: its dark copy rips upward, he collapses."""
        self.expel_t = now; self.collapse_until = now + 5.5; self.shout = ('…ЧТО ЭТО БЫЛО', now + 7.0)
        self.mem.scar('changeling', self.rng.randint(3, 10), self.rng.randint(1, 6), self.song)

    def track_changed(self, now, song):
        if self.smug_until > now:                                          # cocky for the song, then he crashes
            self.smug_until = 0; self.crash_until = now + 20; log('hurt: smug is over, he crashes')
        self.hunt = None; self.fly = None; self.song = song
        for n in self.nails: self.falling.append([n, now])
        self.nails = []
        self.blessed = False
        g = self.mem.grudge(song)
        if g:
            self.nervous_until = now + 6; log(f'hurt: nervous, this song hurt him {g}x')

    def covered(self, now):
        """a window just slid over his corner"""
        if self.mem.afraid(now) and now - self.fear_t > 30:
            self.fear_t = now; log('hurt: flinch (a window over him, the hand is still on his mind)')

    def busy(self):
        return bool(self.hunt or self.hand_due or self.fly)

    # --- the nail hunt, driven by the ear
    def tick(self, now, sn, playing):
        H = self.hunt
        if self.fly and now >= self.fly['arrive']:
            f = self.fly; self.fly = None
            if f['dodge']:
                if H: H['dodges'] += 1
                self.falling.append([dict(dx=20, dy=f['row'] - OY, side=f['side'], t=now, why='miss', fly=True), now])
                log('hurt: he dodged a nail')
            else:
                self._stick(now, 'song' if not (H and H['preview']) else 'preview', (self.rng.randint(2, 11), max(1, min(7, f['row'] - OY))), f['side'])
        if not H: return
        if now - H['t0'] > self.HUNT_MAX:
            self.hunt = None; self.shout = ('НЕ ПОПАЛ.', now + 1.4); log('hurt: ТРИ ГВОЗДЯ: he lasted, the hunt is over'); return
        if self.fly or self.hand_due: return
        hit = False
        if H['preview']: hit = now - H['last_spawn'] > 1.4
        elif sn and playing:
            k, s_ = sn.get('kick', 0), sn.get('snare', 0)
            hit = ((k >= 0.5 and k > self.prev['kick'] + 0.2) or (s_ >= 0.5 and s_ > self.prev['snare'] + 0.2)) and sn.get('level', 0) > 0.7
            self.prev = dict(kick=k, snare=s_)
            hit = hit and now - H['last_spawn'] > 1.5
        if hit:
            H['last_spawn'] = now
            hits = len(self.nails)
            p_dodge = 0.0 if H['preview'] and H['dodges'] >= 1 else (0.5 if hits == 0 else 0.35 if hits == 1 else 0.2)
            if H['dodges'] >= 3: p_dodge = 0.0
            self.fly = dict(t0=now, arrive=now + 0.55, row=OY + self.rng.randint(1, 7), side=self.rng.choice((1, 1, -1)),
                            dodge=self.rng.random() < p_dodge)

    # --- drawing (grid units, after the dance)
    def apply(self, rects, ov, now, ev=None, eye='#8FD9A8'):
        ev = ev or {}
        body = [r for r in rects if 0.9 <= r[2] <= 1.1 and r[5] >= 0.6]
        if body:
            xs = [r[0] for r in body]; ys = [r[1] for r in body]
            self.box = (min(xs), min(ys), max(xs) + 1 - min(xs), max(ys) + 1 - min(ys))
        if ev.get('hidden'): self.nail_draw = []; return [], ov
        react = ev.get('react'); extra = []
        fl = lambda f: [[x, OY + 10 - (OY + 10 - y) * f, w, h * f, c, a] for x, y, w, h, c, a in rects]
        def shift(rr, dx, dy): return [[x + dx, y + dy, w, h, c, a] for x, y, w, h, c, a in rr]
        def eye_to(rr, dx, dy, col=None):
            return [[x + dx, y + dy, w, h, col or c, a] if (c.upper() == (eye or '').upper() or c.upper() == '#E4E0EA') and OY + 4 <= y < OY + 6 else [x, y, w, h, c, a]
                    for x, y, w, h, c, a in rr]
        if react == 'look': rects = eye_to(rects, 0, -0.6)
        elif react == 'look_down': rects = eye_to(rects, 0, 0.4)
        elif react == 'hide':
            rects = shift(fl(0.72), round(self.rng.uniform(-0.2, 0.2) * 5) / 5, 0); rects = eye_to(rects, 0.6, -0.4)
            if self.rng.random() < 0.3: self.falling.append([dict(sweat=True, x=OX + self.rng.choice((1, 12)), y=OY + 3), now])
        elif react == 'dodge':
            u = ev.get('dodge', 0); up = -2.4 * math.sin(math.pi * u); rects = shift(rects, round(-1.5 * u * 5) / 5, round(up * 5) / 5)
        elif react == 'glare': rects = [r for r in rects if not (OY + 4 <= r[1] < OY + 4.6 and (r[4].upper() == (eye or '').upper() or r[4].upper() == '#E4E0EA'))]
        elif react in ('flat', 'land'): rects = fl(0.5 if react == 'flat' else 0.8)
        elif react == 'smug': pass
        if not react:
            if now < self.collapse_until:
                v = clamp(1 - (self.collapse_until - now) / 4.5); f = 0.5 if v < 0.8 else 0.5 + 0.5 * (v - 0.8) / 0.2
                rects = fl(f); rects = [r if not (OY + 4 <= r[1] < OY + 6 and r[4].upper() == (eye or '').upper()) else r[:5] + [r[5] * (0.4 + 0.4 * (int(now * 5) % 2))] for r in rects]
            elif now < self.crash_until:
                rects = fl(0.9); rects = [r[:5] + [r[5] * 0.5] if OY + 4 <= r[1] < OY + 6 and r[4].upper() == (eye or '').upper() else r for r in rects]
            elif now < self.smug_until:                                   # half-lidded, leaning back (unused since h2)
                rects = [r for r in rects if not (OY + 4 <= r[1] < OY + 4.6 and (r[4].upper() == (eye or '').upper() or r[4].upper() == '#E4E0EA'))]
                rects = [[x + (0.4 if y < OY + 5 else 0), y, w, h, c, a] for x, y, w, h, c, a in rects]
            if now < self.nervous_until or now - self.fear_t < 0.9:
                rects = shift(rects, round(self.rng.uniform(-0.25, 0.25) * 5) / 5, 0)
                rects = eye_to(rects, (2 if int(now * 7) % 2 else -2), 0)
                if self.rng.random() < 0.2: self.falling.append([dict(sweat=True, x=OX + self.rng.choice((1, 12)), y=OY + 2), now])
        if now - self.flinch_t < 0.25:
            rects = shift(rects, -self.flinch_side * 1.0, 0); rects = eye_to(rects, 0, 0, '#E4E0EA')
        if self.silence(now):                                               # the second before the hand: everything stops
            rects = [r[:5] + [r[5] * 0.55] for r in rects]; rects = eye_to(rects, 0, -0.6, '#E4E0EA')
        n = len(self.nails)
        if n >= 1:                                                          # right ear droops
            rects = [[x + 0.4, y + 1, w, h, c, a] if y < OY + 1.5 and x >= OX + 8 and react is None else [x, y, w, h, c, a] for x, y, w, h, c, a in rects]
        if n >= 2 and int(now / 0.6) % 2:                                   # limp: he steps on the bad leg
            rects = [[x, y + (0.4 if x >= OX + 7 else 0), w, h, c, a] for x, y, w, h, c, a in rects]
        if n >= 3: rects = [r[:5] + [r[5] * (0.3 if int(now * 9) % 3 == 0 else 1)] if r[4].upper() == (eye or '').upper() else r for r in rects]
        # scars (memory), placed on his body box so they move with him
        if self.box:
            bx, by, bw, bh = self.box
            for s in self.mem.scars(now)[-6:]:
                age = (now - s['t']) / (3 * 86400); a = 0.9 * (1 - age)
                col = PINK if age < 0.3 else BONE
                x, y = bx + min(bw - 2, s['dx']), by + min(bh - 2, s['dy'])
                extra += [[x, y, 0.5, 0.5, col, a], [x + 0.5, y + 0.5, 0.5, 0.5, col, a], [x + 1, y + 1, 0.5, 0.5, col, a * 0.7]]
            # stuck nails: head outside, shaft through, a pink wound
            self.nail_draw = []
            for i, nl in enumerate(self.nails):
                x, y = bx + nl['dx'], by + nl['dy']; sd = nl['side']
                wob = 0.1 * math.sin(now * 8 + i) if now - nl['t'] < 0.6 else 0
                extra += [[x, y, 1, 1, PINK, 0.95], [x + sd * 0.8, y - 0.8 + wob, 0.5, 0.5, '#C9C3D6', 1.0],
                          [x + sd * 1.4, y - 1.4 + wob, 0.5, 0.5, '#C9C3D6', 1.0], [x + sd * 2.0 - 0.25, y - 2.2 + wob, 1.0, 0.5, BONE, 1.0]]
                self.nail_draw.append((i, x + sd * 1.2, y - 1.2))
        # the one in the air (warning glint, then it flies in from his side of the screen)
        if self.fly:
            f = self.fly; u = clamp((now - f['t0']) / (f['arrive'] - f['t0']))
            edge = OX + 17 if f['side'] > 0 else OX - 4
            if u < 0.45:
                a = 0.6 + 0.4 * (int(now * 20) % 2)
                extra += [[edge, f['row'], 0.5, 0.5, PINK, a], [edge - 0.5, f['row'] + 0.5, 0.5, 0.5, BONE, a * 0.6], [edge + 0.5, f['row'] - 0.5, 0.5, 0.5, BONE, a * 0.6]]
                rects = eye_to(rects, 2 * f['side'], 0)                       # he sees it
            else:
                v = (u - 0.45) / 0.55; tx = OX + 7 + f['side'] * 1.5; x = edge + (tx - edge) * v
                extra += [[x + f['side'] * k * 0.6, f['row'], 0.6, 0.35, BONE if k == 0 else '#C9C3D6', 1 - k * 0.2] for k in range(4)]
                extra += [[x + f['side'] * (3 + k), f['row'] + 0.1, 0.8, 0.15, BONE, 0.35 - k * 0.08] for k in range(3)]
                if f['dodge']: rects = shift(rects, 0, -round(1.6 * math.sin(math.pi * v) * 5) / 5)
        u = now - self.expel_t                                              # ПОДМЕНЫШ rips out of him, upward
        if 0 <= u < 1.2:
            extra += [[x, y - u * 14 - (OY + 10 - y) * u * 0.8, w, h * (1 + u), INK if k % 3 else RED, max(0.0, 1 - u / 1.2)] for k, (x, y, w, h, c, a) in enumerate(rects)]
            if u < 0.1: ov = ov + [('flash', (RED, 0.45))]
        # falling things: pulled nails, sweat, missed nails flying on
        keep = []
        for item in self.falling:
            nl, t0 = item; u = now - t0
            if nl.get('sweat'):
                if u < 0.8: extra.append([nl['x'] + u * 0.6, nl['y'] + u * u * 6, 0.35, 0.5, SWEAT, 0.8 * (1 - u / 0.8)]); keep.append(item)
                continue
            if nl.get('fly'):
                if u < 0.5: extra.append([OX + 7 - nl['side'] * (u * 30), OY + nl['dy'], 0.6, 0.35, BONE, 1 - u * 2]); keep.append(item)
                continue
            if u < 1.0 and self.box:
                bx, by, _, _ = self.box
                x, y = bx + nl['dx'] + nl['side'] * u * 3, by + nl['dy'] + u * u * 9
                extra += [[x, y, 0.5, 0.5, '#C9C3D6', 1 - u], [x + 0.5, y - 0.5, 0.5, 0.5, BONE, 1 - u]]
                keep.append(item)
        self.falling = keep[-30:]
        if self.blessed and react is None:                                  # after ПОСЛЕДНИЙ РУБЕЖ: gold rim, light rising off him
            gold = []
            for dx, dy in ((-0.35, 0), (0.35, 0), (0, -0.35), (0, 0.35)):
                gold += [[x + dx, y + dy, w, h, GOLD, 0.6] for x, y, w, h, c, a in rects if 0.9 <= w <= 1.1 and a > 0.6]
            ov = [('under', gold)] + ov
            if self.rng.random() < 0.12: self.motes.append([OX + self.rng.uniform(0, 14), OY + 9, now])
            self.motes = [m for m in self.motes if now - m[2] < 2.0][-20:]
            extra += [[m[0] + math.sin((now - m[2]) * 3) * 0.3, m[1] - (now - m[2]) * 6, 0.4, 0.4, GOLD_L, 0.9 * (1 - (now - m[2]) / 2.0)] for m in self.motes]
        sh = self.shout if self.shout and now < self.shout[1] else None
        if ev.get('shout'): ov = ov + [('shout', (ev['shout'], 1.0))]
        elif sh: ov = ov + [('shout', (sh[0], clamp((sh[1] - now) / 0.5)))]
        return rects + extra, ov
