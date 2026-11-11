# ДЕМОН · concept + direction: ШУМ (shum) · built with Claude (Anthropic)
# >>> h18 ПАСТЬ hunts (mint-pack v45): ОХОТА / ВЫСЛЕЖИВАНИЕ / СТРАХ / ПРОМАХ / БОЙНЯ, blood that rots (03b-act.py). Below: h16 (mint-pack v43: clean body snapshot; v42 h15: h12-h14 were drawn jaws / teeth, retired): sometimes, when its ДЕМОН act ends, ПОДМЕНЫШ eats
#     the fake. ШУМ 2026-11-03: "it just eats it", no teeth, left to right, nothing after. It comes in from the left edge and
#     takes 4 bites across him, each a hair before the kick (its own uneven rhythm with no music). No teeth are drawn: the
#     bitten edge is scalloped, you read the teeth from the wound. Between bites everything holds; what is left of him keeps
#     dancing a beat late, he doesn't notice. His visor blinks once before the last bite. Then it is in his place. Nothing else.
#     Death Grips law: hard cuts and held frames only. Stays inside his window. Once per song at most, about 1 in 3 acts.
JAW_MAX = 6.0                   # the act never runs longer than this, music or not
JAW_CHANCE = 1 / 3
BITE_X = (3.4, 7.0, 10.4, 16.0)     # where each bite reaches, cells from his left edge (OX)
BITE_SCALLOP = (0, 1, 3, 3, 1, 0, 2, 3, 2, 0, 0, 1)    # per row from his top: how much further the bite went (two tooth arcs)
OWN_RHYTHM = (0.30, 0.46, 1.05, 1.62)                  # no kick to follow: a fast double bite, a pause, then the slow one
EARLY = 0.06                    # it bites a hair before the kick it expects (ВПЕРЕДИ)
# h18: the hunts. bx = where each bite reaches, own = its rhythm with no kick, wait = how long it lurks first,
# per = kick spacing multiplier (0.5 = every half beat), blood = drops per bite. ШУМ 2026-11-03: "different velocities".
HUNTS = dict(
    hunt=dict(bx=BITE_X, own=OWN_RHYTHM, wait=0.25, per=1.0, blood=3),
    stalk=dict(bx=BITE_X, own=tuple(x + 1.35 for x in OWN_RHYTHM), wait=1.6, per=1.0, blood=3),
    fear=dict(bx=BITE_X, own=(1.0, 1.18, 1.45, 1.70), wait=0.9, per=1.0, blood=3),
    miss=dict(bx=(5.0,), own=(0.45,), wait=0.25, per=1.0, blood=0),
    slaughter=dict(bx=(2.4, 4.8, 7.0, 9.4, 12.0, 16.0), own=(0.10, 0.22, 0.34, 0.46, 0.58, 0.75), wait=0.08, per=0.5, blood=8))
HUNT_RU = dict(hunt='ОХОТА', stalk='ВЫСЛЕЖИВАНИЕ', fear='СТРАХ', miss='ПРОМАХ', slaughter='БОЙНЯ')
HUNT_W = (('hunt', 35), ('stalk', 20), ('fear', 15), ('miss', 15), ('slaughter', 15))
# stalk: it peeks in and out before it commits (time from t0, how far its mouth comes in; None = hidden)
PEEK = ((0.30, None), (0.55, -0.6), (0.90, None), (1.05, 0.4), (1.40, None), (1.60, -0.6))


def _jaw_body(self, idle, now):
    """h16: ПОДМЕНЫШ's clean body for the bite, taken once when it starts: its base frame with no music, no glitches, no
    mouse, then its state put back. Body + outline + eyes only, fully solid. (h15 copied its last live frame, so a vanished,
    rotting or glyph-shattered moment made the eater invisible or "code form".)"""
    j = getattr(self, 'jaw', None)
    if j is not None and j.get('body'): return j['body']
    saved = dict(self.__dict__); cells = []
    try:
        self._frame(idle, {}, now, mouse=None, music=False, dance=None)
        blk, extra, eyes, rim = self._parts
        cells = [list(r) for r in rim] + [list(r) for r in blk] + [list(r) for r in eyes]
    except Exception as e: log(f'hurt: ПАСТЬ body error: {e!r}')
    finally: self.__dict__.update(saved)
    cells = [[x, y, w, h, c, 1.0] for x, y, w, h, c, a in cells if a > 0.05]
    if j is not None and cells: j['body'] = cells; log(f'hurt: {FORM_NAME} ПАСТЬ body {len(cells)} cells')
    return cells


def _jaw_bite_due(self, j, now):
    """is the next bite now? Follows the kick (predicted from the last kicks, a hair early); its own rhythm without one."""
    e = now - j['t0']
    if j['music'] and self.kick_now and not j['prev_kick']: j['kicks'].append(now)
    j['prev_kick'] = bool(self.kick_now)
    bx, own = j['bx'], j['own']
    if e < j['wait']: return False                                                     # it shows up and waits (stalks, he sees it)
    since = now - j['last'] if j['bites'] else 9.0
    if j['bites'] and since > 1.0: return True                                         # never stalls
    ks = j['kicks'][-5:]
    if j['music'] and len(ks) >= 2:
        gaps = sorted(b - a for a, b in zip(ks, ks[1:])); per = min(1.2, max(0.25, gaps[len(gaps) // 2])) * j['per']
        nxt = ks[-1] + per
        while nxt - EARLY < now - 0.5 * per: nxt += per
        return now >= nxt - EARLY and since > 0.6 * per
    if j['music'] and ks and ks[-1] == now and since > 0.2: return True                # first kicks: on the kick itself
    if not j['music'] or 'own0' in j:                                                  # no music, or no kick heard
        return j['bites'] < len(own) and e >= own[j['bites']] + j.get('own0', 0.0)
    return False


def _jaw(self, out, ov, now, idle=None):
    """the frame while it eats him: what is left of ДЕМОН (dancing, a beat late) right of the bite, ПОДМЕНЫШ left of it."""
    j = getattr(self, 'jaw', None)
    if j is None or now < j['t0']: return out, ov
    if j['end'] is None and j['music'] and not j['kicks'] and now - j['t0'] > 1.4 and 'own0' not in j:
        j['own0'] = now - j['t0'] - j['own'][j['bites']]                              # no kick heard: its own rhythm from here
    BX = j['bx']; kind = j['kind']
    if j['end'] is None and self._jaw_bite_due(j, now):
        j['bites'] += 1; j['last'] = now
        if hasattr(self, '_blood_bite'): self._blood_bite(j, now)                       # h18: blood at the wound
        if j['bites'] >= len(BX):
            j['end'] = now + (0.75 if kind == 'miss' else 0.4); self.mimic = j['end']    # last bite: it holds, then the act ends
            if kind == 'miss': log(f'hurt: {FORM_NAME} ПАСТЬ missed (ПРОМАХ), he is still there')
    n = j['bites']
    body = self._jaw_body(idle if idle is not None else out, now)
    if not body: return out, ov
    right = max(c[0] + c[2] for c in body)
    e = now - j['t0']
    front = OX - 0.6 if n == 0 else OX + BX[n - 1] - 1.0                                # its mouth, a cell behind the wound
    if kind == 'stalk' and n == 0:                                                      # h18 ВЫСЛЕЖИВАНИЕ: peeks in, gone, peeks again
        pk = next((f for t_, f in PEEK if e < t_), -0.6)
        front = OX - 30 if pk is None else OX + pk
    hit = n and now - j['last'] < 0.07                                                  # the bite frame: it lunges one cell
    if kind == 'slaughter': hit = n and now - j['last'] < 0.05
    if kind == 'miss' and n:                                                            # h18 ПРОМАХ: lunge, air, it backs off
        since = now - j['last']
        front = OX + BX[0] - 1.0 if since < 0.30 else OX + BX[0] - 3.0 if since < 0.55 else OX - 30
    dx = round((min(front + (1.0 if hit else 0.0), right) - right) * 5) / 5
    it = [[x + dx, y, w, h, c, a] for x, y, w, h, c, a in body]
    if n >= len(BX) and kind != 'miss': return it, ov                                   # he is gone; it is in his place
    left = []
    if kind == 'miss':                                                                  # he hops right, clear of the bite, and lands back
        since = now - j['last'] if n else 9
        hop = 3.0 if since < 0.30 else 1.0 if since < 0.45 else 0.0
        if n and since < 0.12: hop = 1.6
        shake = 0.2 if n and since < 0.9 and int(now * 30) % 2 else 0.0
        return it + [[x + hop + shake, y, w, h, c, a] for x, y, w, h, c, a in out], ov
    edge0 = OX + BX[n - 1] if n else -99
    blink = n == len(BX) - 1 and 0.12 < now - j['last'] < 0.26                          # his visor, once, before the last bite
    fear = kind == 'fear' and (n or e > 0.35)                                           # h18 СТРАХ: he has seen it
    for x, y, w, h, c, a in out:
        row = int(round(y - OY))
        edge = edge0 + (BITE_SCALLOP[row] if 0 <= row < len(BITE_SCALLOP) and n else 0)
        if x + w / 2 <= edge: continue                                                  # eaten
        if blink and OY + 4 <= y < OY + 6 and OX + 1 <= x < OX + 13: c = '#07060D'
        elif fear and OY + 4 <= y < OY + 6 and OX + 1 <= x < OX + 13 and c not in ('#07060D',):
            c = c if x < OX + 4 else '#07060D'                                           # his eye goes hard left, at it
        if fear: x += 0.2 if (int(now * 24) + row) % 2 else -0.2                         # he shakes, row by row
        elif n and x < edge + 1.0 and a > 0.5:                                          # the wound: red for a moment, then bitten flesh
            c = '#FF2244' if now - j['last'] < 0.16 else '#3A2470'
        left.append([x, y, w, h, c, a])
    return it + left, ov


def _jaw_pick(self):
    tot = sum(w for _, w in HUNT_W); r = self.rng.uniform(0, tot)
    for k, w in HUNT_W:
        r -= w
        if r <= 0: return k
    return 'hunt'


def _jaw_start(self, now, music, kind=None):
    kind = kind if kind in HUNTS else self._jaw_pick()
    self.jaw = dict(t0=now, music=bool(music), bites=0, last=now, kicks=[], prev_kick=False, end=None, kind=kind, **HUNTS[kind])
    self.jaw_t = now; self.mimic = now + JAW_MAX
    return kind


def _jaw_roll(self, now, music):
    """at the end of an act: it eats him instead of the plain end? (once per song, 1 in 3, only with music)"""
    if not music or getattr(self, 'jaw_song', 0) == getattr(self, 'song_key', None): return False
    if self.rng.random() >= JAW_CHANCE: return False
    self.jaw_song = getattr(self, 'song_key', None); k = self._jaw_start(now, True)
    log(f'hurt: {FORM_NAME} ПАСТЬ {HUNT_RU[k]} (it goes for the fake)'); return True


def _jaw_preview(self, now, music=False, kind=None):
    """▶ ПАСТЬ: 0.9 s of the act, then it goes for him (on the kick if a song plays, its own rhythm if not). h18: kind = a hunt."""
    self.arc = None; self.buf = []; k = self._jaw_start(now + 0.9, music, kind); self.mimic = now + 0.9 + JAW_MAX
    log(f'hurt: {FORM_NAME} ПАСТЬ preview {HUNT_RU[k]}')


Form._jaw = _jaw
Form._jaw_body = _jaw_body
Form._jaw_bite_due = _jaw_bite_due
Form._jaw_start = _jaw_start
Form._jaw_pick = _jaw_pick
Form._jaw_roll = _jaw_roll
Form.jaw_preview = _jaw_preview
# <<< h18 ПАСТЬ
