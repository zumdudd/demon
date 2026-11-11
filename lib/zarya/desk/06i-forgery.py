# ДЕМОН · concept + direction: ШУМ (shum) · built with Claude (Anthropic)
# >>> d38 ПОДДЕЛКА: finds nightcore / sped-up edits for ПОДМЕНЫШ (mint-pack v54; zarya-hurt h20 draws it).
#   ШУМ 2026-11-07: nightcore animations, "it goes faster ... as the songs say its speed up", all 6 ideas; rulings by Claude,
#   standing unless ШУМ says otherwise: a layer (ПРИМАНКА can still wear its mask on top), never summons, nightstep = ДЕЛИКАТЕС
#   on the drop + the speed layer around it.
#   Who: "nightcore", "nightstep", "sped up" / "speed up" in the title, an artist or the album (a channel artist like
#   "NightcoreReality" counts); not "slowed", "reverb", "daycore". The original artist / title come out of the title
#   ("Nightcore - Artist - Song (Sped Up)" → Artist, Song).
#   The ratio: MusicBrainz recording length (score ≥ 85, same base title, not itself an edit, 1.04-1.7 × the edit), then
#   Last.fm track.getInfo; r = original / edit. Not found = ×1.25. One lookup per song, cached 30 days (misses 7) in
#   ~/.local/share/zarya/forgery.json. Checked every second against the song ПОДМЕНЫШ knows (Form.song_key).
#   Shouts carry a 6th value (ТОН: cells up), drawn here capped at the window top.
#   Menu: ▶ Animations > ▶ ПОДДЕЛКА · the forgery (16 s preview) · On their own > «ПОДДЕЛКА · nightcore speeds it up» (`forgery`).
import json
NC_CACHE = f'{HOME}/.local/share/zarya/forgery.json'
NC_RX = re.compile(r'night\s*core|night\s*step|sped[\s_-]*up|speed[\s_-]*up', re.I)
NC_NOT = re.compile(r'slowed|reverb|day\s*core|anti[\s-]*nightcore', re.I)
NC_HIT_DAYS, NC_MISS_DAYS = 30, 7


def nc_detect(artists, title, album=''):
    """None, or dict(oartist, otitle, why, nightstep) for a nightcore / sped-up edit."""
    artists = [a for a in (artists or []) if a]
    hay = ' | '.join(artists + [title or '', album or ''])
    m = NC_RX.search(hay)
    if not m or NC_NOT.search(title or '') or NC_NOT.search(album or ''): return None
    t = title or ''
    t = re.sub(r'\s*[\(\[\{][^\)\]\}]*(?:night\s*core|night\s*step|sped|speed)[^\)\]\}]*[\)\]\}]', '', t, flags=re.I)
    t = re.sub(r'^\s*(?:night\s*core|night\s*step)\s*(?:[-–—:|]\s*)?', '', t, flags=re.I)
    t = re.sub(r'\s*[-–—|:]\s*(?:night\s*core|night\s*step|sped[\s-]*up|speed[\s-]*up)(?:\s*(?:version|ver\.?|remix|edit|mix))?\s*$', '', t, flags=re.I)
    t = re.sub(r'\s+(?:sped[\s-]*up|speed[\s-]*up)(?:\s*(?:version|ver\.?|edit))?\s*$', '', t, flags=re.I).strip(' -–—|:')
    real = [a for a in artists if not NC_RX.search(a)]
    oa = real[0] if real else ''
    parts = re.split(r'\s[-–—]\s', t, maxsplit=1)
    if len(parts) == 2 and (not oa or ZM.norm(parts[0]) == ZM.norm(oa)): oa, t = parts[0].strip(), parts[1].strip()
    return dict(oartist=oa, otitle=t.strip(), why=m.group(0).lower(), nightstep=bool(re.search(r'night\s*step', hay, re.I)))


def nc_lookup(oa, ot, edit_len):
    """(original length in s or None, source / why)."""
    if not ot: return None, 'no title'
    lo, hi = (edit_len * 1.04, edit_len * 1.7) if edit_len else (0, 1e9)
    why = []
    try:
        q = f'recording:"{ZM.base_title(ot)}"' + (f' AND artist:"{oa}"' if oa else '')
        j = ZM._get(ZM.MB_API + '/ws/2/recording', dict(query=q, fmt='json', limit=15))
        bt = ZM.norm(ZM.base_title(ot)); ls = []
        for rec in j.get('recordings') or []:
            if int(rec.get('score') or 0) < 85 or not rec.get('length'): continue
            if ZM.norm(ZM.base_title(rec.get('title') or '')) != bt: continue
            if NC_RX.search((rec.get('title') or '') + ' ' + (rec.get('disambiguation') or '')): continue
            s = rec['length'] / 1000
            if lo <= s <= hi: ls.append(s)
        if ls:
            ls.sort(); n = len(ls); med = ls[n // 2] if n % 2 else (ls[n // 2 - 1] + ls[n // 2]) / 2
            return med, f'MusicBrainz ({n} recordings)'
        why.append('MusicBrainz: no match')
    except Exception as e: why.append(f'MusicBrainz failed: {e}')
    key = ZM.lastfm_key()
    if key and oa:
        try:
            j = ZM._get(ZM.LASTFM_API + '/2.0/', dict(method='track.getInfo', artist=oa, track=ot, autocorrect=1, api_key=key, format='json'))
            s = int((j.get('track') or {}).get('duration') or 0) / 1000
            if s and lo <= s <= hi: return s, 'Last.fm'
            why.append('Last.fm: no length' if not s else f'Last.fm: {s:.0f} s out of range')
        except Exception as e: why.append(f'Last.fm failed: {e}')
    return None, '; '.join(why)


def _nc_cache():
    try: return json.load(open(NC_CACHE, encoding='utf-8'))
    except (OSError, ValueError): return {}


def _nc_cache_put(key, orig, src):
    c = _nc_cache(); now = time.time()
    c = {k: v for k, v in c.items() if now - v.get('t', 0) < 86400 * (NC_HIT_DAYS if v.get('orig') else NC_MISS_DAYS)}
    c[key] = dict(orig=orig, src=src, t=now)
    try:
        os.makedirs(os.path.dirname(NC_CACHE), exist_ok=True); tmp = NC_CACHE + '.tmp'
        json.dump(c, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); os.replace(tmp, NC_CACHE)
    except OSError as e: log(f'hurt: ПОДДЕЛКА cache: {e.strerror}')


def _nc_apply(self, key, orig, src):
    f = self.form
    if f is None or getattr(f, 'song_key', None) != key or getattr(f, 'nc', None) is None: return False
    edit = self.music.trackinfo()[2] or f.nc.get('edit_len') or 0
    if orig and edit: f.forgery_r(orig / edit, src, orig, edit)
    else: log(f'hurt: ПОДДЕЛКА: original not found ({src}), stays ×{f.nc["r"]:.2f}')
    return False


def _nc_tick(self, now):
    if now - getattr(self, '_nc_t', 0) < 1.0: return
    self._nc_t = now
    f = self.form
    if f is None or not hasattr(f, 'forgery'): return
    if self.cfg.get('forgery', '1') == '0':
        if getattr(f, 'nc', None) is not None and not f.nc.get('pv_end'): f.nc = None; log('hurt: ПОДДЕЛКА off (menu)')
        self._nc_key = None; return
    key = getattr(f, 'song_key', None)
    if key == getattr(self, '_nc_key', None): return
    self._nc_key = key
    if not key or not self.music.active(): return
    d = nc_detect(self.music.artists() or [self.music.artist() or ''], self.music.title(), self.music.album())
    if not d: return
    edit = self.music.trackinfo()[2] or 0
    hit = _nc_cache().get(key)
    f.forgery(now, dict(d, r=(hit['orig'] / edit) if hit and hit.get('orig') and edit else ZH.NC_GUESS,
                        src=hit['src'] if hit and hit.get('orig') else 'guess', edit_len=edit or None,
                        orig_len=hit.get('orig') if hit else None))
    log(f'hurt: ПОДДЕЛКА found ("{d["why"]}" in {self.music.artist()} — {self.music.title()})')
    if hit: return
    def go(oa=d['oartist'], ot=d['otitle'], edit=edit, key=key):
        try: orig, src = nc_lookup(oa, ot, edit)
        except Exception as e: orig, src = None, f'lookup failed: {e!r}'
        _nc_cache_put(key, orig, src)
        GLib.idle_add(self.nc_apply, key, orig, src)
    threading.Thread(target=go, daemon=True).start()


_nc_event_tick0 = Demon.event_tick
def _nc_event_tick(self, now):
    _nc_event_tick0(self, now)
    try: self.nc_tick(now)
    except Exception as e:
        if str(e) != getattr(self, '_nc_err', None): self._nc_err = str(e); log(f'hurt: ПОДДЕЛКА tick error: {e!r}')


_nc_overlay0 = Demon.overlay
def _nc_overlay(self, cr, kind, a, U, oy, before):
    """ТОН: a shout with a 6th value sits that many cells higher, never above the window top."""
    if kind == 'shout' and not before and len(a) > 5 and a[5]:
        sc = a[2] if len(a) > 2 else 1.0
        room = max(0.0, oy + (ZD.OY - 4) * U - 4.0 * U * sc - 2)
        lift = min(a[5] * U, room)
        cr.save(); cr.translate(0, -lift)
        try: _nc_overlay0(self, cr, kind, a[:5], U, oy, before)
        finally: cr.restore()
        return
    return _nc_overlay0(self, cr, kind, a, U, oy, before)


_nc_anim0 = Demon.anim_menu
def _nc_anim_menu(self, m):
    _nc_anim0(self, m)
    hurt = bool(ZH and self.hurt)
    i = Gtk.MenuItem(label='   ▶ ПОДДЕЛКА · the forgery (nightcore, ×1.30)')
    i.set_sensitive(hurt and self.form_on() and hasattr(self.form, 'forgery_preview'))
    i.connect('activate', lambda *_: self.form.forgery_preview(time.time(), self.music.artist() if self.music.active() else ''))
    kids = m.get_children(); at = next((n + 1 for n, k in enumerate(kids) if (k.get_label() or '').startswith('   ▶ ПРИМАНКА')), None)
    if at is None: m.append(i)
    else: m.insert(i, at)
    on = self.cfg.get('forgery', '1') != '0'
    t = Gtk.MenuItem(label=f'   ПОДДЕЛКА · nightcore / sped up speeds it up  {"✓" if on else "✗  (off)"}')
    t.connect('activate', lambda *_: self.set_opt('forgery', '0' if on else '1')); m.append(t)


Demon.nc_tick = _nc_tick
Demon.nc_apply = _nc_apply
Demon.event_tick = _nc_event_tick
Demon.overlay = _nc_overlay
Demon.anim_menu = _nc_anim_menu
# <<< d38
