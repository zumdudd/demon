# ДЕМОН · concept + direction: ШУМ (shum) · built with Claude (Anthropic)
# >>> d29 ПОДМЕНЫШ skin + СЛЕДЫ on his body (mint-pack v39)
# While ПОДМЕНЫШ is in him, his messages (♥, ГОТОВО, ПЕРЕРЫВ…) and the right-click menu wear its palette: dark flesh,
# a #FF2244 frame, blood-tinted text, and one glitched letter in each title (stable per title, like the dock's «НЕ ОН»).
# The text stays readable. form_skin=0 in daemon.conf turns it off.
CH_LEVEL = dict(info='#FF2244', ok='#E09AA8', warn='#FF7A3D', crit='#FF2244', music='#FF5C8A')
CH_BONE, CH_BODY, CH_HINT, CH_VOID = '#F2DCE0', '#D9B3BA', '#8A4A58', (14 / 255, 4 / 255, 8 / 255, 0.95)
CH_GREY = '#8A5A66'
GLITCH = dict(А='Д', Е='Є', О='Ѳ', И='Ѝ', Н='Ң', Т='Ҭ', Р='Ҏ', К='Ҝ', С='Ҫ', Л='Ӆ', М='Ӎ', Г='Ґ', Ж='Җ', Х='Ҳ', Ч='Ҷ',
              Ш='Щ', В='Ɓ', У='Ў', Я='Ԓ', Ь='Ѣ', Ы='Ѣ', Д='Ԁ', П='Ԥ', З='Ҙ', Б='Ƃ', A='Λ', E='Ǝ', O='Ø', N='Ͷ', R='Я', S='Ƨ',
              T='Ŧ', I='Ɨ', L='Ⅼ', D='Ð', U='Ʉ', M='Ӎ', K='Ҝ', C='Ͼ', G='Ǥ', H='Ң', P='Ҏ', Y='Ұ', W='Ш', V='Ѵ', B='ß')
_CH_CSS = None


def skin_on(d):
    try: return d.cfg.get('form_skin', '1') != '0' and (d.form_on() or d.cfg.get('resident', '1') != '0')   # d34: always while it lives here
    except Exception: return False


def skin_title(d, title):
    """one letter of the title swapped for a look-alike glyph; the same letter every time for the same title."""
    if not title or not skin_on(d): return title
    spots = [i for i, ch in enumerate(title) if ch.upper() in GLITCH]
    if not spots: return title
    i = spots[sum(ord(c) for c in title) % len(spots)]
    g = GLITCH[title[i].upper()]
    return title[:i] + (g if title[i].isupper() else g.lower()) + title[i + 1:]


def bubble_palette(d):
    if skin_on(d): return CH_LEVEL, CH_BONE, CH_BODY, CH_HINT, CH_VOID
    return LEVEL_COL, BONE, BODY, HINT, VOIDBG


def menu_skin(d):
    """the menu stylesheet on top of the normal one while ПОДМЕНЫШ is here; the grey English turns blood-grey."""
    global _CH_CSS, GREY
    scr = Gdk.Screen.get_default()
    if _CH_CSS is None:
        _CH_CSS = Gtk.CssProvider()
        _CH_CSS.load_from_data(b'''menu, .menu { background-color: rgba(14,4,8,0.97); border: 1px solid #FF2244; border-radius: 0; }
            menuitem { color: #D9B3BA; }
            menuitem:hover { background-color: rgba(255,34,68,0.26); color: #F2DCE0; }
            menuitem:disabled, menuitem:disabled label { color: #6E3A46; }
            menu separator { background-color: #4A1420; }''')
    try: Gtk.StyleContext.remove_provider_for_screen(scr, _CH_CSS)
    except Exception: pass
    if skin_on(d):
        Gtk.StyleContext.add_provider_for_screen(scr, _CH_CSS, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1); GREY = CH_GREY
    else: GREY = '#8A8499'


def scar_cells(rects, res):
    """СЛЕДЫ on his body: each saved scar sits where it was saved relative to him (moved with him when he hops / leans) and
    snaps to the nearest solid body cell, so the dots ride on him instead of floating in the empty corners of his box."""
    body = [(x, y) for x, y, w, h, c, a in rects
            if a >= 0.95 and w >= 0.99 and h >= 0.99 and c not in ('#07060D', '#0C0A14', '#8FD9A8')]
    if not body: return []
    sx = min(x for x, y in body) - ZD.OX; sy = min(y for x, y in body) - ZD.OY
    out = []
    for dx, dy in res:
        tx, ty = ZD.OX + dx + sx, ZD.OY + dy + sy
        out.append(min(body, key=lambda p: (p[0] - tx) ** 2 + (p[1] - ty) ** 2))
    return out
# <<< d29
