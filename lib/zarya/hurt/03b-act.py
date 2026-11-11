# ДЕМОН · concept + direction: ШУМ (shum) · built with Claude (Anthropic)
# >>> h18 МИМИКРИЯ pool + ПРОВАЛ + blood (mint-pack v45). ШУМ 2026-11-03: "I haven't seen more than 4-5 of his animations,
#     we have more"; failed shapeshifts that have nothing to do with what's playing, then it goes back or eats him; blood
#     stays 3-4 s, then rots.
#   МИМИКРИЯ: each act picks from his whole repertoire (14 dances, 7 reactions, asleep, startled) from a shuffle bag, so
#     nothing repeats until all have played. The desk draws the act (desk d32); ПОДМЕНЫШ plays it a beat late as before.
#   ПРОВАЛ: about 1 in 4 acts (with music) picks one that doesn't fit the song (a calm sway on a hard song, mosh on a calm
#     one) and ignores the beat. In its last 1.2 s the disguise breaks: red outline cells poke through, the visor flicks to
#     its slit, rows slip out of sync, a horn skips. Then it snaps back, or (1 in 2) ПАСТЬ goes for the failed copy.
#   Blood: each bite drops a few cells at the wound (БОЙНЯ sprays). They snap down to the floor, hold red, darken, then rot
#     away cell by cell, 3-4 s in all. Drawn on top of whatever it is doing, inside his window.
ACT_DANCES = ('break', 'memory', 'nod', 'mosh', 'kendrick', 'grips', 'groove', 'epic', 'kawaii', 'rest', 'drive', 'bolero', 'run', 'hum')
ACT_REACTS = ('fire', 'blown', 'goose', 'frame', 'tear', 'spark', 'back')
ACT_STATES = ('sleep', 'alert')
ACT_POOL = tuple('d:' + m for m in ACT_DANCES) + tuple('r:' + r for r in ACT_REACTS) + tuple('s:' + s for s in ACT_STATES)
ACT_RU = dict(fire='ОГОНЬ', blown='СДУЛО', goose='МУРАШКИ', frame='КАДР', tear='СЛЕЗА', spark='ИСКРЫ', back='ОБИДА',
              sleep='СОН', alert='ИСПУГ')
REACT_LEN = dict(fire=8.0, blown=6.4, goose=4.0, frame=4.0, tear=4.5, spark=4.0, back=6.0)
FAIL_CHANCE = 1 / 4
FAIL_EAT = 1 / 2
FAIL_BREAK = 1.2                # the last seconds of a failed act: the disguise comes apart
MISFIT_HARD = ('d:bolero', 'd:rest', 'd:hum', 'd:memory', 's:sleep', 'r:tear')     # on a hard song
MISFIT_CALM = ('d:mosh', 'd:break', 'd:grips', 'r:fire', 'r:blown', 's:alert')     # on a calm one
BLOOD_LIFE = (3.0, 4.0)
BLOOD_COL = ('#FF2244', '#B0102E', '#5A0F1E', '#3A1A20')


def _act_pick(self, now, music, fail=None):
    """a new act: which of his things it fakes, and whether this one fails."""
    hard = bool(getattr(self, 'hard', False))
    if fail is None: fail = bool(music) and self.rng.random() < FAIL_CHANCE
    if fail: pick = self.rng.choice(MISFIT_HARD if hard else MISFIT_CALM)
    else:
        bag = getattr(self, 'bag', None)
        if not bag: bag = self.bag = list(ACT_POOL); self.rng.shuffle(bag)
        pick = bag.pop()
    kind, name = pick.split(':')
    dur = self.rng.uniform(4, 7)
    if kind == 'r': dur = REACT_LEN.get(name, dur)
    self.act = dict(kind=kind, name=name, fail=fail, t0=now, end=now + dur, seed=self.rng.random())
    self.mimic = now + dur
    log(f'hurt: {FORM_NAME} pretends to be him: {ACT_RU.get(name, name.upper())}' + (' · ПРОВАЛ (wrong for the song)' if fail else ''))
    return self.act


def _act_end(self, now, music):
    """end of an act: a failed one gets eaten half the time (any hunt), else it just snaps back. True = ПАСТЬ took over."""
    a = getattr(self, 'act', None); self.act = None
    if a and a.get('fail') and getattr(self, 'jaw_t', None) is None and self.rng.random() < FAIL_EAT and (a.get('preview') or now - getattr(self, 'fail_eat_t', -1e9) > 90):
        self.fail_eat_t = now; k = self._jaw_start(now, bool(music))
        log(f'hurt: {FORM_NAME} ПРОВАЛ → ПАСТЬ {HUNT_RU[k]} (it eats the failed copy)'); return True
    if a and a.get('fail'): log(f'hurt: {FORM_NAME} ПРОВАЛ → it snaps back')
    return False


def fail_preview(self, now, music=False):
    """▶ ПРОВАЛ: a failed act right now, then the normal ending roll (back, or eaten)."""
    self.arc = None; self.buf = []; self.jaw_t = None; self.jaw = None
    a = self._act_pick(now, music, fail=True); a['preview'] = True; a['end'] = now + 4.0; self.mimic = now + 4.0
    log(f'hurt: {FORM_NAME} ПРОВАЛ preview')


def _blood_bite(self, j, now):
    n = j.get('blood', 0)
    if not n: return
    bx = j['bx'][min(j['bites'], len(j['bx'])) - 1]
    b = getattr(self, 'blood', None)
    if b is None: b = self.blood = []
    for _ in range(n):
        spray = j['kind'] == 'slaughter'
        b.append(dict(x=OX + bx + self.rng.uniform(-0.6, 0.8), y=OY + self.rng.uniform(1, 8),
                      vx=self.rng.uniform(-1.0, 3.0) * (2.2 if spray else 0.6), vy=self.rng.uniform(-6, -1) if spray else 0.0,
                      t=now, last=now, life=self.rng.uniform(*BLOOD_LIFE), s=self.rng.choice((1.0, 1.0, 0.6))))
    del b[:-60]


def _blood_cells(self, now):
    b = getattr(self, 'blood', None)
    if not b: return []
    out = []; keep = []
    for d in b:
        age = now - d['t']
        if age > d['life']: continue
        keep.append(d)
        step = now - d['last']
        if step >= 0.05:                                                   # stepped, never smooth: 20 fps snaps
            d['last'] = now; floor = OY + 10
            if d['y'] < floor:
                d['vy'] += 30 * step; d['x'] += d['vx'] * step; d['y'] = min(floor, d['y'] + d['vy'] * step)
                if d['y'] >= floor: d['vx'] = 0.0
        f = age / d['life']
        c = BLOOD_COL[0] if f < 0.15 else BLOOD_COL[1] if f < 0.45 else BLOOD_COL[2] if f < 0.75 else BLOOD_COL[3]
        if f > 0.7 and (int(now * 12) + int(d['x'] * 7)) % 3 == 0: continue    # rot: it drops out cell by cell
        x = round(d['x'] * 5) / 5; y = round(d['y'] * 5) / 5
        out.append([x, y, d['s'], d['s'] if y < OY + 10 else 0.6, c, 1.0])
    self.blood = keep
    return out


def _break_disguise(self, out, now):
    """ПРОВАЛ, the last FAIL_BREAK s: red rim pokes through, visor slit, rows slip, a horn skips."""
    a = getattr(self, 'act', None)
    if not a or not a.get('fail') or getattr(self, 'jaw_t', None) is not None: return out
    left = a['end'] - now
    if left > FAIL_BREAK or left < 0: return out
    k = 1 - left / FAIL_BREAK; r = random.Random(int(now * 15) + int(a['seed'] * 1e6)); res = []
    slip = {row: (0.2 if r.random() < 0.5 else -0.2) * (1 + int(k * 2)) for row in range(12) if r.random() < 0.25 + 0.5 * k}
    horn_gone = r.random() < 0.5
    for x, y, w, h, c, al in out:
        row = int(round(y - OY))
        if horn_gone and row in (0, 1) and x < OX + 7: continue
        if OY + 4 <= y < OY + 6 and OX + 2 <= x < OX + 12:                 # the visor goes to its slit
            if r.random() < 0.3 + 0.6 * k: c = RED if (OY + 4 <= y < OY + 5 and OX + 4 <= x < OX + 10) else INK
        elif r.random() < 0.10 + 0.35 * k: c = RED                          # its outline shows through
        res.append([x + slip.get(row, 0.0), y, w, h, c, al])
    return res


_frame_h17 = Form.frame


def _frame_h18(self, rects, sn, now, **kw):
    out, ov = _frame_h17(self, rects, sn, now, **kw)
    try:
        if self.mimic_on(now): out = self._break_disguise(list(out), now)
        bl = self._blood_cells(now)
        if bl: out = list(out) + bl
    except Exception as e:
        if str(e) != getattr(self, 'act_err', None): self.act_err = str(e); log(f'hurt: act error: {e!r}')
    return out, ov


Form.frame = _frame_h18
Form._act_pick = _act_pick
Form._act_end = _act_end
Form.fail_preview = fail_preview
Form._blood_bite = _blood_bite
Form._blood_cells = _blood_cells
Form._break_disguise = _break_disguise
# <<< h18 МИМИКРИЯ pool + ПРОВАЛ + blood
