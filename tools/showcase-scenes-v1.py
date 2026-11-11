# ДЕМОН · concept + direction: ШУМ (shum) · built with Claude (Anthropic)
"""showcase scenes v1 (loaded by showcase-render-v1.py, which passes itself in as R).
Each scene starts the way the right-click menu or a real song starts it, then keeps a window of the frames."""
Song, run, clip, set_song, form_in, d, F, CLOCK, scene, FPS = R.Song, R.run, R.clip, R.set_song, R.form_in, R.d, R.F, R.CLOCK, R.scene, R.FPS

LOUD = lambda bpm=120, lv=0.8, **k: Song(bpm, [(0, 'loud', lv)], 'showcase', 'ШУМ', **k)


# ---------------------------------------------------------------- the two of them
@scene('hero-demon', 'ДЕМОН dancing, the one who listens (4 s loop)')
def _():
    set_song(LOUD(120, 0.65), at=40)
    run(1.0); return run(4.0)


@scene('hero-podmenysh', 'ПОДМЕНЫШ in him, snapping on the beat (4 s loop)')
def _():
    set_song(LOUD(120, 0.72), at=40); form_in(hard=False); F.said = CLOCK.t + 1e6; F.live_cd = CLOCK.t + 1e6; F.smelled = True   # hero loop: no lines, no arc
    run(1.0); return run(4.0)


# ---------------------------------------------------------------- the change
@scene('zarazhenie', 'ЗАРАЖЕНИЕ: the way in. Infection, rupture on a kick, hang, reassembly')
def _():
    set_song(LOUD(120, 0.75), at=40); run(0.8)
    form_in(); F.line = None
    d.morph_preview('in')
    return clip(3.6, 0, 3.6)


@scene('smena', 'СМЕНА: a way out, КУЛЬТ (Death Grips / industrial)')
def _():
    set_song(LOUD(120, 0.8), at=40); form_in(); run(0.6)
    d.morph_preview('out', 'cult')
    return clip(5.0, 0, 5.0)


@scene('gnil', 'ГНИЛЬ: the way out on calm songs, it rots off him')
def _():
    form_in(hard=False); run(0.8)                                   # no song: the way out is ГНИЛЬ
    F.end(CLOCK.t, 'showcase'); d._exit_why = ''                    # it really leaves; the draw plays the way out
    return clip(4.2, 0, 4.2)


# ---------------------------------------------------------------- the hype arc
@scene('chuet', 'ЧУЕТ: it smells the hard song coming')
def _():
    form_in(); set_song(LOUD(140, 0.82), at=2.6)
    return clip(2.6, 0, 2.6)


@scene('detonatsiya', 'ДЕТОНАЦИЯ: wind-up, the soul leaves, it blows up, СБОРКА')
def _():
    set_song(LOUD(140, 0.85), at=40); form_in(); run(0.4)
    F.preview(CLOCK.t)
    return clip(8.6, 1.2, 8.6)


@scene('delikates', 'ДЕЛИКАТЕС: build, gap, slam. It explodes on the first kick of the drop')
def _():
    song = Song(150, [(0, 'loud', 0.78), (20, 'build', 0.7), (24, 'gap', 0.08), (24.6, 'slam', 1.0), (40, 'loud', 0.8)],
                'showcase', 'ШУМ', chorus=((8, 20),), vocal=((8, 20),))
    form_in(dg=True); set_song(song, at=17.5, brain=True)
    return clip(9.5, 1.5, 9.5)


@scene('krik', 'КРИК: the red line, one word per vocal hit in the chorus')
def _():
    song = Song(150, [(0, 'loud', 0.8)], 'showcase', 'ШУМ', chorus=((0, 300),), vocal=((0, 300),))
    form_in(dg=True); F.det_max = 0; set_song(song, at=60, brain=True)
    run(0.6); return run(4.0)


# ---------------------------------------------------------------- ПРИМАНКА
@scene('primanka', 'ПРИМАНКА: the cute mask, flickering to the slit on hard hits')
def _():
    set_song(LOUD(128, 0.6), at=40); form_in(); F.lure_preview(CLOCK.t)
    # the preview is cute on even 3 s blocks of the clock: start on one
    while int(CLOCK.t / 3) % 2 != 0: run(1 / FPS)
    return clip(4.4, 0.2, 4.4)


@scene('kukla', 'КУКЛА: dense hits pull pink puppet strings')
def _():
    set_song(Song(170, [(0, 'dense', 0.62)], 'showcase', 'ШУМ'), at=40); form_in(); F.lure_preview(CLOCK.t)
    while int(CLOCK.t / 3) % 2 != 0: run(1 / FPS)
    return clip(4.0, 0.4, 4.0)


@scene('dva-litsa', 'ДВА ЛИЦА: the hard switch, half cute, half dark')
def _():
    set_song(LOUD(128, 0.7), at=40); form_in(); F.lure_preview(CLOCK.t)
    while not (int(CLOCK.t / 3) % 2 == 0 and (CLOCK.t % 3) > 1.6): run(1 / FPS)     # 1.4 s before the switch to dark
    return clip(3.0, 0, 3.0)


# ---------------------------------------------------------------- ПОДДЕЛКА (nightcore)
def forgery(a, b):
    set_song(LOUD(143, 0.8), at=40); form_in(); F.forgery_preview(CLOCK.t)
    return clip(b, a, b)

@scene('poddelka', 'ПОДДЕЛКА: РАЗГОН, the cut, ОРИГИНАЛ (his ghost), УШКИ')
def _(): return forgery(2.2, 7.0)

@scene('peremotka', 'ПЕРЕМОТКА: the blast plays back reversed')
def _(): return forgery(8.4, 12.2)

@scene('konfetti', 'КОНФЕТТИ: hearts and stars that crack and rot')
def _(): return forgery(12.4, 16.2)

@scene('pitch', 'ПИТЧ: rows fly apart to alternating sides')
def _(): return forgery(15.9, 19.4)


# ---------------------------------------------------------------- the maw
@scene('past', 'ПАСТЬ · ОХОТА: it eats the fake ДЕМОН, four bites on the kicks')
def _():
    set_song(LOUD(120, 0.75), at=40); form_in()
    F.jaw_preview(CLOCK.t, True, 'hunt')
    return clip(7.0, 0, 7.0)


@scene('proval', 'ПРОВАЛ: a calm dance on a hard song, the disguise breaks')
def _():
    set_song(LOUD(120, 0.8), at=40); form_in(); F.fail_preview(CLOCK.t, True)
    return clip(4.2, 0, 4.2)


# ---------------------------------------------------------------- ДЕМОН, the witness
@scene('kadr', 'КАДР: epic peak, the frame freezes. «ВОТ ОНО.»')
def _():
    set_song(LOUD(110, 0.95), at=100); run(0.6)
    d.react.start('frame', CLOCK.t, 'showcase')
    return clip(3.2, 0, 3.2)


@scene('ogon', 'ОГОНЬ: an epic song at full excitement, flames climb him')
def _():
    set_song(LOUD(110, 0.95), at=100); run(0.4)
    d.react.start('fire', CLOCK.t, 'showcase')
    return clip(8.6, 0.4, 8.6)
