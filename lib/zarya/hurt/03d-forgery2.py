# ДЕМОН · concept + direction: ШУМ (shum) · built with Claude (Anthropic)
# >>> h21 ПОДДЕЛКА 2 (mint-pack v55). ШУМ 2026-11-07 22:31: "there is only movement but we can add other things like make new
#     explotions and make more fast? also pixels everywhere and we can add some kawaiiish things but all following the main
#     concept of creepish"; 22:32: "all 1 to 12". Everything stays inside his window (no whole-screen: ШУМ 2026-11-02).
#   1  БОЛЬШЕ ВЗРЫВОВ  an edit counts as hard: up to 2 blasts, 3 from ×1.30 (eurodance edits had none in v54).
#   2  ПЕРЕМОТКА       blast at r× speed, then it rebuilds like a tape scrubbed backwards (frames skipped); one pixel
#                      lands in the wrong place and stays there for the song.
#   3  ПИТЧ            it rips apart in horizontal strips, each row faster than the one under it, rows alternate sides.
#   4  КОНФЕТТИ        the blast throws pink / white pixel hearts and stars; on the floor hearts crack in half and leave
#                      red stains that rot like the blood (h18); stars blink into a red eye once and go.
#                      The three blasts take turns per song (random start).
#   5  ХЛОПОК          small pops between the big ones: 6-10 pixels burst off a body cell every 4 bars in loud parts (and
#                      on a chorus start), never closer than 3 s; its body stays whole.
#   6  ПЕРЕГРУЗ        loud parts stutter like a 2× video: of every 5 frames, 2 are held. (Jolts 0.45, jumps 2-3 cells: h21
#                      edits in 03c.)
#   7  ПОЛОСЫ          a jump leaves 1-cell streaks behind it for 0.15 s.
#   8  ПЫЛЬ            dark-red dust rising at r× speed; how much follows the loudness; it all hops on a kick.
#   9  СБОЙ            pixel rain falling, faster with r; it freezes for a frame on each kick.
#   10 УШКИ            choruses (map) or 8 s of loud singing-level (no map): its horns bend into cat ears, the nightcore
#                      thumbnail look; a red horn tip shows inside the left ear; ears flick on hats; a blast snaps them
#                      back to horns. Hard cut in and out with 0.06 s of one ear, one horn.
#   11 ЗВЁЗДОЧКИ       anime sparkles (pink / white plus shapes) pop around it on hats; each blinks into a red eye for one
#                      frame before it goes.
#   12 СЕРДЕЧКО        sung parts (map voice ≥ 0.5; no map: mid loudness): its slit eye becomes a pink heart with a red
#                      pupil; a hard hit cracks it for 0.25 s and the slit shows through. Not while ПРИМАНКА's mask is on.
NC2_KINDS = ('rewind', 'pitch', 'confetti')
NC2_RU = dict(rewind='ПЕРЕМОТКА', pitch='ПИТЧ', confetti='КОНФЕТТИ')
NC2_DUST = ('#491D1E', '#881B22', '#491D1E', '#C71625')
NC2_RAIN_HEAD, NC2_RAIN_TAIL = '#FF2244', '#491D1E'
NC2_STREAK = '#881B22'
NC2_BODY = ('#000000', INK)
HEART3 = ((0, 0), (2, 0), (0, 1), (1, 1), (2, 1), (1, 2))
STAR3 = ((1, 0), (0, 1), (1, 1), (2, 1), (1, 2))
EAR_L = [(0, -1, 'R'), (1, -1, 'K'), (2, -1, 'P'), (3, -1, 'K'), (4, -1, 'R'), (1, -2, 'R'), (2, -2, 'P'), (3, -2, 'R'), (2, -3, 'R')]
NC2_TOP = OY - 14                   # how far up his window the pixels go (cells above the pet area)


def _nc2_tick(dt_items, now, step=0.05):
    """stepped particles (20 fps): [x, y, vx, vy, g, last] updated in place."""
    for p in dt_items:
        d = now - p['last']
        if d < step: continue
        d = min(d, 0.15); p['last'] = now
        p['vy'] += p.get('g', 30) * d; p['x'] += p['vx'] * d; p['y'] += p['vy'] * d


def _nc2_body(cells):
    return [c for c in cells if c[4] in NC2_BODY and c[5] >= 0.5]


def _nc2_layer(self, rects, out, ov, now, sn, pos, pv, el):
    out, ov = _nc2_layer0(self, rects, out, ov, now, sn, pos, pv, el)
    nc = self.nc
    if nc is None or nc['slow'] or getattr(self, 'jaw_t', None) is not None or self.vanish: return out, ov
    r = nc['r']; lvl = sn.get('level', 0) or 0; kick = bool(self.kick_now); hat = bool(self._hits.get('hat'))
    ctx = self.ctx or {}; a = self.arc; ph = a['ph'] if a else None; heavy = ph in ('soul', 'boom', 'build')
    s2 = nc.setdefault('v2', dict(k=0, pop_t=-9, pops=[], conf=[], spark=[], dust=[], rain=[], dust_t=now, rain_t=now, ears=False,
                                  ears_t=-9, loud_since=None, chorus=False, heart_crack=-9, snaps=[], rw=None, wrong=[], held=None,
                                  hold_said=False, ear_flick=(0, -9), said=set()))
    if kick: s2['k'] += 1
    if pv: self._nc2_preview(nc, s2, now, el)
    off = nc.get('off', (0.0, 0.0))
    # ---- 2 ПЕРЕМОТКА: record the blast, play it back reversed at the start of СБОРКА
    if a and a.get('nc_kind') == 'rewind':
        if ph == 'boom': s2['snaps'].append(out); del s2['snaps'][:-40]
        elif ph == 'build':
            if s2['rw'] is None: s2['rw'] = now
            i = len(s2['snaps']) - 1 - int((now - s2['rw']) * 30 * 2 * r)
            if i >= 0 and s2['snaps']:
                out = s2['snaps'][i] if i % 3 else s2['snaps'][max(0, i - 1)]                    # frames skip like a scrubbed tape
                ov = [o for o in ov if o[0] not in ('under', 'glyphs')] + [('flash', (NC2_RAIN_TAIL, 0.25))]
            elif not a.get('nc_wrong'):
                a['nc_wrong'] = True
                body = _nc2_body(out) or [[OX + 6, OY + 5, 1, 1, INK, 1.0]]
                c = self.rng.choice(body)
                s2['wrong'] = (s2['wrong'] + [(c[0] - OX - off[0], c[1] - OY - off[1], self.rng.choice((-2, -1, 1, 2)), self.rng.choice((-1, 0, 1)))])[-3:]
                log(f'hurt: {FORM_NAME} ПЕРЕМОТКА: rebuilt, one pixel in the wrong place ({len(s2["wrong"])})')
    else:
        s2['snaps'] = []; s2['rw'] = None
    # ---- 10 УШКИ
    chorus = bool(ctx.get('chorus')) if ctx else False
    if pv: chorus = 3.5 <= el < 6.5
    elif not ctx:
        if lvl > 0.7: s2['loud_since'] = s2['loud_since'] or now
        else: s2['loud_since'] = None
        chorus = s2['loud_since'] is not None and 8.0 <= now - s2['loud_since'] < 24.0
    want = chorus and not heavy
    if want != s2['ears']:
        s2['ears'] = want; s2['ears_t'] = now
        if want or ph == 'boom': log(f'hurt: {FORM_NAME} УШКИ ' + ('on (chorus)' if want else 'off: a blast snapped them back to horns'))
    if chorus and not s2['chorus'] and not heavy: s2['pop_due'] = True
    s2['chorus'] = chorus
    if s2['ears'] or now - s2['ears_t'] < 0.06:
        half = now - s2['ears_t'] < 0.06
        if hat and self.rng.random() < 0.25: s2['ear_flick'] = (self.rng.choice((-1, 1)), now)
        out, ov = self._nc2_ears(out, ov, now, off, half, s2)
    # ---- 12 СЕРДЕЧКО
    voice = (ctx.get('voice') or 0) >= 0.5 if ctx else 0.35 <= lvl <= 0.75
    if pv: voice = 6.2 <= el < 9.0
    mask = self._lure_on(now) and getattr(self, 'face', None) is True
    if voice and not heavy and not mask:
        if kick and lvl >= 0.85 or (pv and abs(el - 8.0) < 0.02): s2['heart_crack'] = now
        out = self._nc2_heart(out, now, now - s2['heart_crack'] < 0.25)
    # ---- 11 ЗВЁЗДОЧКИ
    if hat and not heavy and len(s2['spark']) < 6 and self.rng.random() < 0.35:
        x = self.rng.choice((self.rng.uniform(OX - 4, OX - 1), self.rng.uniform(OX + 14, OX + 16))) if self.rng.random() < 0.6 else self.rng.uniform(OX, OX + 13)
        y = self.rng.uniform(OY - 5, OY - 1) if OX <= x <= OX + 13 else self.rng.uniform(OY - 4, OY + 8)
        s2['spark'].append(dict(x=round(x), y=round(y), t=now, col=self.rng.choice((SWEET, BONE, BLUSH))))
    sp = []
    for z in s2['spark']:
        u = now - z['t']
        if u < 0.08: sp.append([z['x'] + 0.5, z['y'] + 0.5, 0.5, 0.5, BONE, 0.9])
        elif u < 0.28: sp += [[z['x'] + dx * 0.5, z['y'] + dy * 0.5, 0.5, 0.5, BONE if (dx, dy) == (1, 1) else z['col'], 0.95] for dx, dy in STAR3]
        elif u < 0.33: sp.append([z['x'] + 0.5, z['y'] + 0.25, 0.5, 1.0, RED, 1.0])                  # it was an eye
    s2['spark'] = [z for z in s2['spark'] if now - z['t'] < 0.33]
    # ---- 5 ХЛОПОК
    due = s2.pop('pop_due', False) or (kick and s2['k'] % 16 == 0 and lvl > 0.55)
    if pv and abs(el - 5.0) < 0.02: due = True
    if due and not heavy and now - s2['pop_t'] > 3.0:
        body = _nc2_body(out)
        if body:
            c = self.rng.choice(body); s2['pop_t'] = now; n = self.rng.randint(6, 10)
            s2['pops'] += [dict(x=c[0], y=c[1], vx=self.rng.uniform(-9, 9) * r, vy=self.rng.uniform(-14, -4), g=30, last=now, t=now,
                                col=self.rng.choice((RED, RED, PINK, BONE))) for _ in range(n)]
            log(f'hurt: {FORM_NAME} ХЛОПОК ({n} pixels)')
    _nc2_tick(s2['pops'], now); s2['pops'] = [p for p in s2['pops'] if now - p['t'] < 0.6]
    pops = [[round(p['x'] * 5) / 5, round(min(p['y'], OY + 9.6) * 5) / 5, 0.6, 0.6, p['col'], 1 - (now - p['t']) / 0.6] for p in s2['pops']]
    # ---- 4 КОНФЕТТИ pieces
    conf = self._nc2_confetti(now, s2)
    # ---- 7 ПОЛОСЫ
    streak = []
    if now - nc['jump_t'] < 0.15 and not heavy:
        body = [c for c in out if c[4] in NC2_BODY]
        if body:
            jx = nc['jump'][0]; x0 = min(c[0] for c in body) if jx > 0 else max(c[0] + c[2] for c in body)
            fade = 1 - (now - nc['jump_t']) / 0.15
            for row in range(OY + 1, OY + 10, 2):
                for k in range(abs(jx) * 2 + 2):
                    streak.append([x0 - (k + 1) * 0.5 * (1 if jx > 0 else -1), row + off[1], 0.5, 0.5, NC2_STREAK, 0.8 * fade * (1 - k / (abs(jx) * 2 + 3))])
    # ---- 2 the wrong pixels from ПЕРЕМОТКА
    wrong = []
    for wx, wy, mx, my in s2['wrong']:
        bx, by = OX + wx + off[0], OY + wy + off[1]
        out = [c for c in out if not (c[4] in NC2_BODY and abs(c[0] - bx) < 0.3 and abs(c[1] - by) < 0.3)]
        wrong.append([bx + mx, by + my, 1, 1, INK, 1.0]); wrong.append([bx + mx + 0.2, by + my + 0.2, 0.6, 0.6, RED, 0.9])
    # ---- 8 ПЫЛЬ + 9 СБОЙ
    back = self._nc2_dust_rain(now, s2, lvl, kick, r)
    out = back + list(out) + streak + wrong + pops + conf + sp
    # ---- 6 ПЕРЕГРУЗ
    if lvl > 0.6 and not heavy:
        if int(now * 30) % 5 in (1, 2) and s2['held'] is not None: return s2['held']
        if not s2['hold_said']: s2['hold_said'] = True; log(f'hurt: {FORM_NAME} ПЕРЕГРУЗ (loud part: 2 of 5 frames held)')
    s2['held'] = (out, ov)
    return out, ov


def _nc2_ears(self, out, ov, now, off, half, s2):
    """horns → cat ears (half: left ear, right horn). The rim under them follows."""
    keep_right_horn = half
    top = OY + off[1] - 0.05
    def is_horn(c): return c[1] < top and c[4] in NC2_BODY + (RED,) and c[5] >= 0.5 and (not keep_right_horn or c[0] < OX + 7)
    out = [c for c in out if not is_horn(c)]
    fx, ft = s2['ear_flick']; flick = 0.4 * fx if now - ft < 0.08 else 0.0
    ears = []
    for side in ((-1,) if half else (-1, 1)):
        for ex, ey, k in EAR_L:
            x = OX + (ex if side < 0 else 13 - ex) + off[0] + (flick if side == fx else 0.0); y = OY + ey + off[1]
            col = RED if k == 'R' else SWEET if k == 'P' else INK
            if side < 0 and (ex, ey) == (2, -2) and int(now * 2) % 2 == 0: col = RED                  # the horn tip, inside the ear
            ears.append([x, y, 1, 1, col, 1.0])
    rims = []
    for o in ov:
        if o[0] == 'under': rims.append(('under', [c for c in o[1] if not (c[1] < top and (not keep_right_horn or c[0] < OX + 7))]))
        else: rims.append(o)
    return list(out) + ears, rims


def _nc2_heart(self, out, now, cracked):
    eye = next((c for c in out if c[4] == RED and c[3] == 2 and OY + 1.5 <= c[1] < OY + 7.5 and OX - 2 <= c[0] < OX + 16), None)   # h22: ТИК teleports it 2 up
    if eye is None: return out
    ex, ey = eye[0], eye[1]
    out = [c for c in out if not (c[4] == RED and ey - 1 <= c[1] < ey + 2.5 and ex - 4 <= c[0] < ex + 5 and c[2] <= 1 and c[3] <= 2)]
    h = []
    for dx, dy in HEART3:
        sh = (-0.4 if dx == 0 else 0.4 if dx == 2 else 0.0) if cracked else 0.0
        if cracked and dx == 1: continue
        h.append([ex - 1 + dx * 0.7 + sh, ey - 0.2 + dy * 0.7, 0.7, 0.7, SWEET, 1.0])
    h.append([ex - 0.3, ey + 0.5, 0.7, 0.7, RED, 1.0] if not cracked else [ex - 0.25, ey - 0.2, 0.6, 2.0, RED, 1.0])     # pupil / the slit
    return out + h


def _nc2_confetti(self, now, s2):
    res = []
    _nc2_tick(s2['conf'], now)
    floor = OY + 10
    keep = []
    for p in s2['conf']:
        if p['landed'] is None and p['y'] >= floor - 1.5:
            p['landed'] = now; p['y'] = floor - 1.5; p['vx'] = p['vy'] = 0.0; p['g'] = 0
            if p['shape'] == 'heart':
                b = getattr(self, 'blood', None)
                if b is None: b = self.blood = []
                for k in range(2):
                    b.append(dict(x=p['x'] + 0.5 * k, y=floor, vx=0.0, vy=0.0, t=now, last=now, life=self.rng.uniform(3.0, 4.0), s=0.6))
        u = now - p['landed'] if p['landed'] is not None else None
        if u is not None and u > (0.5 if p['shape'] == 'heart' else 0.12): continue
        keep.append(p)
        x, y = round(p['x'] * 5) / 5, round(p['y'] * 5) / 5
        if p['shape'] == 'heart':
            split = 0.0 if u is None else 0.3 + u
            for dx, dy in HEART3:
                if u is not None and dx == 1 and dy == 1: continue                                  # the crack
                res.append([x + dx * 0.5 + (-split if dx == 0 else split if dx == 2 else 0), y + dy * 0.5, 0.5, 0.5, p['col'], 1.0])
        elif u is None:
            res += [[x + dx * 0.5, y + dy * 0.5, 0.5, 0.5, p['col'], 1.0] for dx, dy in STAR3]
        else: res.append([x + 0.5, y + 0.25, 0.5, 1.0, RED, 1.0])                                     # a star lands: an eye, once
    s2['conf'] = keep
    return res


def _nc2_dust_rain(self, now, s2, lvl, kick, r, dust_cap=70, rain_cap=None):     # h22: caps for other songs
    # ПЫЛЬ
    d = s2['dust']; dt = now - s2['dust_t']
    if dt >= 0.05:
        s2['dust_t'] = now; dt = min(dt, 0.15)
        n = int(lvl * 30 * r * dt + self.rng.random())
        for _ in range(n):
            if len(d) < dust_cap: d.append([self.rng.uniform(0, PW), OY + 10, -self.rng.uniform(3, 7) * r, self.rng.choice((0.4, 0.4, 0.6)), self.rng.choice(NC2_DUST)])
        for p in d: p[1] += p[2] * dt; p[0] += self.rng.choice((-0.2, 0, 0.2))
    if kick:
        for p in d: p[1] -= 0.6                                                           # the whole cloud hops on a kick
    s2['dust'] = d = [p for p in d if p[1] > NC2_TOP]
    dust = [[round(p[0] * 5) / 5, round(p[1] * 5) / 5, p[3], p[3], p[4], 0.85] for p in d]
    # СБОЙ
    rn = s2['rain']; dt = now - s2['rain_t']
    if dt >= 0.05 and not kick:                                                           # a kick freezes it for a frame
        s2['rain_t'] = now; dt = min(dt, 0.15)
        if lvl > 0.3 and len(rn) < (rain_cap if rain_cap is not None else 6 + int(10 * lvl)) and self.rng.random() < 0.5 + lvl * 0.5:
            rn.append([float(self.rng.randint(0, PW - 1)), NC2_TOP, self.rng.uniform(10, 18) * r, self.rng.randint(2, 4)])
        for p in rn: p[1] += p[2] * dt
        s2['rain'] = rn = [p for p in rn if p[1] < OY + 10.5]
    elif kick: s2['rain_t'] = now
    rain = []
    for x, y, v, n in rn:
        yy = round(y * 2) / 2
        rain.append([x, yy, 0.5, 0.5, NC2_RAIN_HEAD, 0.9])
        rain += [[x, yy - 0.5 * (k + 1), 0.5, 0.5, NC2_RAIN_TAIL, 0.8 - 0.15 * k] for k in range(n)]
    return dust + rain


def _nc2_preview(self, nc, s2, now, el):
    """the preview's three blasts: ПЕРЕМОТКА 9 s, КОНФЕТТИ 13 s, ПИТЧ 16.5 s."""
    for at, kind in ((9.0, 'rewind'), (13.0, 'confetti'), (16.5, 'pitch')):
        if el >= at and at not in s2['said']:
            s2['said'].add(at); s2['force'] = kind
            self.arc = dict(ph='soul', t=now, at=None, lead=0.6, power=2.7, pv=True, k=1.0)


_nc2_boom0 = Form._boom


def _nc2_boom(self, now, a, lvl):
    _nc2_boom0(self, now, a, lvl)
    nc = getattr(self, 'nc', None)
    if nc is None or nc['slow']: return
    s2 = nc.setdefault('v2', None)
    if s2 is None: return
    kind = s2.pop('force', None)
    if kind is None:
        i = nc.setdefault('kind_i', self.rng.randrange(len(NC2_KINDS))); nc['kind_i'] = i + 1; kind = NC2_KINDS[i % len(NC2_KINDS)]
    a['nc_kind'] = kind; r = nc['r']
    for s in self.shards:
        s[6] *= r; s[7] *= r                                                              # everything flies r× faster
        if kind == 'pitch':
            row = s[1] - OY; side = 1 if int(round(row)) % 2 else -1
            s[6] = side * (5 + (10 - row) * 1.8) * r; s[7] = -self.rng.uniform(1, 4)
    if kind == 'confetti':
        n = self.rng.randint(12, 16); mx = OX + 7
        s2['conf'] += [dict(x=mx + self.rng.uniform(-4, 4), y=OY + self.rng.uniform(2, 7), vx=self.rng.uniform(-14, 14) * r,
                            vy=-self.rng.uniform(10, 22), g=30, last=now, t=now, landed=None,
                            shape=self.rng.choice(('heart', 'heart', 'star')), col=self.rng.choice((SWEET, BONE, BLUSH))) for _ in range(n)]
    log(f'hurt: {FORM_NAME} ДЕТОНАЦИЯ {NC2_RU[kind]} (×{r:.2f})')


_nc2_set_hard0 = Form.set_hard


def _nc2_set_hard(self, hard, soft=False):
    nc = getattr(self, 'nc', None)
    edit = nc is not None and not nc.get('pv_end') and not nc['slow']
    if edit: hard, soft = True, False
    _nc2_set_hard0(self, hard, soft)
    if edit:
        want = 3 if nc['r'] >= 1.3 else 2
        if self.det_max < want:
            self.det_max = want
            if self.targets is not None and len(self.targets) < want: self.targets = None              # the desk asks the map again
            if not nc.get('more_said'): nc['more_said'] = True; log(f'hurt: {FORM_NAME} БОЛЬШЕ ВЗРЫВОВ: up to {want} blasts on this edit')


_nc2_layer0 = Form._nc_layer
Form._nc_layer = _nc2_layer
Form._nc2_ears = _nc2_ears
Form._nc2_heart = _nc2_heart
Form._nc2_confetti = _nc2_confetti
Form._nc2_dust_rain = _nc2_dust_rain
Form._nc2_preview = _nc2_preview
Form._boom = _nc2_boom
Form.set_hard = _nc2_set_hard
# <<< h21 ПОДДЕЛКА 2
