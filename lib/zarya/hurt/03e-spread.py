# ДЕМОН · concept + direction: ШУМ (shum) · built with Claude (Anthropic)
# >>> h22 ПОДДЕЛКА's pieces on other songs (mint-pack v56). ШУМ 2026-11-07 22:49 asked whether the new animations work on any
#     song (they were nightcore-only); 22:52 "i like it lets make it happen" for the three spreads Claude proposed:
#   1  ВЗРЫВЫ     every hard song (not an edit) blasts in turns: the old one (classic), ПЕРЕМОТКА, ПИТЧ, КОНФЕТТИ, at normal
#                 speed (r = 1). Random start per song. ДЕЛИКАТЕС songs (Death Grips grammar) skip КОНФЕТТИ.
#   2  ПРИМАНКА   on lure songs (and the ▶ ПРИМАНКА preview) УШКИ in choruses, ЗВЁЗДОЧКИ on hats, СЕРДЕЧКО in sung parts
#                 whenever the mask is off (the mask still wins its cute parts).
#   3  ПЫЛЬ/СБОЙ  loud parts (level > 0.6) of any song: dust and rain at normal speed, at most 30 dust / 5 drops (an edit: 70 / 14), gone in calm
#                 parts. Kept lighter so a nightcore edit still looks different (Claude's call, 22:52).
#   Off: right-click > ▶ Animations > On their own > «ПОДДЕЛКА · its pieces on other songs» (`nc_spread`, desk d39).
#   Edits are untouched: while Form.nc is on, h20 / h21 do everything.
SP_KINDS = ('classic', 'rewind', 'pitch', 'confetti')
SP_RU = dict(NC2_RU, classic='обычная')


def _sp_state(self, now):
    s = getattr(self, 'sp', None)
    if s is None or s.get('song') != self.song_key:
        s = self.sp = dict(song=self.song_key, k=0, conf=[], spark=[], dust=[], rain=[], dust_t=now, rain_t=now, ears=False, ears_t=-9,
                           loud_since=None, heart_crack=-9, snaps=[], rw=None, wrong=[], ear_flick=(0, -9), said=set(),
                           kind_i=self.rng.randrange(len(SP_KINDS)))
    return s


_sp_frame0 = Form.frame


def _sp_frame(self, rects, sn, now, **kw):
    out, ov = _sp_frame0(self, rects, sn, now, **kw)
    if getattr(self, 'nc', None) is not None or not getattr(self, 'spread', True): return out, ov
    music = kw.get('music', False); a = self.arc; ph = a['ph'] if a else None
    lpv = now < getattr(self, 'lure_pv', 0) and not getattr(self, 'lure', False)
    if not (music or (a and a.get('pv')) or lpv): return out, ov
    if getattr(self, 'jaw_t', None) is not None or self.vanish: return out, ov
    if kw.get('dance') is not None and self.mimic_on(now): return out, ov                       # МИМИКРИЯ draws his dance
    try: return self._sp_layer(out, ov, now, sn or {}, music, lpv, a, ph)
    except Exception as e:
        if str(e) != getattr(self, 'sp_err', None): self.sp_err = str(e); log(f'hurt: spread error: {e!r}')
        return out, ov


def _sp_layer(self, out, ov, now, sn, music, lpv, a, ph):
    s = self._sp_state(now)
    lvl = (sn.get('level', 0) or 0) if music else 0.0; kick = bool(self.kick_now) and music; hat = bool(self._hits.get('hat')) and music
    heavy = ph in ('soul', 'boom', 'build'); ctx = self.ctx or {}
    if kick: s['k'] += 1
    # ---- 1 the blast styles: ПЕРЕМОТКА playback + its wrong pixel
    if a and a.get('sp_kind') == 'rewind':
        if ph == 'boom': s['snaps'].append(out); del s['snaps'][:-40]
        elif ph == 'build':
            if s['rw'] is None: s['rw'] = now
            i = len(s['snaps']) - 1 - int((now - s['rw']) * 30 * 2)
            if i >= 0 and s['snaps']:
                out = s['snaps'][i] if i % 3 else s['snaps'][max(0, i - 1)]
                ov = [o for o in ov if o[0] not in ('under', 'glyphs')] + [('flash', (NC2_RAIN_TAIL, 0.25))]
            elif not a.get('sp_wrong'):
                a['sp_wrong'] = True; body = _nc2_body(out) or [[OX + 6, OY + 5, 1, 1, INK, 1.0]]; c = self.rng.choice(body)
                s['wrong'] = (s['wrong'] + [(c[0] - OX, c[1] - OY, self.rng.choice((-2, -1, 1, 2)), self.rng.choice((-1, 0, 1)))])[-3:]
                log(f'hurt: {FORM_NAME} ПЕРЕМОТКА: rebuilt, one pixel in the wrong place')
    else: s['snaps'] = []; s['rw'] = None
    wrong = []
    for wx, wy, mx, my in s['wrong']:
        bx, by = OX + wx, OY + wy
        out = [c for c in out if not (c[4] in NC2_BODY and abs(c[0] - bx) < 0.3 and abs(c[1] - by) < 0.3)]
        wrong += [[bx + mx, by + my, 1, 1, INK, 1.0], [bx + mx + 0.2, by + my + 0.2, 0.6, 0.6, RED, 0.9]]
    conf = self._nc2_confetti(now, s)
    # ---- 2 ПРИМАНКА: ears, sparkles, heart
    sp = []
    if (self._lure_on(now)) and not heavy:
        if lpv: chorus = True
        elif ctx: chorus = bool(ctx.get('chorus'))
        else:
            if lvl > 0.7: s['loud_since'] = s['loud_since'] or now
            else: s['loud_since'] = None
            chorus = s['loud_since'] is not None and 8.0 <= now - s['loud_since'] < 24.0
        if chorus != s['ears']:
            s['ears'] = chorus; s['ears_t'] = now
            if chorus and 'ears' not in s['said']: s['said'].add('ears'); log(f'hurt: {FORM_NAME} УШКИ on (ПРИМАНКА)')
        if s['ears'] or now - s['ears_t'] < 0.06:
            if (hat or (lpv and int(now * 6) % 7 == 0)) and self.rng.random() < 0.25: s['ear_flick'] = (self.rng.choice((-1, 1)), now)
            out, ov = self._nc2_ears(out, ov, now, (0.0, 0.0), now - s['ears_t'] < 0.06, s)
        voice = (ctx.get('voice') or 0) >= 0.5 if ctx else (lpv or 0.35 <= lvl <= 0.75)
        mask = getattr(self, 'face', None) is True and not getattr(self, 'mask_off', False)
        if voice and not mask:
            if kick and lvl >= 0.85: s['heart_crack'] = now
            out = self._nc2_heart(out, now, now - s['heart_crack'] < 0.25)
        tick = hat or (lpv and int(now * 8) != int((now - 1 / 30) * 8))
        if tick and len(s['spark']) < 6 and self.rng.random() < 0.35:
            x = self.rng.choice((self.rng.uniform(OX - 4, OX - 1), self.rng.uniform(OX + 14, OX + 16))) if self.rng.random() < 0.6 else self.rng.uniform(OX, OX + 13)
            y = self.rng.uniform(OY - 5, OY - 1) if OX <= x <= OX + 13 else self.rng.uniform(OY - 4, OY + 8)
            s['spark'].append(dict(x=round(x), y=round(y), t=now, col=self.rng.choice((SWEET, BONE, BLUSH))))
    elif s['ears']: s['ears'] = False; s['ears_t'] = now
    for z in s['spark']:
        u = now - z['t']
        if u < 0.08: sp.append([z['x'] + 0.5, z['y'] + 0.5, 0.5, 0.5, BONE, 0.9])
        elif u < 0.28: sp += [[z['x'] + dx * 0.5, z['y'] + dy * 0.5, 0.5, 0.5, BONE if (dx, dy) == (1, 1) else z['col'], 0.95] for dx, dy in STAR3]
        elif u < 0.33: sp.append([z['x'] + 0.5, z['y'] + 0.25, 0.5, 1.0, RED, 1.0])
    s['spark'] = [z for z in s['spark'] if now - z['t'] < 0.33]
    # ---- 3 ПЫЛЬ / СБОЙ, lighter, loud parts only
    le = (lvl - 0.2) if music and lvl > 0.6 else 0.0
    if le and 'dust' not in s['said']: s['said'].add('dust'); log(f'hurt: {FORM_NAME} ПЫЛЬ / СБОЙ (loud part, normal speed)')
    back = self._nc2_dust_rain(now, s, le, kick, 1.0, dust_cap=30, rain_cap=5)        # about half of an edit's 70 / 14
    return back + list(out) + wrong + conf + sp, ov


_sp_boom0 = Form._boom


def _sp_boom(self, now, a, lvl):
    _sp_boom0(self, now, a, lvl)
    if getattr(self, 'nc', None) is not None or not getattr(self, 'spread', True): return
    s = self._sp_state(now)
    kinds = [k for k in SP_KINDS if not (k == 'confetti' and getattr(self, 'dg', False))]
    kind = kinds[s['kind_i'] % len(kinds)]; s['kind_i'] += 1
    a['sp_kind'] = kind
    if kind == 'pitch':
        for sh in self.shards:
            row = sh[1] - OY; side = 1 if int(round(row)) % 2 else -1
            sh[6] = side * (5 + (10 - row) * 1.8); sh[7] = -self.rng.uniform(1, 4)
    elif kind == 'confetti':
        n = self.rng.randint(12, 16); mx = OX + 7
        s['conf'] += [dict(x=mx + self.rng.uniform(-4, 4), y=OY + self.rng.uniform(2, 7), vx=self.rng.uniform(-14, 14), vy=-self.rng.uniform(10, 22),
                           g=30, last=now, t=now, landed=None, shape=self.rng.choice(('heart', 'heart', 'star')),
                           col=self.rng.choice((SWEET, BONE, BLUSH))) for _ in range(n)]
    log(f'hurt: {FORM_NAME} ДЕТОНАЦИЯ style: {SP_RU[kind]}')


Form.spread = True
Form._sp_state = _sp_state
Form._sp_layer = _sp_layer
Form.frame = _sp_frame
Form._boom = _sp_boom
# <<< h22
