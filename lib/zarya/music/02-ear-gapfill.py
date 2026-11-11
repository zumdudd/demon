

class Ear:
    """Feed it one cava frame (16 values 0-65535) at a time; read .snap (a dict) any time."""
    def __init__(self):
        self.reset()

    def reset(self):
        self.t0 = None; self.n = 0
        self.ok = Onset(0.11, 1.5, 2.0); self.os_ = Onset(0.09, 1.6, 1.6); self.oh = Onset(0.05, 1.6, 1.4)
        self.ov = Onset(0.09, 1.6, 1.2); self.osub = Onset(0.25, 1.4, 3.0)
        self.env = []                       # (t, onset strength) for tempo
        self.ev = []                        # (t, kind) onsets in the last 6 s
        self.ref = None; self.lvl_s = 0; self.short = []; self.med = []
        self.sub_ref = 40.0; self.hi_hist = []; self.subr_hist = []
        self.pulse = dict(kick=0.0, snare=0.0, hat=0.0, vocal=0.0, punch=0.0)
        self.last_t = None; self.prev_lv = None; self.hish_hist = []; self.excite = 1.0; self.bpm = 0.0; self.phase = 0.0; self.next_tempo = 0
        self.auto = None; self.auto_since = 0; self.cand = None; self.cand_since = 0
        self.lvh = []; self.next_lvh = 0; self.build = 0.0; self.drop_t = -99; self.section = 0; self.sec_ref = None; self.sec_off = 0
        self.max_hold = 0.0; self.chaos = 0.0
        self.beat = 0.0                     # m3: beat steadiness 0-1 (speech ≈ 0)
        self.snap = dict(active=False)

    def track_changed(self):
        self.excite = 1.0; self.ref = None; self.auto = None; self.cand = None; self.env = []; self.ev = []
        self.bpm = 0.0; self.hi_hist = []; self.subr_hist = []; self.hish_hist = []
        self.lvh = []; self.build = 0.0; self.section = 0; self.sec_ref = None; self.max_hold = 0.0; self.beat = 0.0

    def feed(self, v, t):
        if self.t0 is None: self.t0 = t
        dt = 0.016 if self.last_t is None else max(0.001, min(0.2, t - self.last_t)); self.last_t = t
        sub = db(v[0] + v[1] * 0.6)
        low = db(v[1] + v[2] + v[3])
        snr = db(v[4] + v[5] + v[11] + v[12] + v[13])
        hi = db(v[14] + v[15])
        mid = db(sum(v[6:10]))
        tot_lin = sum(v)
        L = db(tot_lin)
        # loudness relative to this track's own peak (24 dB window, peak slowly forgets: 3 dB / 10 s)
        if self.ref is None: self.ref = L
        self.ref = max(L, self.ref - 0.3 * dt)
        self.lvl_s = L if L > self.lvl_s else self.lvl_s + (L - self.lvl_s) * min(1, dt / 0.25)
        level = max(0.0, min(1.0, (self.lvl_s - (self.ref - 24)) / 24))
        quiet = tot_lin < 400
        # onsets
        k = self.ok.feed(low, t); s = self.os_.feed(snr, t); h = self.oh.feed(hi, t); vo = self.ov.feed(mid, t)
        sb = self.osub.feed(sub, t)
        decay = lambda x, tau: x * math.exp(-dt / tau)
        P = self.pulse
        P['kick'] = decay(P['kick'], 0.13); P['snare'] = decay(P['snare'], 0.11); P['hat'] = decay(P['hat'], 0.05)
        P['vocal'] = decay(P['vocal'], 0.12); P['punch'] = decay(P['punch'], 0.16)
        self.sub_ref = max(sub, self.sub_ref - 0.4 * dt)
        sub_lvl = max(0.0, min(1.0, (sub - (self.sub_ref - 18)) / 18))
        if not quiet:
            if k: P['kick'] = min(1.0, 0.5 + k / 8); self.ev.append((t, 'k'))
            if s: P['snare'] = min(1.0, 0.5 + s / 8); self.ev.append((t, 's'))
            if h: P['hat'] = 1.0; self.ev.append((t, 'h'))
            if vo: P['vocal'] = 1.0; self.ev.append((t, 'v'))
            if sb and sub_lvl > 0.7 and v[0] > 0.18 * max(1, tot_lin): P['punch'] = 1.0; self.ev.append((t, 'p'))
        lv = [db(x) for x in v]
        if self.prev_lv is not None:
            fl = sum(max(0.0, a - b) for a, b in zip(lv, self.prev_lv))
            self.env.append((t, fl))
        self.prev_lv = lv
        cut = t - 6.0
        while self.env and self.env[0][0] < cut: self.env.pop(0)
        while self.ev and self.ev[0][0] < cut: self.ev.pop(0)
        self.subr_hist.append((v[0] + v[1]) / max(1, tot_lin)); self.subr_hist = self.subr_hist[-360:]
        self.hi_hist.append(sum(v[9:16])); self.hi_hist = self.hi_hist[-360:]
        self.hish_hist.append(sum(v[9:16]) / max(1, tot_lin)); self.hish_hist = self.hish_hist[-360:]
        # excitement: track start, drops (loud after quiet), peaks; otherwise calm down
        self.short.append(L); self.short = self.short[-30:]
        self.med.append(L); self.med = self.med[-360:]
        if len(self.med) > 120:
            s_avg = sum(self.short) / len(self.short); m_avg = sum(self.med) / len(self.med)
            if s_avg - m_avg > 5 and level > 0.7:
                if self.excite < 0.9 and t - self.drop_t > 2: self.drop_t = t                  # m2: a drop just landed
                self.excite = 1.0
        if level > 0.92: self.excite = max(self.excite, 0.75)
        self.excite *= math.exp(-dt / 5.0)
        if t >= self.next_tempo and len(self.env) > 60:
            self.next_tempo = t + 0.5; self._tempo(t)
        if self.bpm:
            per = 60.0 / self.bpm; self.phase = (self.phase + dt / per) % 1.0
            if k:
                err = self.phase if self.phase < 0.5 else self.phase - 1.0
                self.phase = (self.phase - 0.5 * err) % 1.0
        f = self.features(t)
        self._shape(t, dt, level, f, sub_lvl, quiet)
        self._classify(f, t)
        self.snap = dict(active=not quiet, t=t, level=level, excite=self.excite, sub=sub_lvl, bpm=self.bpm, phase=self.phase,
                         bars=[min(1.0, x / 26000) for x in v], quiet=quiet, auto=self.auto, build=self.build, drop_t=self.drop_t,
                         section=self.section, sec_energy=self._sec_energy(), chaos=self.chaos, max_hold=self.max_hold, beat=self.beat, **P, **f)
        return self.snap

    def _sec_energy(self):
        if not self.lvh: return 0.0
        tail = [l for tt, l in self.lvh if tt >= self.lvh[-1][0] - 8]
        return sum(tail) / len(tail)

    def _shape(self, t, dt, level, f, sub_lvl, quiet):
        """m2: sections (energy over ~8 s), builds (rising energy + denser drums), chaos, МАКС hold."""
        if t >= self.next_lvh:
            self.next_lvh = t + 0.25; self.lvh.append((t, level)); self.lvh = [x for x in self.lvh if x[0] >= t - 12]
        se = self._sec_energy()
        if self.sec_ref is None: self.sec_ref = se
        if abs(se - self.sec_ref) > 0.2:
            self.sec_off += dt
            if self.sec_off > 1.5: self.section += 1; self.sec_ref = se; self.sec_off = 0
        else: self.sec_off = 0
        if t - self.drop_t < 0.05: self.section += 1; self.sec_ref = se
        # build: level climbing over 4 s while snares / hats get denser, not yet at the top
        raw = 0.0
        pts = [x for x in self.lvh if x[0] >= t - 4]
        if len(pts) >= 10 and not quiet:
            n = len(pts); mx = sum(p[0] for p in pts) / n; my = sum(p[1] for p in pts) / n
            den = sum((p[0] - mx) ** 2 for p in pts) or 1
            slope = sum((p[0] - mx) * (p[1] - my) for p in pts) / den
            new = sum(1 for tt, kk in self.ev if kk in 's h' and tt >= t - 2); old = sum(1 for tt, kk in self.ev if kk in 's h' and t - 4 <= tt < t - 2)
            dens = clamp((new - old * 1.1) / 6)
            raw = clamp((slope - 0.03) / 0.07) * (0.45 + 0.55 * dens) * (1.0 if level < 0.93 else 0.3)
        self.build += (raw - self.build) * min(1.0, dt * (4 if raw > self.build else 1.5))
        if t - self.drop_t < 0.3: self.build = 0.0
        # chaos: dense hits + guitar wall, scaled by loudness
        dens_all = (f['kps'] + f['sps'] + 0.5 * f['hps']) / 12
        self.chaos = clamp(0.6 * clamp(dens_all) + 0.4 * clamp(f['wall'])) * clamp(level * 1.1)
        # МАКС: sitting at the track's loudest with heavy sub
        if level > 0.9 and (f['subr'] > 0.2 or f['pps'] >= 0.3 or sub_lvl > 0.75) and not quiet: self.max_hold += dt
        else: self.max_hold = max(0.0, self.max_hold - 2 * dt)

    def _tempo(self, t):
        """Autocorrelation of the spectral-flux envelope over 6 s, scored as a comb (lag, 2x, 3x), 68-190 BPM."""
        if len(self.env) < 120: return
        span = self.env[-1][0] - self.env[0][0]
        fps = (len(self.env) - 1) / span if span > 0 else 60.0
        g = [x for _, x in self.env]
        m = sum(g) / len(g); g = [x - m for x in g]
        if max(g) - min(g) < 1e-6: self.bpm = 0.0; self.beat *= 0.7; return
        def ac(L):
            L0 = int(L); fr = L - L0
            if L0 + 1 >= len(g): return 0.0
            a = sum(g[i] * g[i - L0] for i in range(L0, len(g))) / (len(g) - L0)
            b = sum(g[i] * g[i - L0 - 1] for i in range(L0 + 1, len(g))) / (len(g) - L0 - 1)
            return a * (1 - fr) + b * fr
        lo, hi = fps * 60 / 190, fps * 60 / 68
        cand = []
        L = lo
        while L <= hi:
            sc = ac(L) + 0.5 * ac(2 * L) + 0.33 * ac(3 * L)
            cand.append((sc, L)); L += 0.5
        sc, L = max(cand)
        a0 = sum(x * x for x in g) / len(g) or 1e-9                          # m3: how periodic is it at all
        self.beat = self.beat * 0.75 + 0.25 * clamp(sc / (1.83 * a0))
        if sc <= 0: return
        bpm = 60 * fps / L
        self.bpm = bpm if not self.bpm or abs(bpm - self.bpm) > 6 else self.bpm * 0.7 + bpm * 0.3

    def features(self, t):
        span = max(1.0, min(6.0, t - (self.ev[0][0] if self.ev else t)))
        cnt = lambda kind: sum(1 for _, k in self.ev if k == kind) / span
        hh = sorted(self.hi_hist)
        wall = (sum(hh) / len(hh)) / max(1, hh[int(len(hh) * 0.9)]) if hh else 0
        hi_mean = (sum(hh) / len(hh)) if hh else 0
        subr = sum(self.subr_hist) / len(self.subr_hist) if self.subr_hist else 0
        hish = sum(self.hish_hist) / len(self.hish_hist) if self.hish_hist else 0
        if hi_mean < 1500: wall = 0.0
        return dict(kps=cnt('k'), sps=cnt('s'), hps=cnt('h'), vps=cnt('v'), pps=cnt('p'),
                    wall=wall, hi_mean=hi_mean, subr=subr, hish=hish)

    def guess(self, f):
        """Mode from the sound alone (no rule / keyword / tag). Ratios, not absolute levels.
        m2: breakcore is checked BEFORE the guitar-wall test (distorted breakcore looked like a wall: Sewerslvt → МОШ)."""
        bpm = self.bpm; b2 = bpm * 2 if 0 < bpm < 100 else bpm
        dense_breaks = f['sps'] >= 2.2 and f['hps'] >= 3.0 and f['kps'] >= 1.2
        if 150 <= b2 <= 200 and dense_breaks and f['subr'] < 0.34:
            return 'break', 'jungle' if f['sps'] >= 3.0 else 'liquid'
        if f['wall'] > 0.7 and f['hish'] > 0.45: return 'mosh', ''                       # sustained distorted treble
        if f['subr'] > 0.38 or f['pps'] >= 0.6: return 'nod', ''
        if (150 <= bpm <= 190 or 75 <= bpm <= 95) and f['hps'] >= 3.5 and f['subr'] < 0.3:
            return 'break', 'jungle' if f['sps'] >= 3.0 else 'liquid'
        if 65 <= bpm <= 120 and f['subr'] >= 0.15: return 'nod', ''
        return 'groove', ''

    def _classify(self, f, t):
        if not self.bpm or t - (self.t0 if self.t0 is not None else t) < 4: return
        g = self.guess(f)
        if g != self.cand: self.cand = g; self.cand_since = t
        if self.auto is None and t - self.cand_since >= 4: self.auto = g; self.auto_since = t      # first pick after ~8 s
        elif g != self.auto and t - self.cand_since >= 16: self.auto = g; self.auto_since = t    # m2: flips need 16 s of agreement


class Listener(threading.Thread):
    """Runs cava while wanted; feeds the Ear. start_ear()/stop_ear() are cheap to call often."""
    def __init__(self):
        super().__init__(daemon=True)
        self.ear = Ear(); self.want = False; self.proc = None; self.err = None; self.fps = 0
        self.cv = threading.Condition()

    def start_ear(self):
        with self.cv: self.want = True; self.cv.notify()

    def stop_ear(self):
        with self.cv: self.want = False
        p = self.proc
        if p: p.terminate()

    def run(self):
        import shutil, ctypes, signal as sig
        if not shutil.which('cava'):
            self.err = 'cava not installed (sudo apt install cava)'; log(self.err); return
        os.makedirs(CACHE, exist_ok=True)
        with open(CAVA_CONF, 'w') as f: f.write(CAVA_TEXT)
        def child():
            try: ctypes.CDLL('libc.so.6').prctl(1, sig.SIGTERM)
            except Exception: pass
        fails = 0
        while True:
            with self.cv:
                while not self.want: self.cv.wait()
            t_start = time.time()
            try:
                self.proc = subprocess.Popen(['cava', '-p', CAVA_CONF], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                             stdin=subprocess.DEVNULL, preexec_fn=child)
                log('ear on (cava)'); n = 0; tn = time.time()
                fmt = f'<{BANDS}H'; sz = BANDS * 2; rd = self.proc.stdout.read
                while self.want:
                    b = rd(sz)
                    if len(b) < sz: break
                    now = time.time(); self.ear.feed(struct.unpack(fmt, b), now); n += 1
                    if now - tn >= 5: self.fps = n / (now - tn); n = 0; tn = now
                if self.proc.poll() is None: self.proc.terminate()
                self.proc.wait(timeout=2)
            except Exception as e:
                log(f'ear: {e}')
            self.proc = None; self.ear.snap = dict(active=False)
            if self.want:
                fails = fails + 1 if time.time() - t_start < 10 else 0
                self.err = f'cava stopped (restart in {min(60, 2 ** fails)} s)'; log(self.err)
                time.sleep(min(60, 2 ** fails))
            else:
                log('ear off')


# ======================= the dance =======================
OX, OY = 3, 4                                    # sprite origin in zarya-daemon's grid
MONO = {'#7B4DFF': '#6A6578', '#9D7BFF': '#A9A4B6', '#07060D': '#09080D', '#F29AB4': '#2A2833', '#8FD9A8': '#8FD9A8',
        '#5A3FB0': '#55505F', '#6E5BB4': '#8A8596'}
KEND_VARIANTS = [('gnx', 'gnx'), ('damn', 'damn'), ('morale', 'morale'), ('big steppers', 'morale'), ('butterfly', 'tpab'),
                 ('good kid', 'gkmc'), ('m a a d', 'gkmc'), ('section 80', 'gkmc'), ('untitled', 'tpab')]
# feet frames (rows 8-9 of the sprite, 14 columns): the four little feet are the bottom-row cells
FEET = {'stand': ['.V.VV.VVV.V.V.', '.V..V..V....V.'], 'alt': ['.VV.V.VV.VV.V.', '..V....V..V...'],
        'stepL': ['.V.VV.VVV.V.V.', '.......V....V.'], 'stepR': ['.V.VV.VVV.V.V.', '.V..V.........'],
        'splay': ['.V.VV.VVV.V.V.', 'V...V...V....V'], 'tiptoe': ['..VVV.VVV.VV..', '....V..V......'],
        'wide': ['VV.VV.VVV.V.VV', 'V............V'], 'tuck': ['..VVVVVVVVVV..', '..............']}
HEART = ['.X.X.', 'XXXXX', '.XXX.', '..X..']
NOTE = ['.XX', '.X.', 'XX.', 'XX.']                                         # m4: НАПЕВ
KIN = ['.X.X.', '.XXX.', 'XX.XX', 'XXXXX', '.XXX.', '.X.X.']                # m4: the one who is missing (original)
ROCK = [(0, 3), (0, 2), (1, 1), (1, 0), (2, 0), (2, 1), (3, 2), (3, 3)]       # m4: ПРИВАЛ rock outline (col, top row)
SHADE = ['X.......X', 'XX.....XX', '.XXXXXXX.', 'XXXXXXXXX', 'XX.XXX.XX', 'XXXXXXXXX', '.XXXXXXX.', '..XXXXX..']   # m5: the summoned shadow (original)
HOOD = ['.X.', 'XXX', 'X.X', 'XXX', 'XXX', 'XXX', 'X.X']                       # m5: a hooded figure (original)
ANTLER = [(0, -1), (0, -2), (-1, -2), (0, -3), (1, -3), (-1, -4), (0, -4), (-2, -4), (1, -5), (-1, -5)]   # m5: grows from the left horn
GLYPHS = 'ЖЯЮЩШЦФЪЬЫЭБДЛПИГЗҐЄЇѢѲѴ'
CYR = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
MOVES = dict(groove=('bob', 'sway', 'steptouch', 'hop'), nod=('nod', 'bounce', 'lean', 'earbob'),
             mosh=('bang', 'swaybang', 'stomp', 'circle'), kawaii=('arcs', 'uwu', 'wink'))


def var_of(ctx): return (ctx or {}).get('_var', '')


def kendrick_variant(album):
    a = norm(album)
    for key, var in KEND_VARIANTS:
        if key in a: return var
    return 'base'


def row_of(r): return int(round(r[1] - OY))
def col_of(r): return int(round(r[0] - OX))


def gapfill(rects):
    """The jump fix: rows moved by a fraction of a cell left see-through strips between body and feet.
    Any vertical gap under 1 cell between two sprite cells in the same pixel column is closed by stretching the upper one."""
    cells = [r for r in rects if 0.98 <= r[2] <= 1.02 and 0.98 <= r[3] <= 1.6 and r[5] >= 0.6]
    cols = {}
    for r in cells: cols.setdefault(round(r[0] * 5), []).append(r)
    for col in cols.values():
        col.sort(key=lambda r: r[1])
        for a, b in zip(col, col[1:]):
            gap = b[1] - (a[1] + a[3])
            if 0.02 < gap < 0.95: a[3] += gap
    return rects
