class _Demon4:     # mixin of Demon (v35 split; one class in the original)

    # --- drawing ---
    def draw(self, w, cr):
        cr.set_operator(cairo.OPERATOR_SOURCE); cr.set_source_rgba(0, 0, 0, 0); cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)
        U, oy = self.U, self.WH - self.SH
        now = time.time()
        st = self.state(); rects = ZD.build(st); ov = []; hide = False
        mimic = bool(self.form_on() and self.form.mimic_tick(now, self.dancing()))                      # d19: МИМИКРИЯ
        dancing = st['mode'] == 'idle' and self.dancing() and not (self.hurt and self.hurt.silence(now)) and (not self.form_on() or mimic) \
                  and not (self.stand is not None and self.stand.phase in ('fight', 'climax'))                 # d10 / d11 / d14
        if dancing:
            try:
                sn = dict(self.ear.ear.snap); sn['progress'] = self.music.progress()
                if self.brain:                                                               # d20: what the map knows
                    b = self.bctx = self.brain.ctx(self.music.position())
                    if b:
                        if b['sec'] is not None: sn['section'] = 1000 + b['sec']             # moves change at real sections
                        di = b['drop_in']
                        if di is not None and 0 < di <= 4: sn['build'] = max(sn.get('build', 0) or 0, 1 - di / 4)    # wind-up
                        if di is not None and -0.15 <= di <= 0: sn['drop_t'] = now           # lands on the drop, on time
                        sn['chorus'] = b['chorus']
                self.pos_ctx = self.music.position()
                mode, var, _ = self.cur_mode()
                if mimic and hasattr(self, 'mimic_mode'): mode, var, sn = self.mimic_mode(mode, var, sn, now)      # d32: the act it picked
                wthr = self.cur_weather()[0]; peak = (self.srule or {}).get('peak')
                if ZH and self.hurt:                                                         # d10: hard songs: possession or nails
                    hard = ZH.is_hard(mode, var, wthr, peak, ZM.CALM)
                    rt = ZH.route(f'{self.music.artist()}|{self.music.title()}', peak) if hard else None
                    if rt == 'nails' and self.cfg.get('nails', '0') != '1': rt = 'possess'      # d12: nails archived
                    self.route = (hard, rt)
                    if rt == 'nails': peak = 'nails'
                    elif rt == 'possess' and self.descent_ok(now): peak = 'descend'         # d11: the hand takes him instead
                    if self.epic_song(): peak = 'stand'; self.route = (False, 'stand')       # d14: epic songs stand, never ПОДМЕНЫШ
                ctx = dict(weather=wthr, pos=self.pos_ctx if self.pos_ctx is not None else -1,
                           cues=(self.srule or {}).get('cues') or [], breach_gap=self.cfg.get('breach_gap', '45'), hooks=self.hooks,
                           peak=peak, ritual=self.ritual(), possess_gap=self.cfg.get('possess_gap', '60'),
                           force_possess=self.take_force_possess())
                rects, ov, hide = self.dance.draw(rects, mode, var, sn, now, st.get('eye') or ZD.C['G'], ctx)
                if mimic and hasattr(self, 'mimic_after'): rects, ov, hide = self.mimic_after(rects, ov, hide, now, st, sn)   # d32
                b = self.bctx
                if b and b.get('chorus') and (b.get('voice') or 0) >= 0.6 and (sn.get('level') or 0) > 0.25 and not hide:   # d21: he sings
                    eye = st.get('eye') or ZD.C['G']; lv = sn.get('level') or 0
                    rects = [r for r in rects if not (ZD.OY + 4 <= r[1] < ZD.OY + 6 and ZD.OX + 2 <= r[0] < ZD.OX + 12 and r[4] != '#07060D')]
                    for k in range(10):
                        a = lv * (0.55 + 0.45 * math.sin(now * 17 + k * 1.3) * math.sin(now * 5.3 + k * 0.7))
                        y = ZD.OY + (4.5 if abs(a) < 0.3 else 4 if a > 0 else 5)
                        rects.append([ZD.OX + 2 + k, y, 1, 1 if abs(a) >= 0.3 else 0.6, eye, 1.0])
                        if abs(a) > 0.62: rects.append([ZD.OX + 2 + k, ZD.OY + (5 if a > 0 else 4), 1, 1, eye, 0.8])
                self.fx_err = None
            except Exception as e:
                if str(e) != self.fx_err: self.fx_err = str(e); log(f'music: frame error: {e!r}')
                rects, ov, hide = ZD.build(st), [], False
        if self.stand is not None and st['mode'] in ('idle', 'sleep', 'work', 'poke', 'alert') and not self.form_on():   # d14
            try:
                sn_ = self.ear.ear.snap if self.ear and self.ear_on else {}
                if self.stand.phase in ('fight', 'climax'): rects, ov = self.stand.frame(ZD.build(dict(st, mode='idle')), [], now, sn_); hide = False
                else: rects, ov = self.stand.after(rects, ov, now)
            except Exception as e:
                if str(e) != getattr(self, 'stand_err', None): self.stand_err = str(e); log(f'hurt: stand frame error: {e!r}')
        say = getattr(self.react, 'say', None)                                                         # d23: godlike only
        if say and now < say[1] and not self.form_on() and not hide:
            ov = [o for o in ov if o[0] != 'shout'] + [('shout', (say[0], max(0.0, min(1.0, (say[1] - now) / 0.5))))]
        if self.form_on() and st['mode'] in ('idle', 'sleep', 'work', 'poke', 'alert'):                       # d11: ПОДМЕНЫШ moves its own way
            try:
                ox, oy_ = self.get_position(); ex = ox + (ZD.OX + 7) * self.U; ey = oy_ + self.WH - self.SH + (ZD.OY + 5) * self.U
                mouse = ((self.mouse[0] - ex) / self.U, (self.mouse[1] - ey) / self.U) if self.mouse else None
                live = self.ear_on and self.music.playing()
                kw = {}
                if hasattr(self.form, 'set_targets'):                                                        # d23 (zarya-hurt h7+)
                    b_ = None
                    if self.brain and live:
                        b_ = self.bctx = self.brain.ctx(self.music.position())
                        if b_ is not None and self.form.targets is None and self.form.det_max > 0:
                            kw_ = dict(drops_only=True) if getattr(self.form, 'drop_only', False) else {}                # d24
                            self.form.set_targets(self.brain.targets(self.form.det_max, 60 if self.form.steroids else 40, **kw_))
                    kw = dict(ctx=b_, pos=self.music.position() if live else None, lyr=self.lyric_raw() if live else None)
                rects, ov = self.form.frame(ZD.build(dict(st, mode='idle')), self.ear.ear.snap if live else None, now, mouse=mouse, music=bool(live),
                                           dance=rects if mimic else None, **kw)
                hide = False
            except Exception as e:
                if str(e) != getattr(self, 'form_err', None): self.form_err = str(e); log(f'hurt: form frame error: {e!r}')
        if not hide and self.vol_show and now - self.vol_show[1] < 1.6:          # d5: the visor is the volume meter
            lvl = self.vol_show[0] or 0; n = int(round(lvl / 10))
            rects = [r for r in rects if not (ZD.OY + 4 <= r[1] < ZD.OY + 6 and ZD.OX + 2 <= r[0] < ZD.OX + 12 and r[4] != '#07060D')]
            for k in range(10):
                c = ZD.C['G'] if k < n else ZD.C['dim']
                rects += [[ZD.OX + 2 + k, ZD.OY + 4, 1, 1, c, 1.0 if k < n else 0.6], [ZD.OX + 2 + k, ZD.OY + 5, 1, 1, c, 1.0 if k < n else 0.6]]
        if now < self.love_until:                                                  # liked: little hearts pop
            u = 1 - (self.love_until - now) / 1.8
            for k, x0 in enumerate((ZD.OX + 1, ZD.OX + 8, ZD.OX + 13)):
                y0 = ZD.OY - 1 - u * 6 - k
                for yy, row in enumerate(('.X.X.', 'XXXXX', '.XXX.', '..X..')):
                    for xx, ch in enumerate(row):
                        if ch == 'X': rects.append([x0 + xx * 0.45, y0 + yy * 0.45, 0.45, 0.45, '#F29AB4', 0.9 * (1 - u)])
        if self.hurt and not hide:                                                 # d10: nails, flinches, the hand, scars
            try:
                sfx = self.screen_fx; evs = sfx.ev.pet(now - sfx.t0) if sfx is not None and getattr(sfx, 'ev', None) is not None else None
                rects, ov = self.hurt.apply(rects, ov, now, evs, st.get('eye') or ZD.C['G'])
            except Exception as e:
                if str(e) != getattr(self, 'hurt_err', None): self.hurt_err = str(e); log(f'hurt: frame error: {e!r}')
        if not hide and self.react.busy(now) and not self.form_on():                 # d16: reactions on top of everything he does
            sn_ = self.ear.ear.snap if self.ear and self.ear_on else {}
            rects, ov = self.react.apply(rects, ov, now, sn_, st.get('eye') or ZD.C['G'])
        if self.hurt and not hide and not self.form_on() and hasattr(ZH, 'residue'):     # d19: СЛЕДЫ, today's dead pixels
            for i, (cx, cy) in enumerate(scar_cells(rects, ZH.residue(self.hurt.mem, now))):          # d29: on his body
                if int(now * 3 + i * 7) % 23: rects.append([cx, cy, 1, 1, '#FF2244', 0.8])
        if hasattr(self, 'morph_apply'):                                            # d31 СМЕНА: the way in / out
            try: rects, ov, hide = self.morph_apply(rects, ov, hide, now, st)
            except Exception as e:
                if str(e) != getattr(self, 'morph_err', None): self.morph_err = str(e); log(f'hurt: СМЕНА error: {e!r}')
        self.frame = (rects, ov, hide)                                             # d11: the overlay paints him in front during events
        if self.screen_fx is None: self.paint_frame(cr, rects, ov, hide)
        # bubble
        content = None
        if self.report:
            lvl, title, body, hint, _ = self.report; content = (lvl, title, body, hint)
            if self.ringing and title.startswith('ВРЕМЯ ВЫШЛО'): content = ('crit', title, body, hint)
        elif (self.hover or self.pinned) and not self.ghost_on:
            title = 'ДЕМОН · ' + ('ИГРАЕТ' if self.music.playing() else 'СИСТЕМА')
            body = '\n'.join(self.stats.lines())
            # d6: song / mode / weather / next live in the caption; `zarya-music` says why
            if self.timer:
                left = int(self.timer[0] - time.time()); body += f'\nТАЙМЕР {self.timer[2]} · {left // 60:02d}:{left % 60:02d}'
            if self.job: body += f'\nRUNNING {self.job[0][:28]} · {int(self.job[1])}s'
            content = ('info', title, body, 'PINNED · CLICK TO UNPIN' if self.pinned else 'CLICK: PIN · RIGHT: MENU' if self.hints <= 5 else '')
        rect = self.bubble(cr, *content) if content else None
        if rect is None: self.caption(cr, now)
        if rect != self.bubble_rect:
            self.bubble_rect = rect; self.reshape()

    def caption(self, cr, now):
        """d5: now playing as plain text next to ДЕМОН. Big for 3 s on a new song (even over apps), then small and dim,
        only where no window covers it. Click-through (not in the input shape). Hidden in fullscreen / games with him."""
        if not (self.music.playing() and self.caption_on() and self.cfg.get('music', '1') != '0' and not self.muted()): return
        if self.stand is not None and self.stand.phase in ('fight', 'climax'): return                    # d14: the horde walks there
        big = self.announce is not None and now - self.announce < 3.0
        if not big and self.cover_cap and self.cfg.get('caption_fold', '0') == '1': return       # d16: no fold by default
        title, artist = self.music.title(), self.music.artist()
        if self.form_on() and self.form.mimic_on(now): title = self.form.fake_title(title)             # d19: one letter wrong
        elif self.form_on():                                                                            # d11 / d19: its lyric line
            lyr = self.form.lyric((self.info or {}).get('lyrics') or [], self.music.position(), now) if hasattr(self.form, 'lyric') else None
            if hasattr(self.form, 'chorus_off') and self.form.chorus_off(now): lyr = None                # d23: it is shouting it
            title, artist = lyr or self.form.corrupt(title, now), f'НЕ ОН · {artist}'
        if not title or title == '?': return
        k = 1.0 if big else 0.0
        if self.announce is not None and 3.0 <= now - self.announce < 3.6: k = 1 - (now - self.announce - 3.0) / 0.6   # settle
        tag = ''
        if self.dancing() or self.mrule:
            w = self.cur_weather()[0]
            tag = self.mode_label(False) + (f'  {ZM.WGLYPH[w]} {ZM.WLABEL[w]}' if w and ZM else '')
        if self.form_on() and not self.form.mimic_on(now): tag = self.form.label()
        if self.ear is not None and not self.fx_enabled(): tag = 'АНИМАЦИИ ВЫКЛ'                   # d7
        elif self.talk: tag = 'РЕЧЬ'
        if self.brain and not self.form_on() and tag not in ('АНИМАЦИИ ВЫКЛ', 'РЕЧЬ'):              # d20
            bl = ZB.label_for(None, self.bctx) or ('ИЗУЧАЮ' if self.brain.learning() else '')
            if bl: tag += ('  ·  ' if tag else '') + bl
        if self.stop_fade or os.path.exists(f'{CACHE}/stop-at'): tag += '  ·  СОН'
        s = self.U / 5
        ft, fa, fg = 10 + 6 * k, 8.5 + 2.5 * k, 7.5
        col_t = (0.894, 0.878, 0.918, 0.80 + 0.2 * k); col_a = (0.788, 0.765, 0.839, 0.62 + 0.3 * k)
        col_g = (0.616, 0.482, 1.0, 0.75)
        x = self.SW + int(8 * s); y_bot = self.WH - int(6 * s)
        lines = [(f'JetBrainsMono Nerd Font Bold {ft * s:.1f}', title, col_t), (f'JetBrainsMono Nerd Font {fa * s:.1f}', artist, col_a)]
        if self.up_next and not big: lines.append((f'JetBrainsMono Nerd Font {fg * s:.1f}', f'NEXT ▸ {self.up_next[0]}', (0.43, 0.40, 0.53, 0.7)))
        if tag: lines.append((f'JetBrainsMono Nerd Font {fg * s:.1f}', tag, col_g))
        lays = []
        for font, txt, col in lines:
            if not txt: continue
            lay = PangoCairo.create_layout(cr); lay.set_font_description(Pango.FontDescription.from_string(font))
            lay.set_width(int(360 * s * Pango.SCALE)); lay.set_ellipsize(Pango.EllipsizeMode.END); lay.set_text(txt, -1)
            lays.append((lay, col))
        hsum = sum(l.get_pixel_size()[1] for l, _ in lays) + 2 * (len(lays) - 1)
        y = y_bot - hsum
        for lay, col in lays:
            cr.move_to(x, y); PangoCairo.layout_path(cr, lay)
            cr.set_source_rgba(7 / 255, 6 / 255, 13 / 255, 0.72 * col[3]); cr.set_line_width(3); cr.set_line_join(cairo.LINE_JOIN_ROUND)
            cr.stroke()                                                            # thin dark outline: readable over the Reze wall
            cr.move_to(x, y); cr.set_source_rgba(*col); PangoCairo.show_layout(cr, lay)
            y += lay.get_pixel_size()[1] + 2

    def overlay(self, cr, kind, a, U, oy, before):
        """d4/d5: extra shapes from the music modes (grid units like the sprite)."""
        ga = 1 - self.ghost
        if kind == 'spot' and before:
            cx, al, col = a; r, g, b, _ = rgb(col)
            top = -oy / U
            pat = cairo.LinearGradient(0, 0, 0, oy + (ZD.OY + 10) * U)
            pat.add_color_stop_rgba(0, r, g, b, 0); pat.add_color_stop_rgba(1, r, g, b, al * ga)
            cr.set_source(pat)
            cr.move_to((cx - 1.5) * U, top * U + oy); cr.line_to((cx + 1.5) * U, top * U + oy)
            cr.line_to((cx + 8) * U, oy + (ZD.OY + 10) * U); cr.line_to((cx - 8) * U, oy + (ZD.OY + 10) * U)
            cr.close_path(); cr.fill()
        elif kind == 'ring' and not before:
            cx, cy, rx, ry, col, al = a
            cr.save(); cr.translate(cx * U, oy + cy * U); cr.scale(max(0.1, rx * U), max(0.1, ry * U))
            cr.arc(0, 0, 1, 0, 2 * math.pi); cr.restore()
            cr.set_source_rgba(*rgb(col, al * ga)); cr.set_line_width(2); cr.stroke()
        elif kind == 'letterbox' and before:
            al = a[0] * ga; cr.set_source_rgba(7 / 255, 6 / 255, 13 / 255, al)
            cr.rectangle(0, oy + (ZD.OY - 3) * U, self.SW, 0.8 * U); cr.fill()
            cr.rectangle(0, oy + (ZD.OY + 11.2) * U, self.SW, 0.8 * U); cr.fill()
        elif kind == 'tear' and not before:
            yo, hh, col = a
            cr.set_source_rgba(*rgb(col, 0.5 * ga)); cr.rectangle(0, round(oy + (ZD.OY + 5 + yo) * U), self.SW, max(1, round(hh * 0.3 * U))); cr.fill()
        elif kind == 'under' and before:                                            # d5: rift and other shapes BEHIND him
            for x, y, ww, hh, c, al in a:
                if al * ga < 0.04: continue
                x0, y0 = round(x * U), round(oy + y * U)
                cr.set_source_rgba(*rgb(c, al * ga)); cr.rectangle(x0, y0, max(1, round((x + ww) * U) - x0), max(1, round(oy + (y + hh) * U) - y0)); cr.fill()
        elif kind == 'glyphs' and before:                                           # corrupted Cyrillic inside the rift
            for x, y, ch, al, col in a:
                lay = PangoCairo.create_layout(cr); lay.set_font_description(Pango.FontDescription.from_string(f'JetBrainsMono Nerd Font Bold {max(5, int(1.4 * U))}'))
                lay.set_text(ch, -1); cr.move_to(round(x * U), round(oy + y * U)); cr.set_source_rgba(*rgb(col, al * ga)); PangoCairo.show_layout(cr, lay)
        elif kind == 'flash' and not before:                                        # a short soft glow around him only
            col, al = a; r, g, b_, _ = rgb(col); cx, cy = self.SW / 2, oy + (ZD.OY + 5) * U
            pat = cairo.RadialGradient(cx, cy, 4, cx, cy, 13 * U)
            pat.add_color_stop_rgba(0, r, g, b_, al * ga); pat.add_color_stop_rgba(1, r, g, b_, 0)
            cr.set_source(pat); cr.arc(cx, cy, 13 * U, 0, 2 * math.pi); cr.fill()
        elif kind == 'edge' and not before:                                         # МАКС: edges of his area flash on the kick
            col, al = a; cr.set_source_rgba(*rgb(col, al * ga))
            cr.rectangle(0, oy, 2, self.SH); cr.fill(); cr.rectangle(self.SW - 2, oy, 2, self.SH); cr.fill()
            cr.rectangle(0, oy + self.SH - 2, self.SW, 2); cr.fill()
        elif kind == 'paint' and ZH and (before == (a[0] == 'sky')):                # d14: the last stand's sky, slash, tally
            ZH.paint_stand(cr, a, U, oy, self.SW, self.WH)
        elif kind == 'shout' and not before:                                        # МАКС: ТИШЕ… НЕТ. ГРОМЧЕ.
            txt, al = a[0], a[1]; sc = a[2] if len(a) > 2 else 1.0                       # d23: КРИК sizes
            lay = PangoCairo.create_layout(cr); lay.set_font_description(Pango.FontDescription.from_string(f'JetBrainsMono Nerd Font Bold {int(2.4 * U * sc)}'))
            lay.set_text(txt, -1); tw, th = lay.get_pixel_size()
            x = max(2, self.SW // 2 - tw // 2); y = oy + (ZD.OY - 4) * U - th
            fg_ = a[3] if len(a) > 3 else '#E4E0EA'; sh_ = a[4] if len(a) > 4 else '#FF5C8A'           # d25: coloured shouts
            cr.move_to(x + 2, y); cr.set_source_rgba(*rgb(sh_, 0.7 * al * ga)); PangoCairo.show_layout(cr, lay)
            cr.move_to(x, y); cr.set_source_rgba(*rgb(fg_, al * ga)); PangoCairo.show_layout(cr, lay)

    def bubble(self, cr, lvl, title, body, hint):
        LC_, BONE_, BODY_, HINT_, VOID_ = bubble_palette(self); title = skin_title(self, title)          # d29: ПОДМЕНЫШ skin
        col = LC_.get(lvl, LC_['info'])
        s = self.U / 4
        lay = PangoCairo.create_layout(cr)
        lay.set_width(int(380 * s * Pango.SCALE)); lay.set_wrap(Pango.WrapMode.WORD_CHAR)
        lay.set_spacing(int(3 * s * Pango.SCALE))
        esc = GLib.markup_escape_text
        mark = (f'<span font="JetBrainsMono Nerd Font Bold {int(9 * s)}" foreground="{col if lvl != "info" else BONE_}" letter_spacing="1200">{esc(title)}</span>\n'
                f'<span font="JetBrainsMono Nerd Font {int(9.5 * s)}" foreground="{BODY_}">{esc(body)}</span>')
        if hint: mark += f'\n<span font="JetBrainsMono Nerd Font {int(7.5 * s)}" foreground="{HINT_}">{esc(hint)}</span>'
        lay.set_markup(mark, -1)
        tw, th = lay.get_pixel_size()
        pad = int(11 * s); bw, bh = tw + 2 * pad + 3, th + 2 * pad
        x = self.SW + int(10 * s)
        eye_y = self.WH - self.SH + (ZD.OY + 4) * self.U                    # bubble bottom sits a little below the eye line
        y = max(2, min(eye_y + int(30 * s) - bh, self.WH - bh - 2))
        # link line from the pet, at eye height
        ly = max(y + 6, min(eye_y, y + bh - 6))
        cr.set_source_rgba(*rgb(col)); cr.rectangle(self.SW - int(2 * s), ly, x - self.SW + int(2 * s), 1); cr.fill()
        cr.set_source_rgba(*VOID_); cr.rectangle(x, y, bw, bh); cr.fill()
        cr.set_source_rgba(*rgb(col)); cr.set_line_width(1)
        cr.rectangle(x + 0.5, y + 0.5, bw - 1, bh - 1); cr.stroke()
        cr.rectangle(x + bw - 3, y, 3, bh); cr.fill()                       # thick right edge (Zarya HUD)
        cr.move_to(x + pad, y + pad); cr.set_source_rgba(*rgb(BONE_)); PangoCairo.show_layout(cr, lay)
        return (x, y, bw, bh)

