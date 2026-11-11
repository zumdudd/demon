# ДЕМОН · concept + direction: ШУМ (shum) · built with Claude (Anthropic)
# >>> d39 ПОДДЕЛКА's pieces on other songs (mint-pack v56; zarya-hurt h22 draws them). ШУМ 2026-11-07 22:52.
#   The switch: right-click > ▶ Animations > On their own > «ПОДДЕЛКА · its pieces on other songs» (`nc_spread`, default 1):
#   blast styles on hard songs, ears / sparkles / heart on ПРИМАНКА songs, light dust + rain on loud parts.
_sp_event_tick0 = Demon.event_tick
def _sp_event_tick(self, now):
    _sp_event_tick0(self, now)
    if self.form is not None: self.form.spread = self.cfg.get('nc_spread', '1') != '0'


_sp_anim0 = Demon.anim_menu
def _sp_anim_menu(self, m):
    _sp_anim0(self, m)
    on = self.cfg.get('nc_spread', '1') != '0'
    t = Gtk.MenuItem(label=f'   ПОДДЕЛКА · its pieces on other songs  {"✓" if on else "✗  (off)"}')
    t.connect('activate', lambda *_: self.set_opt('nc_spread', '0' if on else '1')); m.append(t)


Demon.event_tick = _sp_event_tick
Demon.anim_menu = _sp_anim_menu
# <<< d39
