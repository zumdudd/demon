

# ======================= CLI =======================
def _state():
    try: return json.load(open(STATE))
    except (OSError, ValueError): return None


def cli():
    a = sys.argv[1:]
    cmd = a[0] if a else 'status'
    if cmd in ('-h', '--help', 'help'):
        print(open(__file__).read().split('\nimport ', 1)[0].replace('# ', '')); return
    if cmd == 'ctl': sys.exit(ctl(a[1:]))
    if cmd == 'possess':                                                  # m5: preview ОДЕРЖИМОСТЬ now
        r = a[1] if len(a) > 1 else 'summon'
        if r not in RITUALS: print('rituals: ' + ' '.join(RITUALS)); sys.exit(1)
        os.makedirs(os.path.dirname(POSSESS_FILE), exist_ok=True)
        with open(POSSESS_FILE, 'w') as f: f.write(f'{r} {time.time() + 4:.0f}')
        print(f'ОДЕРЖИМОСТЬ · {RLABEL[r]}: starts within 2 s while a song plays and he dances (about 12 s)'); return
    if cmd == 'hell': print('ПРЕИСПОДНЯЯ was removed in v18. Try: zarya-music show descend  (the hand takes him under)'); return
    if cmd == 'show':                                                     # m4: preview a whole-screen event
        ev = a[1] if len(a) > 1 else ''
        if ev not in SCREEN_EVENTS:                                                   # m11: what each one is
            for k, v in SHOW_LIST: print(f'  zarya-music show {k:8s} {v}')
            print('  zarya-music possess [summon|cult|pagan|none]   ОДЕРЖИМОСТЬ (while a song plays)'); sys.exit(0 if not ev else 1)
        os.makedirs(os.path.dirname(SCREEN_FILE), exist_ok=True)
        with open(SCREEN_FILE, 'w') as f: f.write(f'{ev} {time.time():.0f}')
        print(f'{ev}: the desktop ДЕМОН shows it within 2 s (not while a fullscreen app or game is up)'
              + ('  · the hand: click him 6× fast to free him' if ev == 'hand' else '  · click a stuck nail to pull it out' if ev == 'nails' else
                 '  · the lightning rewrites him into ПОДМЕНЫШ (right-click > Изгнать)' if ev == 'descend' else
                 '  · archived in v19, preview only' if ev in ('nails', 'hand', 'shadow') else
                 '  · ПОСЛЕДНИЙ РУБЕЖ in his corner (~20 s); with an epic song playing he fights on its hits' if ev == 'stand' else '')); return
    if cmd == 'peak':                                                     # m11
        v = a[1] if len(a) > 1 else ''
        if v not in PEAKS + ('auto',): print('usage: zarya-music peak possess|stand|rift|auto [--artist]'); sys.exit(1)
        if not alive_now() : print('nothing playing that I can name.'); sys.exit(1)
        st = _state(); every = '--artist' in a
        teach_song(dict(artists=st['artists'], title=ARTIST_ALL if every else st['title']), peak='' if v == 'auto' else v)
        print(f"{(st['artists'][0] + ' (every song)') if every else st['title']} → peak {v}  (saved in {SONGS})"); return
    if cmd == 'rules':
        for p in (RULES, SONGS):
            print(f'{p}\n'); print(open(p).read() if os.path.exists(p) else '(no file yet)\n')
        return
    if cmd == 'listen':
        secs = float(a[1]) if len(a) > 1 else 30
        L = Listener(); L.start(); L.start_ear(); t_end = time.time() + secs
        print('listening (Ctrl+C to stop)…')
        try:
            while time.time() < t_end:
                time.sleep(1); s = L.ear.snap
                if L.err: print(L.err); break
                if not s.get('t'): continue
                g = L.ear.guess(s) if 'kps' in s else ('?', '')
                print(f"{s.get('bpm', 0):5.0f} BPM  level {s.get('level', 0):.2f}  808 {s.get('subr', 0):.2f}  wall {s.get('wall', 0):.2f}"
                      f"  k/s {s.get('kps', 0):.1f}  s/s {s.get('sps', 0):.1f}  h/s {s.get('hps', 0):.1f}  sec {s.get('section', 0)}"
                      f"  build {s.get('build', 0):.2f}  chaos {s.get('chaos', 0):.2f}  max {s.get('max_hold', 0):.1f}"
                      f"  →  {g[0]}{':' + g[1] if g[1] else ''}  (settled: {s.get('auto') and s['auto'][0]})", flush=True)
        except KeyboardInterrupt: pass
        L.stop_ear(); return
    st = _state()
    alive = st and time.time() - st.get('ts', 0) <= 10
    if cmd == 'status':
        if not alive: print('ДЕМОН is not running, or nothing has played yet.'); return
        if not st.get('playing'): print('nothing playing.'); return
        m = st.get('mode') or '?'
        print(f"♪ {st.get('title')} · {', '.join(st.get('artists') or [])}" + (f"  [{st.get('album')}]" if st.get('album') else ''))
        print(f"  player {st.get('player')} · body {LABEL.get(st.get('label'), m)} ({m}{':' + st['variant'] if st.get('variant') else ''}) · because {st.get('reason')}")
        print(f"  weather {WLABEL.get(st.get('weather'), 'none')} · because {st.get('wreason') or '-'}")
        if st.get('bpm'): print(f"  ear: {st['bpm']:.0f} BPM · level {st.get('level', 0):.2f} · 808 {st.get('subr', 0):.2f} · wall {st.get('wall', 0):.2f} · section {st.get('section', 0)}")
        if st.get('ear_err'): print(f"  ear: {st['ear_err']}")
        print('  teach: right-click ДЕМОН > This song… / Mode for <artist>   ·   zarya-music tags   for the lookups'); return
    if cmd == 'tags':
        if not alive or not st.get('title'): print('nothing playing.'); return
        info = st.get('info') or {}
        print(f"♪ {st.get('title')} · {', '.join(st.get('artists') or [])}")
        print(f"  Last.fm tags: {', '.join(f'{t} {c}' for t, c in (info.get('tags') or [])[:10]) or '(none)'}")
        print(f"  credits: {', '.join(info.get('credits') or []) or '(none found)'}")
        print(f"  lyrics: {info.get('lyrics_n', 0)} timed lines" + (f" · lyrics mood {info.get('lyric_weather')}" if info.get('lyric_weather') else ''))
        print(f"  from tags: weather {info.get('tag_weather') or '-'}, body hint {info.get('tag_mode') or '-'}")
        for n in info.get('notes') or []: print(f'  · {n}')
        if not lastfm_key(): print('  · no Last.fm key: put it in ~/.config/zarya/lastfm.key (0600)')
        return
    if cmd in ('teach', 'song'):
        if len(a) < 2: print(f'usage: zarya-music {cmd} MODE[:variant]   modes: ' + ' '.join(MODES)); return
        mode, _, var = a[1].partition(':')
        if mode not in MODES and not (cmd == 'song' and mode == 'auto'): print('unknown mode. modes: ' + ' '.join(MODES)); sys.exit(1)
        if not alive or not st.get('artists'): print('nothing playing that I can name.'); sys.exit(1)
        if cmd == 'teach': teach(st['artists'][0], mode, var); print(f"{st['artists'][0]} → {mode}{':' + var if var else ''}  (saved in {RULES})")
        else:
            teach_song(dict(artists=st['artists'], title=st['title']), mode='' if mode == 'auto' else a[1])
            print(f"{st['title']} → {a[1]}  (saved in {SONGS})")
        return
    if cmd == 'feel':
        w = a[1] if len(a) > 1 else ''
        if w not in WEATHERS + ('auto',): print('usage: zarya-music feel rain|clear|storm|dawn|auto'); sys.exit(1)
        if not alive or not st.get('artists'): print('nothing playing.'); sys.exit(1)
        teach_song(dict(artists=st['artists'], title=st['title']), feel='' if w == 'auto' else w); print(f"{st['title']} feels {w}  (saved in {SONGS})"); return
    if cmd == 'forget':
        if not alive or not st.get('artists'): print('nothing playing.'); sys.exit(1)
        print('forgotten.' if forget(st['artists'][0]) else 'no taught rule for this artist.'); return
    if cmd == 'try':
        if len(a) < 2 or a[1].split(':')[0] not in MODES: print('usage: zarya-music try MODE[:variant] [seconds]'); sys.exit(1)
        secs = float(a[2]) if len(a) > 2 else 30
        os.makedirs(CACHE, exist_ok=True); open(FORCE, 'w').write(f'{a[1]} {time.time() + secs}')
        print(f'{a[1]} for {secs:.0f} s (needs music playing)'); return
    print('commands: status · tags · teach MODE · song MODE · feel WEATHER · peak PEAK [--artist] · forget · try MODE [S] · listen [S] · rules · show [EVENT] · possess [RITUAL] · ctl …'); sys.exit(1)


PEAKS = ('possess', 'stand', 'rift', 'nails')                                         # m11
SHOW_LIST = [('stand', 'ПОСЛЕДНИЙ РУБЕЖ · last stand in his corner (epic songs)'),
             ('descend', 'ПОДМЕНЫШ · the lightning rewrites him (hard songs; right-click > Изгнать to end it)'),
             ('form', 'ПОДМЕНЫШ now, without the lightning'), ('unform', 'drive ПОДМЕНЫШ out'),
             ('ascend', 'ВОЗНЕСЕНИЕ · whole-screen rise'),
             ('nails', 'ТРИ ГВОЗДЯ (archived)'), ('hand', 'THE HAND (archived)'), ('shadow', 'ТЕНЬ (archived)')]


def alive_now():
    st = _state()
    return bool(st and time.time() - st.get('ts', 0) <= 10 and st.get('artists'))


if __name__ == '__main__':
    cli()
