# ДЕМОН · concept + direction: ШУМ (shum) · built with Claude (Anthropic)
# >>> h20 ПОДДЕЛКА + НЕТЕРПЕНИЕ (mint-pack v54). ШУМ 2026-11-07: animations for ПОДМЕНЫШ tied to nightcore, keep the concept,
#     nothing silly; "it goes faster ... as the songs say its speed up"; all 6 ideas (ОРИГИНАЛ, РАЗГОН, СЛЕД, ПОДПИСЬ, ТОН,
#     УКРАДЕННОЕ ВРЕМЯ) + the speed layer.
#   A nightcore / sped-up edit is a copy of a real song that took the original's place, faster, in a voice that is not quite
#   its own: ПОДМЕНЫШ knows it as its own kind of forgery. The desk (d38) finds the edit and the ratio
#   r = original length / edit length (1.05-1.6; 1.25 when it can't find the original) and hands it over with forgery().
#   Never summons: only while ПОДМЕНЫШ is already out. A layer: ПРИМАНКА, ДЕЛИКАТЕС (nightstep), the arc keep their rules.
#   РАЗГОН        the first 2 bars it moves at the original speed (4 snaps a second), then a hard cut on a kick: «×1.27».
#   НЕТЕРПЕНИЕ    ТАКТ ×r (its moves change r times sooner) · ДВОЙНОЙ ШАГ (it steps on the 8ths, 16ths from ×1.25) ·
#                 ПРЫЖОК (some steps teleport 1-2 cells, frames skipped) · ВЗГЛЯД (the slit jumps every step) ·
#                 НЕ СТОИТ (calm parts: twitches every 0.2-0.3 s / r) · ВПЕРЕДИ ×r (40-120 ms early instead of 30-90).
#   НЕ ДОСЛУШАЛ   its mimicry acts last 1/r, and (r - 1) × 2 of them are dropped halfway; the next one comes r times sooner.
#   ОРИГИНАЛ      a dim ghost of ДЕМОН behind it bobs on the original tempo (beat × r); every 8 beats of drift they line up
#                 on a kick for a moment and the ghost loses a row, bottom up; by ~85 % of the song it is gone.
#   СЛЕД          in fast parts 2 stale copies (3 from ×1.25) one frame apart, in the palette's dark reds.
#   ПОДПИСЬ       its label starts as the original artist's name and is overwritten letter by letter into ПОДМЕНЫШ
#                 (0.3 / (r - 1) s, 0.8-3 s), then keeps «×r».
#   ОБРЫВ + ТОН   its shouts lose (r - 1) × 1.2 of their letters (the cut letter flickers once in a glyph) and every repeat of
#                 the same shout sits higher (step = the pitch shift in semitones / 2 cells, capped at the window top).
#   УКРАДЕННОЕ    at the end of an edit heard past half: «−0:41.» (original minus edit) and those seconds feed ГОЛОД.
#   ▶ Animations > ▶ ПОДДЕЛКА · the forgery: a 16 s preview of all of it on a fake ×1.30 beat.
NC_GUESS = 1.25
NC_RANGE = (1.05, 1.6)
NC_GHOST, NC_GHOST_EYE = '#3C1718', '#491D1E'
NC_TRAIL = ('#491D1E', '#3C1718', '#281314')
NC_LINEUP = 8                       # beats of drift between two line-ups
NC_ROWS = 10                        # ДЕМОН's body rows (the ghost loses them bottom up)
NC_DX = -2.4                        # the ghost stands a little behind it, to the left
NC_TARGET = 'ПОДМЕНЫШ'
NC_PV = 22.6                        # h21: 22.6 s, room for the three blasts
NC_JOLT = 0.45                      # h21: was 0.2 (ШУМ 2026-11-07: "there is only movement … make more fast")
NC_JUMP = (-3, -2, 2, 3)            # h21: was 1-2 cells


def _nc_fmt(s):
    s = int(round(s or 0)); return f'{s // 60}:{s % 60:02d}'


def forgery(self, now, info):
    """the desk found an edit (info: r, src, oartist, otitle, orig_len, edit_len, nightstep). Starts РАЗГОН."""
    r = float(info.get('r') or NC_GUESS)
    if not (NC_RANGE[0] <= r <= NC_RANGE[1]): r = NC_GUESS
    self.nc = dict(r=r, src=info.get('src', 'guess'), oartist=(info.get('oartist') or '').strip(), otitle=info.get('otitle') or '',
                   orig_len=info.get('orig_len'), edit_len=info.get('edit_len'), step_st=12 * math.log2(r), pv_end=info.get('pv_end'),
                   t0=now, kicks=0, slow=True, cut_t=None, sig_t0=None, sig_done=False, lost=0, lineups=0, line_t=-9, gone=False,
                   lk=None, sub=0, side=1, jolt=(0.0, 0.0), jolt_t=-9, jump=(0, 0), jump_t=-9, eye=0, twitch=None, twitch_t=-9,
                   next_twitch=0.0, held=None, held_t=-9, hist=[], words={}, last_txt=None, txt_t=-9, cut_said=False,
                   own=set(), maxpos=0.0, jumps=0, cuts=0, pk=-1, ph=-1, pv_said=set())
    log(f'hurt: {FORM_NAME} ПОДДЕЛКА ×{r:.2f} ({self.nc["src"]}) · '
        f'{self.nc["oartist"] or "?"} — {self.nc["otitle"] or "?"}' + (' · nightstep' if info.get('nightstep') else ''))


def forgery_r(self, r, src, orig_len=None, edit_len=None):
    """the desk found the original's length later: the ratio changes, РАЗГОН is not replayed."""
    nc = getattr(self, 'nc', None)
    if nc is None: return
    if not (NC_RANGE[0] <= r <= NC_RANGE[1]): log(f'hurt: {FORM_NAME} ПОДДЕЛКА: ×{r:.2f} out of range, stays ×{nc["r"]:.2f}'); return
    nc.update(r=r, src=src, orig_len=orig_len, edit_len=edit_len, step_st=12 * math.log2(r))
    log(f'hurt: {FORM_NAME} ПОДДЕЛКА ×{r:.2f} (original {_nc_fmt(orig_len)} from {src}, edit {_nc_fmt(edit_len)})')


def forgery_preview(self, now, artist=''):
    """▶ ПОДДЕЛКА: 22.6 s (h21; was 16) on a fake ×1.30 beat (143 bpm): РАЗГОН, ПОДПИСЬ, the speed layer, ОРИГИНАЛ, ОБРЫВ + ТОН, НЕ СТОИТ, the stolen time."""
    self.arc = None; self.jaw_t = None; self.jaw = None
    self.forgery(now, dict(r=1.30, src='preview', oartist=artist or 'ОРИГИНАЛ', otitle='', orig_len=195.0, edit_len=150.0, pv_end=now + NC_PV))
    log(f'hurt: {FORM_NAME} ПОДДЕЛКА preview')


def _nc_per(self):
    d = [b - a for a, b in zip(self.kicks, self.kicks[1:]) if 0.25 <= b - a <= 1.2]
    if len(d) < 3: return 0.5
    d.sort(); return d[len(d) // 2]


def _nc_shift(cells, dx, dy, pick=None):
    if not dx and not dy: return cells
    return [[x + dx, y + dy, w, h, c, a] if pick is None or pick(x, y) else [x, y, w, h, c, a] for x, y, w, h, c, a in cells]


def _nc_preview_sn(self, nc, now):
    """the fake song of the preview: a kick every 0.42 s, hats between, loud, then calm from 11.5 s."""
    el = now - nc['t0']; k = int(el / 0.42); h = int(el / 0.21)
    calm = 19.2 <= el < 21.2
    sn = dict(level=0.2 if calm else 0.8, kick=1.0 if k != nc['pk'] and not calm else 0.0, snare=0.0,
              hat=1.0 if h != nc['ph'] and not calm else 0.0)
    nc['pk'] = k; nc['ph'] = h
    for at, word in ((6.4, 'СЛЫШИШЬ.'), (7.2, 'СЛЫШИШЬ.'), (8.0, 'СЛЫШИШЬ.'), (8.8, 'СЛЫШИШЬ.')):
        if at <= el and at not in nc['pv_said']: nc['pv_said'].add(at); self.line = (word, now + 0.55)
    if el >= 21.4 and 'end' not in nc['pv_said']:
        nc['pv_said'].add('end'); txt = '−' + _nc_fmt(nc['orig_len'] - nc['edit_len']) + '.'
        nc['own'].add(txt); self.line = (txt, now + 1.5); self.said = now
    return sn, el


_nc_frame0 = Form.frame


def _nc_frame(self, rects, sn, now, **kw):
    nc = getattr(self, 'nc', None)
    if nc is not None and nc.get('pv_end') and now >= nc['pv_end']:
        self.nc = nc = None; log(f'hurt: {FORM_NAME} ПОДДЕЛКА preview over')
    if nc is None: return _nc_frame0(self, rects, sn, now, **kw)
    pv = bool(nc.get('pv_end')); el = None
    if pv:
        sn, el = self._nc_preview_sn(nc, now); kw['music'] = True; kw['ctx'] = None; kw['pos'] = None
    music = kw.get('music', False)
    if not music: return _nc_frame0(self, rects, sn, now, **kw)                 # no song, no forgery
    r = nc['r']
    if not nc['slow'] and self.arc is None and now - self.move_t > 22 / r: self.move_t = now - 23    # ТАКТ ×r: moves change sooner
    out, ov = _nc_frame0(self, rects, sn, now, **kw)
    try: return self._nc_layer(rects, out, ov, now, sn or {}, kw.get('pos'), pv, el)
    except Exception as e:
        if str(e) != getattr(self, 'nc_err', None): self.nc_err = str(e); log(f'hurt: ПОДДЕЛКА error: {e!r}')
        return out, ov


def _nc_layer(self, rects, out, ov, now, sn, pos, pv, el):
    nc = self.nc; r = nc['r']
    if pos: nc['maxpos'] = max(nc['maxpos'], pos)
    kick = bool(self.kick_now); hat = bool(self._hits.get('hat')) or bool(self._hits.get('snare'))
    lvl = sn.get('level', 0) or 0
    if kick:
        nc['kicks'] += 1
    if getattr(self, 'jaw_t', None) is not None or self.vanish: return out, ov            # ПАСТЬ and the silence keep their look
    # ---- РАЗГОН: the original speed for 2 bars, then the cut
    if nc['slow']:
        e = now - nc['t0']
        if (kick and (nc['kicks'] >= 8 or e > 5.0)) or e > 8.0:
            nc['slow'] = False; nc['cut_t'] = now; nc['sig_t0'] = now + 0.3
            txt = f'×{r:.2f}'; nc['own'].add(txt); self.line = (txt, now + 1.0); self.said = now; self.move_t = now - 23   # h21: said = no random line over it
            log(f'hurt: {FORM_NAME} РАЗГОН ×{r:.2f} (cut to speed after {e:.1f} s, {nc["kicks"]} kicks)')
        else:
            if nc['held'] is None or now - nc['held_t'] >= 0.25: nc['held'] = (out, ov); nc['held_t'] = now   # 4 snaps a second
            return nc['held']
    ov = list(ov)
    if now - nc['cut_t'] < 0.15: ov.append(('flash', (RED, 0.35)))
    ph = self.arc['ph'] if self.arc else None
    heavy = ph in ('soul', 'boom', 'build')
    under = [o for o in ov if o[0] == 'under']; ov = [o for o in ov if o[0] != 'under']
    rim = [c for o in under for c in o[1]]
    per = self._nc_per()
    if not heavy:
        # ---- ДВОЙНОЙ ШАГ / ПРЫЖОК / ВЗГЛЯД
        n = 4 if r >= 1.25 else 2; step = False
        if kick: nc['lk'] = now; nc['sub'] = 0; step = True
        elif nc['lk'] is not None and now - nc['lk'] < per * 1.5:
            s = int((now - nc['lk']) / (per / n))
            if s != nc['sub']: nc['sub'] = s; step = True
        if hat: step = True
        calm = getattr(self, 'part_feel', None) == 'calm' or lvl < 0.3
        if step and not calm:
            nc['side'] = -nc['side']; nc['jolt'] = (NC_JOLT * nc['side'], -NC_JOLT if nc['side'] > 0 else 0.0); nc['jolt_t'] = now
            nc['eye'] = self.rng.choice([v for v in (-3, -2, -1, 1, 2, 3) if v != nc['eye']])
            if ph is None and self.rng.random() < clamp((r - 1) * 2.2, 0.15, 0.6):
                nc['jump'] = (self.rng.choice(NC_JUMP), self.rng.choice((0, 0, -1))); nc['jump_t'] = now; nc['jumps'] += 1
        if now - nc['jolt_t'] > 0.5: nc['jolt'] = (0.0, 0.0)
        dx, dy = nc['jolt']
        if now - nc['jump_t'] < 0.1: dx += nc['jump'][0]; dy += nc['jump'][1]
        out = _nc_shift(out, dx, dy); rim = _nc_shift(rim, dx, dy); nc['off'] = (dx, dy)
        if nc['eye'] and now - nc['jolt_t'] < 0.5:
            def eye_cell(x, y, c): return c == RED and OY + 3.5 <= y < OY + 6.5 and OX + 1 + dx <= x < OX + 13 + dx
            out = [[clamp(x + nc['eye'], OX + 2 + dx, OX + 11 + dx), y, w, h, c, a] if eye_cell(x, y, c) else [x, y, w, h, c, a]
                   for x, y, w, h, c, a in out]
        # ---- НЕ СТОИТ: calm parts, it can't hold still
        if calm and ph is None:
            if now >= nc['next_twitch']:
                nc['next_twitch'] = now + self.rng.uniform(0.2, 0.3) / r
                nc['twitch'] = self.rng.choice(('horn', 'horn', 'foot', 'nudge', 'blink')); nc['twitch_t'] = now
                nc['tw_side'] = self.rng.choice((-1, 1))
            if now - nc['twitch_t'] < 0.08:
                t = nc['twitch']; sd = nc.get('tw_side', 1)
                if t == 'horn':
                    left = sd < 0
                    def pick(x, y): return y < OY + 0.5 and ((x < OX + 7) == left)
                    out = _nc_shift(out, 0.4 * sd, -0.2, pick); rim = _nc_shift(rim, 0.4 * sd, -0.2, pick)
                elif t == 'foot':
                    def pick(x, y): return y >= OY + 8 and ((x < OX + 7) == (sd < 0))
                    out = _nc_shift(out, 0, -0.4, pick); rim = _nc_shift(rim, 0, -0.4, pick)
                elif t == 'nudge':
                    out = _nc_shift(out, 0.2 * sd, 0); rim = _nc_shift(rim, 0.2 * sd, 0)
                else:
                    out = [c for c in out if not (c[4] == RED and OY + 3.5 <= c[1] < OY + 6.5)]
    # ---- СЛЕД: stale copies in fast parts
    nc['hist'] = [hst for hst in nc['hist'] if now - hst[0] < 0.3] + [(now, out)]
    fast = not heavy and (lvl > 0.55 or len([t for t in getattr(self, 'rh', []) if now - t < 1.0]) >= 4 or (pv and lvl > 0.5))
    trails = []
    if fast:
        for i, lag in enumerate((0.07, 0.14, 0.21)[:3 if r >= 1.25 else 2]):
            old = next((cells for t, cells in reversed(nc['hist']) if now - t >= lag), None)
            if old is not None and old is not out:
                trails = [[x, y, w, h, NC_TRAIL[i], 0.9] for x, y, w, h, c, a in old] + trails
    # ---- ОРИГИНАЛ: the ghost on the original tempo
    ghost = self._nc_ghost(rects, now, per, kick, pos, pv, el, ov)
    out = ghost + trails + out
    ov.append(('under', rim))
    # ---- ОБРЫВ + ТОН
    ov = [('shout', self._nc_shout(o[1], now)) if o[0] == 'shout' else o for o in ov]
    return out, ov


def _nc_ghost(self, rects, now, per, kick, pos, pv, el, ov):
    nc = self.nc; r = nc['r']
    if nc['gone'] or nc['cut_t'] is None: return []
    lagb = ((now - nc['cut_t']) / per) * (1 - 1 / r)
    want = int(lagb / NC_LINEUP)
    need = 0
    el_len = nc.get('edit_len') or 0
    if pos and el_len > 30: need = int(NC_ROWS * pos / (0.85 * el_len))
    if pv:
        want = 1 if el >= 6.0 else 0; want += 1 if el >= 10.4 else 0; need = 0
    if kick and (want > nc['lineups'] or need > nc['lost'] + 1):
        nc['lineups'] = max(nc['lineups'] + 1, want); nc['line_t'] = now
        nc['lost'] = min(NC_ROWS, max(nc['lost'] + (3 if pv else 1), need))
        ov.append(('flash', (RED, 0.2)))
        log(f'hurt: {FORM_NAME} ОРИГИНАЛ lines up ({nc["lineups"]}), loses a row: {NC_ROWS - nc["lost"]}/{NC_ROWS} left')
        if nc['lost'] >= NC_ROWS: nc['gone'] = True; log(f'hurt: {FORM_NAME} ОРИГИНАЛ is gone'); return []
    keep = NC_ROWS - 1 - nc['lost']
    sync = now - nc['line_t'] < 0.15
    gk = int((now - nc['cut_t']) / (per * r))                              # its own beat, r times slower
    gx = 0.0 if sync else NC_DX + (0.2 if gk % 2 else -0.2); gy = 0.0 if sync or gk % 2 == 0 else 0.4
    g = []
    for x, y, w, h, c, a in rects:
        if int(round(y - OY)) > keep: continue
        eye = OY + 4 <= y < OY + 6 and OX + 2 <= x < OX + 12 and c.upper() != '#07060D'
        g.append([x + gx, y + gy, w, h, NC_GHOST_EYE if eye else NC_GHOST, 0.85])
    return g


def _nc_shout(self, a, now):
    nc = self.nc; r = nc['r']; txt = a[0]
    if txt in nc['own'] or not txt: return a
    if txt != nc['last_txt'] or now - nc['txt_t'] > 0.2:                   # a new shout (the same one again after a 0.2 s gap)
        nc['words'][txt] = nc['words'].get(txt, 0) + 1; nc['last_txt'] = txt; nc['shout_t0'] = now
    nc['txt_t'] = now
    mark = ''
    body = txt
    for m in (' ♡', ' ✕'):
        if body.endswith(m): body, mark = body[:-len(m)], m
    letters = [i for i, ch in enumerate(body) if ch.isalpha()]
    out = body
    if len(letters) >= 4:
        ncut = max(1, int(round(len(letters) * (r - 1) * 1.2)))
        cut = letters[-ncut]
        out = body[:cut]
        if now - nc.get('shout_t0', now) < 0.1: out += random.Random(txt).choice(GLYPHS)     # the cut letter flickers once
        if not nc['cut_said']: nc['cut_said'] = True; log(f'hurt: {FORM_NAME} ОБРЫВ: «{body}» → «{body[:cut]}»')
        nc['cuts'] += 1
    step = max(1, int(round(nc['step_st'] / 2)))
    lift = min(6, (nc['words'][txt] - 1) * step)
    fg = a[3] if len(a) > 3 else '#E4E0EA'; bg = a[4] if len(a) > 4 else '#FF5C8A'
    return (out + mark, a[1], a[2] if len(a) > 2 else 1.0, fg, bg, lift)


def _nc_ahead(self, sn, now):
    """ВПЕРЕДИ (h7), ×r on an edit: 40-120 ms early instead of 30-90 (ПРИМАНКА 60-120 → up to 150)."""
    nc = getattr(self, 'nc', None)
    r = nc['r'] if nc is not None and not nc['slow'] else 1.0
    sn = dict(sn or {}); k = sn.get('kick', 0) or 0
    if k >= 0.5 and k > self.kprev + 0.2: self.kicks = [t for t in self.kicks if now - t < 6][-8:] + [now]
    self.kprev = k
    d = [b - a for a, b in zip(self.kicks, self.kicks[1:]) if 0.25 <= b - a <= 1.2]
    if len(d) >= 4:
        d.sort(); med = d[len(d) // 2]; mad = sorted(abs(x - med) for x in d)[len(d) // 2]
        if mad < 0.12 * med:
            nxt = self.kicks[-1] + med
            while nxt < now - 0.05: nxt += med
            key = round(nxt, 2)
            lead = (self.rng.uniform(0.06, 0.12) if self._lure_on(now) else self.rng.uniform(0.03, 0.09)) * r
            lead = min(lead, 0.15)
            if key != self.pre_for and nxt - lead <= now < nxt + 0.1:
                self.pre_for = key; self.pre = now
    if self.pre is not None and now - self.pre < 0.2: sn['kick'] = 1.0
    return sn


_nc_act0 = Form._act_pick


def _nc_act_pick(self, now, music, fail=None):
    a = _nc_act0(self, now, music, fail)
    nc = getattr(self, 'nc', None)
    if nc is None or not a or a.get('fail') or nc['slow']: return a
    r = nc['r']; dur = (a['end'] - a['t0']) / r
    if music and self.rng.random() < min(0.7, (r - 1) * 2):
        dur *= 0.5; a['cut'] = True; log(f'hurt: {FORM_NAME} НЕ ДОСЛУШАЛ (drops {ACT_RU.get(a["name"], a["name"].upper())} halfway)')
    a['end'] = a['t0'] + dur; self.mimic = a['end']
    return a


_nc_mimic0 = Form.mimic_tick


def _nc_mimic_tick(self, now, music):
    before = self.next_mimic
    res = _nc_mimic0(self, now, music)
    nc = getattr(self, 'nc', None)
    if nc is not None and not nc['slow'] and self.next_mimic != before and self.next_mimic > now:
        self.next_mimic = now + (self.next_mimic - now) / nc['r']            # the next act comes r times sooner
    return res


_nc_label0 = Form.label


def _nc_label(self):
    s = _nc_label0(self); nc = getattr(self, 'nc', None)
    if nc is None: return s
    now = time.time(); tag = f'  ×{nc["r"]:.2f}'
    if nc['slow'] or nc['sig_t0'] is None or now < nc['sig_t0']:
        name = (nc['oartist'] or 'ОРИГИНАЛ').upper()[:18]
        return name + s[len(FORM_NAME):]
    if nc['sig_done']: return s + tag
    orig = (nc['oartist'] or 'ОРИГИНАЛ').upper()[:18]; L = max(len(orig), len(NC_TARGET)); tgt = NC_TARGET.ljust(L); orig = orig.ljust(L)
    dur = clamp(0.3 / max(0.01, nc['r'] - 1), 0.8, 3.0)
    k = int(L * (now - nc['sig_t0']) / dur)
    if k >= L:
        nc['sig_done'] = True; log(f'hurt: {FORM_NAME} ПОДПИСЬ: {orig.strip()} → {NC_TARGET} ({dur:.1f} s)')
        return s + tag
    g = GLYPHS[int(now * 20) % len(GLYPHS)]
    name = (tgt[:k] + g + orig[k + 1:]).rstrip()
    return name + s[len(FORM_NAME):]


_nc_song0 = Form.song


def _nc_song(self, now, key, dg=False, steroids=False, lure=False):
    nc = getattr(self, 'nc', None)
    if nc is not None and not nc.get('pv_end'):
        ol, ed = nc.get('orig_len'), nc.get('edit_len')
        if ol and ed and nc['maxpos'] >= 0.5 * ed and ol - ed >= 3:          # УКРАДЕННОЕ ВРЕМЯ
            stolen = ol - ed; txt = '−' + _nc_fmt(stolen) + '.'
            self.line = (txt, now + 2.4); self.said = now
            st = self.state()
            if st:
                h = self.hunger(); st['hunger'] = round(min(1.0, h + min(0.12, stolen / 400)), 2); self.mem.save()
                log(f'hurt: {FORM_NAME} УКРАДЕННОЕ ВРЕМЯ {txt} (fed, hunger {st["hunger"]:.2f})')
            else: log(f'hurt: {FORM_NAME} УКРАДЕННОЕ ВРЕМЯ {txt}')
        log(f'hurt: {FORM_NAME} ПОДДЕЛКА over: {nc["jumps"]} jumps, {nc["cuts"]} cut shouts, ОРИГИНАЛ {NC_ROWS - nc["lost"]}/{NC_ROWS} rows left')
    _nc_song0(self, now, key, dg=dg, steroids=steroids, lure=lure)
    if nc is not None and not nc.get('pv_end'): self.nc = None
    elif not hasattr(self, 'nc'): self.nc = None


Form.nc = None
Form.forgery = forgery
Form.forgery_r = forgery_r
Form.forgery_preview = forgery_preview
Form._nc_per = _nc_per
Form._nc_preview_sn = _nc_preview_sn
Form._nc_layer = _nc_layer
Form._nc_ghost = _nc_ghost
Form._nc_shout = _nc_shout
Form._ahead = _nc_ahead
Form._act_pick = _nc_act_pick
Form.mimic_tick = _nc_mimic_tick
Form.label = _nc_label
Form.song = _nc_song
Form.frame = _nc_frame
# <<< h20 ПОДДЕЛКА + НЕТЕРПЕНИЕ
