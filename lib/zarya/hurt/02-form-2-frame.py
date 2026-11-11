class _Form2:     # mixin of Form (v35 split; one class in the original)

    def frame(self, rects, sn, now, eye='#8FD9A8', mouse=None, music=False, dance=None, ctx=None, pos=None, lyr=None):
        """h7: the h6 frame + Death Grips grammar. ctx: the song brain's map context (None = no map), pos: song position (s),
        lyr: the current synced lyric line (raw). Returns (rects, overlays)."""
        self.ctx = ctx if music else None
        if music: self._ear(sn, now, (sn or {}).get('level', 0) or 0)                         # h8: real hits
        else: self.kick_now = False
        if music: sn = self._ahead(sn, now)                                                    # ВПЕРЕДИ
        out, ov = self._frame(rects, sn, now, eye=eye, mouse=mouse, music=music, dance=dance)
        if dance is not None and self.mimic_on(now):                                            # МИМИКРИЯ stays a beat late
            return self._jaw(out, ov, now, rects) if getattr(self, 'jaw_t', None) is not None else (out, ov)      # h12: ПАСТЬ
        lvl = (sn or {}).get('level', 0) or 0 if music else 0.0
        hit = self._hit; vocal = music and (self._hits.get('snare') or lvl - self.lvl_prev > 0.22)
        self._arc_tick(now, sn or {}, ctx, pos, music, lvl)
        blk, extra, eyes, rim = [list(p) for p in self._parts]
        ov = [o for o in ov if o[0] != 'under']
        a = self.arc; ph = a['ph'] if a else None
        krik = None
        # ---- ПРОПУСК: a section cut = 3 repeated frames, then a jump; silence after a hit = it is gone
        if music and ctx and ctx.get('new_sec') and (pos or 0) > 10 and self.skips < (5 if self._lure_on(now) else 3) and a is None:
            self.skips += 1; self.hold_n = 3; self.skip_t = now; log(f'hurt: {FORM_NAME} ПРОПУСК (section cut)')
        if music and a is None:
            if lvl > 0.7: self.loud_t = now
            if not self.vanish and self.vanishes < 3 and now - self.loud_t < 1.0 and lvl < 0.12 and (pos or 0) > 10 and now - self.vanish_t > 4.0:
                self.vanish = True; self.vanishes += 1; self.vanish_t = now; log(f'hurt: {FORM_NAME} ПРОПУСК (gone in the silence)')
            elif self.vanish and (hit or lvl > 0.4): self.vanish = False
        elif self.vanish: self.vanish = False
        if self.hold_n > 0 and self.last is not None:
            self.hold_n -= 1; self.lvl_prev = lvl; return self.last
        # ---- ГНИЛЬ: a long hard song rots it
        if music and self.hard and pos is not None: self.rot = max(self.rot, clamp((pos - 60) / 240))
        if self.rot > 0.05 and ph not in ('boom', 'build'):
            r = random.Random(int(now * 6)); rk = self.rot
            blk = [[math.floor(x / 2) * 2, math.floor(y / 2) * 2, 2, 2, c, al] if r.random() < 0.35 * rk else [x, y, w, h, c, al] for x, y, w, h, c, al in blk]
            rim = [[x, y, w, h, c, al * (1 - 0.5 * rk)] for x, y, w, h, c, al in rim]
            dr = random.Random(self.song_key or 'x')
            extra += [[OX + dr.randint(1, 12), OY + dr.randint(1, 9), 1, 1, BONE, 0.85] for _ in range(int(rk * 12)) if r.random() < 0.9]
        # ---- ГЛОТКА: the voice clips the visor
        if music and ctx and (ctx.get('voice') or 0) >= 0.6 and a is None:
            if lvl < 0.35:
                blk, extra, eyes, rim = [[[x, y + (1 if y < OY + 8 else 0), w, h, c, al] for x, y, w, h, c, al in p] for p in (blk, extra, eyes, rim)]
                eyes = [[x, y, w, h, c, al * 0.4] for x, y, w, h, c, al in eyes]
            elif vocal:
                eyes = eyes + [[OX + 2 + k, OY + 4, 1, 2, BONE, 1.0] for k in range(10)]
        # ---- the hype arc
        if ph == 'smell':
            if a['frozen'] is None: a['frozen'] = (blk, extra)
            blk, extra = a['frozen']
            j = self.rng.choice((-0.4, 0, 0.4))
            rim = [[x + j, y, w, h, c, al] for x, y, w, h, c, al in rim]
            eyes = [[OX + 6.5, OY + 4.5, 1, 1, RED, 1.0]]
        elif ph == 'wind':
            k = a.get('k', 0.0)
            if self.last is not None and self.rng.random() < 0.08 + 0.45 * k:
                self.lvl_prev = lvl; return self.last                                          # frames drop as it builds
            d = self.rng.choice((-1, 1)) * 0.2 * self.rng.randint(0, 1 + int(k * 4))
            blk, extra, eyes, rim = [[[x + d, y, w, h, c, al] for x, y, w, h, c, al in p] for p in (blk, extra, eyes, rim)]
            extra += [[OX + 3 + round(self.rng.random() * 40) / 5, OY - 3 + round(self.rng.random() * 15) / 5, 0.6, 0.6,
                       RED if self.rng.random() < 0.6 else PINK, 0.85] for _ in range(int(2 + 9 * k))]
            krik = ('ЕДА.' if k < 0.4 else 'ГРОМЧЕ' if k < 0.75 else 'ЕЩЁ ЕЩЁ ЕЩЁ', 1.0, 1.0 + 0.4 * k)
        elif ph in ('soul', 'boom', 'build'):
            el = now - a['t']
            up = min(3, 1 + int(el / 0.2)) if ph == 'soul' else 4
            if 'soul_at' not in a: a['soul_at'] = self._outline(blk)
            sa = 1.0 if ph == 'soul' else 0.5 + 0.2 * (int(now * 12) % 2)                    # over the debris it flickers
            soul = [[x, y - up + (self.rng.choice((-0.2, 0, 0.2)) if ph != 'soul' else 0), 1, 1, RED, sa] for x, y in a['soul_at']]
            if ph == 'build' and a['slam'] is not None: soul = []
            tether = [[OX + 6.7, y, 0.4, 0.4, PINK, 0.6] for y in range(OY - up + 1, OY + 1)] if ph == 'soul' else []
            if ph == 'soul':
                eyes = [[x, y, w, h, c, al * 0.3] for x, y, w, h, c, al in eyes]; rim = []
                extra = [e for e in extra if e[4] == FLY]
            elif ph == 'boom':
                u = el / 1.1; horns = a['size'] == 'horns'
                if el < 0.12:
                    blk = [[x, y, w, h, BONE, 1.0] for x, y, w, h, c, al in blk]; extra = []; eyes = []; rim = []
                    ov.append(('flash', ('#FFFFFF', 0.9)))
                else:
                    sh = self._shard_tick(now)
                    if horns: blk = [c for c in blk if c[1] >= OY] + sh; rim = [c for c in rim if c[1] >= OY]
                    else: blk = sh; eyes = []; rim = []; extra = []
                    rim += [[x + dx, y + dy, w, h, RED, 0.9] for x, y, w, h, c, al in sh for dx, dy in ((-0.2, 0), (0.2, 0), (0, -0.2), (0, 0.2))]
                    for rr in ((0.0, 1.0),) + (((0.15, 0.8),) if a['size'] == 'god' else ()):
                        uu = max(0.0, (el - 0.12 - rr[0]) / 0.9)
                        if 0 < uu < 1:
                            rad = uu * (5 if horns else 13); cx = OX + 7
                            for sx_ in (-1, 1):
                                xr = round((cx + sx_ * rad) * 5) / 5
                                if 0 <= xr <= PW - 1: extra.append([xr, OY + 9.4, 2 if not horns else 1, 0.6, RED, rr[1] * (1 - uu)])
                    if a['size'] == 'god' and el < 0.5: ov.append(('flash', (RED, 0.35 * (1 - el / 0.5))))
            else:                                                                               # build
                sh = self._shard_tick(now); back = set(a['back'])
                mid = self._mid(blk); hz = a['size'] == 'horns'
                def q(c): return self._q(c, mid, hz)
                if a['size'] == 'horns':
                    blk = [c for c in blk if c[1] >= OY or q(c) in back] + [s for s, s0 in zip(sh, self.shards) if s0[9] not in back]
                    rim = [c for c in rim if c[1] >= OY or q(c) in back]
                else:
                    blk = [c for c in blk if q(c) in back] + [s for s, s0 in zip(sh, self.shards) if s0[9] not in back]
                    eyes = [c for c in eyes if q(c) in back]; rim = [c for c in rim if q(c) in back]
                    extra = [c for c in extra if c[4] == FLY or q(c) in back]
                rim += [[x + dx, y + dy, w, h, RED, 0.9] for (x, y, w, h, c, al), s0 in zip(sh, self.shards) if s0[9] not in back
                        for dx, dy in ((-0.2, 0), (0.2, 0), (0, -0.2), (0, 0.2))]
                if a['slam'] is not None:
                    ov.append(('flash', (RED, 0.45)))
                    krik = ('РЕКОРД' if a.get('record') else 'ЕЩЁ.', 1.0, 1.3)
            extra = extra + soul + tether
        # ---- БРИКВОЛЛ: a crushed master flattens it between two lines
        cr_ = (ctx or {}).get('crush') if music else None
        if cr_ is not None and cr_ >= 0.3 and ph not in ('boom', 'build'):
            ceil = OY - 3 + round(3 * cr_)
            blk, extra, eyes, rim = [[[x, max(y, ceil), w, h - max(0, ceil - y) if h > 1 else h, c, al] for x, y, w, h, c, al in p] for p in (blk, extra, eyes, rim)]
            if self._hits.get('kick'):
                extra += [[OX - 1, ceil - 0.3, 16, 0.2, PINK, 0.3], [OX - 1, OY + 10, 16, 0.2, PINK, 0.3]]
        # ---- h9: ПРИМАНКА
        lure = self._lure_on(now); dark_hit = False
        if lure and ph not in ('soul', 'boom', 'build'):
            blk, extra, eyes, rim, dark_hit = self._lure_layer(now, ctx, lvl, music, blk, extra, eyes, rim)
        if lure and ph == 'boom' and not self.mask_off: self.mask_off = True; self.cracks = min(6, self.cracks + 1)
        # ---- КРИК: the red line follows the song
        if krik is None and ph in ('soul', 'boom'): self.line = None
        if krik is None and music and ctx and ctx.get('chorus') and (ctx.get('voice') is None or ctx['voice'] >= 0.4) and a is None:
            if vocal and now - self.krik_t > 0.22:
                self.krik_t = now; self.krik_w = (self._word(lyr), now, 0.8 + 0.8 * clamp(lvl))
            if self.krik_w and now - self.krik_w[1] < 0.5:
                krik = (self.krik_w[0], clamp((0.5 - (now - self.krik_w[1])) / 0.2), self.krik_w[2])
        if krik is not None and lure:                                                         # h9: СЛАДКИЙ КРИК
            w_ = krik[0].rstrip('.')
            krik = (w_.upper() + ' ✕', krik[1], krik[2] * 1.1, RED, INK) if dark_hit or ph in ('wind',) or self.face is False else (w_.lower() + ' ♡', krik[1], krik[2], SWEET, RED)
        if krik is not None: ov = [o for o in ov if o[0] != 'shout'] + [('shout', krik)]
        if ph in ('soul', 'boom'): ov = [o for o in ov if o[0] not in ('glyphs', 'shout')]
        extra += self._flies(now, music)
        self.lvl_prev = lvl
        if self.vanish:                                                                         # only the shout hangs in the black
            res = ([], [o for o in ov if o[0] == 'shout'])
        else:
            res = (blk + extra + eyes, ov + [('under', rim)])
        self.last = res
        return res

