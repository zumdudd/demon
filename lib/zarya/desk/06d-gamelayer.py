# ДЕМОН · concept + direction: ШУМ (shum) · built with Claude (Anthropic)
# >>> d33 ИГРА on top (mint-pack v46). ШУМ 2026-11-04: in games ДЕМОН / ПОДМЕНЫШ should stay on top, just not clickable;
#     d31 kept him running but Muffin stacks a focused fullscreen window above every DOCK / keep-above window, so he was
#     drawn behind the game. Now, while a game runs, he is drawn in an override-redirect POPUP (like the screen events): the
#     window manager never restacks it, the compositor keeps it above the game, input shape empty so every click goes to
#     the game. His own window is hidden meanwhile and comes back when the game ends. Raised again every second in case
#     the game restacks itself. game_layer=0 in daemon.conf = d31 behaviour (stays in his own window).
class GameLayer(Gtk.Window):
    def __init__(self, d):
        super().__init__(type=Gtk.WindowType.POPUP)
        self.d = d
        vis = self.get_screen().get_rgba_visual()
        if vis: self.set_visual(vis)
        self.set_app_paintable(True); self.set_accept_focus(False)
        x, y = d.get_position(); self.move(x, y); self.set_default_size(d.WW, d.WH); self.resize(d.WW, d.WH)
        self.connect('draw', lambda w, cr: d.draw(w, cr))
        self.connect('realize', lambda *_: self.input_shape_combine_region(cairo.Region()))
        self.show_all(); self.input_shape_combine_region(cairo.Region())
        self.raise_id = GLib.timeout_add(1000, self._raise)

    def _raise(self):
        try:
            gw = self.get_window()
            if gw is not None: gw.raise_()
        except Exception: pass
        return True

    def close(self):
        if self.raise_id: GLib.source_remove(self.raise_id); self.raise_id = None
        self.destroy()


def _game_layer(self, on):
    """d33: his frame moves to / from the on-top layer when a game starts / ends."""
    L = getattr(self, 'glayer', None)
    if on and L is None and self.cfg.get('game_layer', '1') != '0':
        try:
            self.glayer = GameLayer(self); Gtk.Widget.hide(self); log('game: he is drawn on top of it (layer)')
        except Exception as e:
            self.glayer = None; log(f'game: layer error: {e!r}')
    elif not on and L is not None:
        self.glayer = None
        try: L.close()
        except Exception: pass
        self.show_all(); self.place(); log('game: layer off, back in his window')


def _queue_draw(self):
    L = getattr(self, 'glayer', None)
    if L is not None: L.queue_draw()
    else: Gtk.Widget.queue_draw(self)


Demon.game_layer = _game_layer
Demon.queue_draw = _queue_draw
# <<< d33
