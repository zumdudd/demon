# ДЕМОН change log

Concept + direction: ШУМ (shum) · built with Claude (Anthropic). Moved here from the code headers (copied in mint-pack v34; removed from the code in v35).

## zarya-brain

**b6 (mint-pack v52, 2026-11-05):** ears for zarya-mind: with `ears=1` (mind.conf, default) each song plays through once more for its clips (songs studied before too; new songs get them from the study recording): up to 8 × 10 s, one per map section (spread evenly without a map), joined as a 22 kHz mono 16-bit WAV in `~/.cache/zarya-brain/ears/` with their song times; ≤ 20 waiting, 3 days max. Never in games (no capture there). `zarya-brain ears RAW META` cuts them (stdlib only).

```
ZARYA ⇢ SLMAEVE :: ДЕМОН's song brain (b5, mint-pack v33: lure() = cute + dark by sound; b4, mint-pack v32: drops vs the gap, onset-timed; b3, mint-pack v31: dynamics, drop power + hits, ДЕЛИКАТЕС score; b2, mint-pack v29: voice + aggression per section, style → dance mode; b1 mint-pack v28). Module for zarya-daemon-desk + a CLI.
The first time a song plays all the way through, ДЕМОН records what he hears (the speakers' monitor, mono 22 kHz, a temp file
that is deleted after) and studies it in the background: where each section starts and which ones repeat (verse / chorus),
the chorus, where the drops land and the builds before them, the energy curve, the key (major / minor), and, with the
Essentia models installed, mood (happy / sad / aggressive / relaxed / party), danceability, singing vs instrumental and the
style (400 Discogs styles). The result is a small map per song; from the second play on he knows what is coming.
Your Spotify history adds weight: favourites (100+ plays) get his reactions twice as often, songs you always skip half.
  zarya-brain now              the map of the song playing now (and where you are in it)
  zarya-brain list             songs he has studied
  zarya-brain show TEXT        the map of a studied song (title or artist words)
  zarya-brain study FILE       study an audio file (wav / mp3 / flac…) and print the map (needs the models env)
  zarya-brain forget TEXT      drop a map (he studies the song again next time)
  zarya-brain grit             b3: how close each studied song is to Death Grips (ДЕЛИКАТЕС score, logged only in v31)
  zarya-brain weights          rebuild song weights from the imported Spotify history (zarya-journal import)
  zarya-brain setup            create the analysis env (~700 MB: numpy + essentia-tensorflow) and download the models
  zarya-brain doctor
Files: ~/.local/share/zarya/brain/{maps/*.json, env/, models/, weights.json}, temp captures in ~/.cache/zarya-brain/,
       log ~/.cache/zarya-brain.log
```

## zarya-daemon

```
ZARYA v29.2 :: ДЕМОН in the terminal. Same frame engine as the desktop pet (sprite.js port).
MINT adapter m1 (crossover guest ЗАРЯ ⇢ SLMAEVE): AMD k10temp + NVIDIA GPU in stats, no 5-min timer hint.
MINT adapter m2: survives terminal resizes (redraws on SIGWINCH instead of painting at stale rows).
  zarya-daemon                    static header
  zarya-daemon -a                 entrance: glitch in, blink, glance around (~0.8 s)
  zarya-daemon -e RRGGBB -- L1 L2 L3   custom eye colour + header lines (zarya-greet)
  zarya-daemon --react ok|fail TITLE BODY   short reaction (shell hook, after long jobs)
  zarya-daemon --hold N -e RRGGBB -- L1 L2 L3   greeting: the pet printed N lines up stays alive and
                                     clickable until the first key, which is handed to bash
  zarya-daemon --live  (alias: pet)  lives in the terminal: idles, blinks, eye follows the mouse,
                                     sleeps, scans while jobs run, shows kitchen timers.
                                     space = poke · t = 5-min timer · q / Esc = leave
```

## zarya-daemon-desk

**d39 (mint-pack v56, 2026-11-07):** ПОДДЕЛКА's pieces on other songs (ШУМ 22:49-22:52: "are they only available for nightcore songs? or to any song" → "i like it lets make it happen"). `desk/06j-spread.py`: sets Form.spread from `nc_spread` (default 1) every tick; toggle «ПОДДЕЛКА · its pieces on other songs» at the end of ▶ Animations > On their own.

**d38 (mint-pack v54, 2026-11-07):** ПОДДЕЛКА (ШУМ 2026-11-07 21:38-21:42: nightcore animations for ПОДМЕНЫШ, keep the concept, nothing silly; "it goes faster ... as the songs say its speed up"; all 6 ideas; "built it"). `desk/06i-forgery.py`: finds nightcore / sped-up / nightstep edits by title, artist (channel names) or album, never slowed / reverb / daycore, pulls the original artist + title out of the title; the ratio r = original / edit from MusicBrainz (median of matching recordings, score ≥ 85, not edits, 1.04-1.7 × the edit), else Last.fm track.getInfo, else ×1.25; cached per song 30 days (misses 7) in `~/.local/share/zarya/forgery.json`. Hands it to ПОДМЕНЫШ every new song (1 s tick), never summons. Shouts with a 6th value are drawn that many cells higher (ТОН), capped at the window top. ▶ Animations > ▶ ПОДДЕЛКА (16 s preview) and On their own > «ПОДДЕЛКА · nightcore / sped up speeds it up» (`forgery`, default 1). Rulings by Claude, standing unless ШУМ changes them: a layer (ПРИМАНКА's mask can sit on top), no summon, nightstep = ДЕЛИКАТЕС on the drop + the speed layer around it.

**d37 (mint-pack v53, 2026-11-05):** ДЕЛИКАТЕС НА СЛУХ (top pick 3; ШУМ: yes to the ears version). `desk/06h-mind-deli.py`: a heard zarya-mind reading with `deli` is a third way into ДЕЛИКАТЕС next to the seed and the marks (wraps `dg_song`: hard, up to 2 blasts, drop smelled 7 s ahead, ДЕМОН stays in, no ПРИМАНКА from the reading, summons ПОДМЕНЫШ when ДЕМОН is out). The brain's ДЕЛИКАТЕС score under 0.15 vetoes it. Mid-song pickup every 5 s. Per song, from the second play. One log line per verdict. Toggle «ДЕЛИКАТЕС на слух» (`deli_mind`). Why: the grit score ranked Death Grips at the bottom (Hacker 0.21) and SOAD / Skrillex on top (0.73).

**d36 (mint-pack v52, 2026-11-05):** ЧАСТИ ПЕСНИ (AI part 2, piece b; ШУМ: top pick 1). `desk/06g-mind-parts.py`: the reading's part at the song position steers ПОДМЕНЫШ while it is in him: calm parts (calm / sad / tender / sweet / hollow) start no new blast, no ПАСТЬ, no ПРОВАЛ, and its mimicry fakes only his quiet acts; loud parts (hype / angry / defiant / dark) make ПАСТЬ 1 in 2 at an act's end. ДЕМОН ВЫГЛЯДЫВАЕТ: on a calm part with ≥ 30 s of calm ahead, while resident, it rots off and ДЕМОН witnesses that part; it comes back on the next loud part ≥ 20 s later; once per song; a new song hands over to the resident rules. A lyrics-only reading loses to the brain's ears (map section aggressive ≥ 0.7 or energy ≥ 0.75). One log line per part. Toggles «ЧАСТИ ПЕСНИ из чтения» (`mind_parts`) and «ДЕМОН выглядывает» (`mind_peek`). ♪ This song… adds «· heard · now <feel>».

**d35 (mint-pack v51, 2026-11-05):** ПРИМАНКА from the reading (AI part 2, piece a). `desk/06f-mind-lure.py`: zarya-mind's cached reading (`~/.local/share/zarya/mind/songs/<md5 key>.json`) with `dark_core` is a third way into ПРИМАНКА next to the marks and the brain's ears: at song start, or mid-song when the reading lands (looked for every 5 s). The ears veto it when a studied map is hard (aggressive ≥ 0.75) with no cute side (happy < 0.35, party < 0.5, no cute style); never on a ДЕЛИКАТЕС song. One log line per verdict per song. ♪ This song… shows «ЧТЕНИЕ · <about>» greyed. Animations > On their own toggle «ПРИМАНКА из чтения» (`lure_mind`, default 1).

**d34 (mint-pack v47, 2026-11-05):** ПОДМЕНЫШ ЖИВЁТ ЗДЕСЬ (ШУМ 2026-11-04 23:34: ПОДМЕНЫШ is the face everywhere except Zarya). `desk/06e-resident.py`: `resident=1` (default) makes it his default form with no time limit; ДЕМОН shows only on calm songs (after 20 s it rots off; back on the next song that is not calm, ≥ 60 s later, after 8 s of it), when ГОЛОД starves to 0 (back after `resident_rest` 20 min) or after Изгнать (back after `resident_banish` 30 min). Every way back is a Form.start, so СМЕНА plays. Starts while resident are open-ended; a stay from before v47 becomes open-ended at start. The ПОДМЕНЫШ menu / message skin is on whenever resident=1. Settings toggle «ПОДМЕНЫШ ЖИВЁТ ЗДЕСЬ». `resident=0` = d33.

**d33 (mint-pack v46, 2026-11-04):** ИГРА on top (ШУМ: in games he should be on top, just not clickable; d31 kept him running behind the game). Muffin stacks a focused fullscreen window above DOCK / keep-above windows, so while a game runs he is drawn in an override-redirect POPUP (`desk/06d-gamelayer.py`, like the screen events): never restacked by the WM, input shape empty, raised every second; his own window hides and comes back when the game ends. `game_layer=0` = d31.

**d32 (mint-pack v45, 2026-11-04):** МИМИКРИЯ acts (`desk/06c-mimic.py`, hooks in draw()): while ПОДМЕНЫШ fakes him the desk draws the act it picked (any of the 14 dances, his 7 reactions over the song's dance, asleep, startled) instead of the song's mode; a failed act (ПРОВАЛ) dances to a fake beat that doesn't fit the song. ▶ Animations > ▶ ПАСТЬ is a submenu with the 5 hunts, plus ▶ ПРОВАЛ.

**d31 (mint-pack v44, 2026-11-03):** СМЕНА + ИГРА. The way in / out between ДЕМОН and ПОДМЕНЫШ runs zarya-hurt's Morph in his window (`desk/06b-morph.py`, hook at the end of draw()). The way out picks a ritual from the song: song rule `ritual=` > Last.fm ritual tags > Death Grips → КУЛЬТ > metal tags → ПРИЗЫВ > hard → ЦИФРА > calm / no song → ГНИЛЬ; Изгнать (menu or the 2 s hold) always plays a ritual (calm song: the song's fixed pick; no song: by the song it came for). ▶ Animations > ▶ СМЕНА: the way in + each way out. ИГРА (ШУМ: "keep the whole thing but I can't click him"): a Steam game or a fullscreen window that is not a video keeps him on screen and animating with an empty input shape (no menu, no hold-to-exorcise, no ghost fade, no song study); `game_show=0` hides like before. Video check reads both WM_CLASS fields (fullscreen Firefox was not counted as video).

**d30 (mint-pack v42):** ▶ ПАСТЬ previews on the kick when a song plays.

**d29 (mint-pack v39, 2026-11-03):** ПОДМЕНЫШ skin: while it is in him, messages and the right-click menu wear its palette (dark flesh, #FF2244 frame, blood-tinted text, one glitched letter per title; `form_skin=0` off). СЛЕДЫ ride on his body (nearest body cell, moved with him) instead of floating in the empty corners of his box. ▶ ПАСТЬ in Animations.

**d28 (mint-pack v36, 2026-11-03):** event bus + director, first slice. Every log line and decision also goes to
`~/.cache/zarya/bus-YYYYmmdd.jsonl` (song + second, 14 days kept, `bus=0` off). Song starts / ends with mode, weather, epic,
ДЕЛИКАТЕС, ПРИМАНКА mark, weight. The reaction gates (reactions off, ПОДМЕНЫШ here, the stand fighting, one at a time,
gap × weight, too early) live in `Director`; a reaction whose moment came while a gate said no is logged as `skip` with the
reason, once per song. Decisions unchanged (parity: 40 scripted song sets, 420 reactions, 0 differences).

```
ZARYA ⇢ SLMAEVE :: ДЕМОН on the desktop. Mint guest version d1 of Zarya's desktop pet (zarya-daemon@zarya, v29).
Same sprite engine as the terminal pet (imports build() from ~/.local/bin/zarya-daemon), drawn with cairo.
Lives bottom-left. Watches: CPU / GPU / RAM, Spotify (now playing), long terminal jobs, overheating.
  hover / left click   stats (left click pins them; click a report to dismiss it)
  middle click         play / pause        scroll up / down   music volume (the player's own stream only)
  double click         next track          right click        menu
Hides while a fullscreen window (game, video) is focused or a Steam game runs. Log: ~/.cache/zarya-daemon-desk.log
d5 (mint-pack v12): two layers (body = sound, weather = mood), ЭПОС / КАВАЙ, ears / feet / visor body language,
    build → drop, МАКС, the Blackwall breach, ВОДОВОРОТ, jump fix (no split rows, whole pixels), permanent now-playing
    caption (click-through, only where nothing covers his corner), ghost on approach over apps, like / volume / stop-in.
    Config: caption=1, ghost=1, breach_gap=45 (seconds between breaches, -1 = never)
d4: music modes (zarya-music): listens through cava and dances per artist / sound; any MPRIS player (Spotify, Firefox, Chrome)
    right-click > "Mode for <artist>" teaches a mode; config fx=1 (0 = off), fx_fps=30
d3: writes ~/.cache/zarya-daemon/stats.json for the terminal docks
d2: kitchen timers (zt), game session report, Firefox/Chrome downloads, Steam installs, other notifier alerts,
    CPU load drives the visor (RunCat), break reminder, Spotify "up next" (opt-in: zarya-spotify-login)
d6 (mint-pack v13): DOCK window type, so Show Desktop (Super+D) leaves him and his caption on screen; hover bubble =
    stats only (the caption already shows song, mode, weather, next); its hint shows for the first 5 hovers; publishes
    ~/.cache/zarya-daemon/select-hold ("until since") so the terminal docks stop drawing while you select text.
d7 (mint-pack v14): right-click > Report… (what happened + description, saved with a snapshot in
    ~/.local/share/zarya/reports/, read with `zarya-report`); "Music animations ✓/✗" and "Fade over apps ✓/✗" show
    their state and log every change; caption says АНИМАЦИИ ВЫКЛ while off; no dancing to talk videos in a browser
    (no song match + no steady beat → РЕЧЬ). Files: ~/.cache/zarya-daemon/{fx-off,ghost-off}.
d8 (mint-pack v15): the calm modes from zarya-music m4 in the teach menus (ПРИВАЛ, ТРАССА, БОЛЕРО, БЕГ, НАПЕВ); passes
    the song's hook times (synced lyrics) to БЕГ; whole-screen events: a click-through overlay over the whole monitor for a
    few seconds at a song moment (song rule event=ascend[@M:SS]), never while a fullscreen app or a Steam game is up.
    Config screen=1 (0 = never). Preview: zarya-music show ascend.
d9 (mint-pack v16): ОДЕРЖИМОСТЬ (zarya-music m5) on hard songs, with its ritual (song rule > Last.fm tags > fixed pick per
    song); right-click > This song… > Peak (possession / Blackwall rift / auto) and Ritual; whole-screen СОШЕСТВИЕ fires once
    per play when he gets possessed (or song rule event=descend). Config possess_gap=60. Previews: zarya-music possess RITUAL,
    zarya-music show descend.
d10 (mint-pack v17): he gets hurt, and remembers (zarya-hurt h1): ТРИ ГВОЗДЯ on hard songs (half of them; the other half keep
    ОДЕРЖИМОСТЬ; song rule peak=nails|possess), Shift+click = you stab him, failed sudo passwords stick in him too; click a
    nail to pull it out; three nails = THE HAND (click him fast to free him); ПРЕИСПОДНЯЯ once a day at most on the biggest
    moment of a hard song; СОШЕСТВИЕ's hand now goes for him; scars, fear, grudges. Listening journal (zarya-journal j1):
    one line per play; he asks how a song feels only when you keep playing one he can't read; right-click > ДНЕВНИК.
    Config hurt=1 stab=1 sudo_nails=1 hell=1 journal=1 ask=1. Previews: zarya-music show nails|hand|hell.
d11 (mint-pack v18): ПРЕИСПОДНЯЯ removed. On hard songs routed to possession, the hand from the crack takes him under
    (СОШЕСТВИЕ v3, once per descent_gap minutes) and ПОДМЕНЫШ climbs back out: a lasting form (form_min, default 45; 0 = until
    driven out) with its own moves, lines and corrupted caption; right-click > Изгнать drives it out. While ПОДМЕНЫШ, the
    hardest moments raise ТЕНЬ (his big true shape) behind him. The hands are new (zarya-hurt h2). During every screen
    event he is painted on the overlay, in front of the cracks / lightning. Config form_min=45 descent_gap=180.
    Previews: zarya-music show descend | shadow | form | unform.
d12 (mint-pack v19): СОШЕСТВИЕ v4: no hand; the crack's lightning strikes him on the song's hits and rewrites him into
    ПОДМЕНЫШ (the scene reads the ear). ARCHIVED (off by default, code kept, previews still work): ТРИ ГВОЗДЯ (nails=1),
    Shift+click stab (stab=1), sudo nails (sudo_nails=1), THE HAND (comes only after nails), ТЕНЬ (shadow=1). With nails off,
    every hard song that is not a rift song is a possession song.
d13 (mint-pack v20): ПОСЛЕДНИЙ РУБЕЖ for epic songs (ЭПОС mode, or song rule event=stand): gold light, he plants a spear of
    light, leaps on the next big hit into a star flare, lands in a burst of gold, «…ЕЩЁ НЕ ВСЁ.»; blessed (gold rim, rising
    light) for the rest of the song. Once per play, at most every stand_gap minutes (20). Preview: zarya-music show stand.
d14 (mint-pack v21): ПОСЛЕДНИЙ РУБЕЖ is dark and stays inside his window (zarya-hurt LastStand): black sun, red sky, ink
    hatching, a cape and an iron blade; the horde comes in from the right on the hits and he cuts it down on the kicks (tally
    to 100); at the climax «…ЕЩЁ ДЫШУ.»; cape + blade stay for the rest of the song. Epic songs = ЭПОС mode, song rule
    peak=stand / event=stand, or power / symphonic metal tags (those never go to ПОДМЕНЫШ). Config laststand=1 horde=1 (0 = the
    stand without the horde), stand_gap=20. The gold full-screen version is archived.
d15 (mint-pack v22): right-click > Animations: play ПОСЛЕДНИЙ РУБЕЖ / ПОДМЕНЫШ / ОДЕРЖИМОСТЬ / ВОЗНЕСЕНИЕ now, and switch the
    last stand, the horde and ПОДМЕНЫШ on / off (saved in daemon.conf). Peak lists say what each peak is; This song… and
    Mode for <artist> both have one (the artist one = every song by them). ЭПОС is labelled as the last stand; the
    «КАК ОНА ЗВУЧИТ?» bubble can answer Epic. Config form=1 (0 = hard songs never turn him into ПОДМЕНЫШ).
d16 (mint-pack v23): reactions, like a side character watching the song: ШОК (surprise face when a song comes out of
    nowhere), ОГОНЬ (epic songs: he catches fire and keeps dancing, then charcoal + smoke), СДУЛО (a drop blows him over, he
    spins and lies dizzy). Short, at most one of each per song, 75 s apart. Config reactions=1. ПОСЛЕДНИЙ РУБЕЖ no longer
    starts on its own by default (laststand=0; Animations menu turns it back on). Menu: 8 items at the top (Settings and More
    hold the rest), every Cyrillic label has its English in grey. ВОЗНЕСЕНИЕ without the horizon line. The song caption no
    longer folds away when a window covers its spot (caption_fold=1 brings the old fold back).
d17 (mint-pack v24): ШОК removed (ШУМ: out of character). СДУЛО is no longer a dizzy spin: the drop's air pushes him off
    the left edge, wind streaks keep blowing, he walks back in leaning into it with his visor narrowed, a gust shoves him
    back once, then he straightens up. Reactions stay in his style: nothing cartoonish.
d18 (mint-pack v25): the rest of the reactions, in his style: МУРАШКИ (epic drop: horns grow, outline bristles), КАДР (epic
    climax: the frame freezes, letterbox + speed lines), СЛЕЗА (sad climax: one tear out of the visor, wiped), ИСКРЫ (fast hats:
    static arcs between the horns), ОБИДА (a song skipped mid-peak: he turns his back), scroll the volume up at a peak = СДУЛО,
    a rare godlike epic peak (МАКС > 2.5 s past half, once per 3 h) = ВОЗНЕСЕНИЕ. Third play of a song today: «ОПЯТЬ?».
d19 (mint-pack v27, zarya-hurt h6): ПОДМЕНЫШ grows: ГОЛОД (each hard song feeds it and adds 10 min, calm songs starve
    it until it dies off; meter in the caption), МИМИКРИЯ (now and then it plays at being ДЕМОН, a beat late, title with
    one wrong letter), СОПРОТИВЛЕНИЕ (the first Изгнать fails with «НЕТ.» and a tear; hold the left button on him 2 s to
    force it), СЛЕДЫ (red dead pixels on him for the rest of the day, he flinches at the song it took him on), the caption
    shows the song's lyric line rewritten, stronger after midnight. stats.json carries `changeling` for the terminal dock.
d20 (mint-pack v28, zarya-brain b1): the song brain. The first time a song plays through, he records it and studies it in
    the background (sections, which repeat, the chorus, drops and the builds before them, energy, key; with the Essentia
    models mood, danceability, voice, style). From then on: his moves change exactly at the song's sections, he winds up
    before a drop he knows is coming and lands it on time, the sound's mood sets the weather when nothing else does, and
    your Spotify history weights his reactions (favourites twice as often, songs you mostly skip half). Caption: ПРИПЕВ,
    ДРОП ▸ 3, ИЗУЧАЮ while he studies. Config brain=1. CLI: zarya-brain now | list | show | study FILE | forget.
d21 (mint-pack v29, zarya-brain b2): the rest of the song brain. He sings along on a sung chorus (the visor becomes a
    voice waveform that follows the loudness); the sound's style picks the dance mode when no artist / song rule does
    (Discogs styles matched to zarya-music's tag words, before the ear's own guess); the lyrics' mood is read per map
    section, so a sad verse into a hype chorus changes the weather mid-song; favourites get ВОЗНЕСЕНИЕ twice as often.
d22 (mint-pack v30): ОБИДА's turned back is his body colour (it picked the eye green), checked on the real sprite;
    the terminal dock k6 shows ПОДМЕНЫШ (stats.json `changeling`).
d23 (mint-pack v31, zarya-hurt h7, zarya-brain b3): ПОДМЕНЫШ moves like Death Grips sound (never tweens, ahead of the kick,
    voice clips the visor, crushed masters flatten it, cuts skip frames, rots over a long song, flies when starving) and the
    hype blows it up once per hard song inside his window: ЧУЕТ → ЗАВОД → ДУША ВОН → ДЕТОНАЦИЯ → СБОРКА. ДЕЛИКАТЕС (Death
    Grips, v31 by name): it comes for the song by itself (the lightning, no 180 min gap), winds up earlier, blows up twice;
    Steroids (the 22-minute megamix) four times. КРИК: the red line follows the song (silent verses, chorus words one per
    vocal hit, its own build lines). ДЕМОН himself says one line only on godlike moments (КАДР, ВОЗНЕСЕНИЕ).
    Right-click > ▶ Animations > ▶ ДЕТОНАЦИЯ while ПОДМЕНЫШ is out.
d24 (mint-pack v32, zarya-hurt h8, zarya-brain b4): drops on the first play: the blast waits for build -> gap -> slam and lands
    on the first kick of the drop (EDM / dubstep included); any song that is not calm or epic gets one blast on a real drop.
d25 (mint-pack v33, zarya-hurt h9, zarya-brain b5): ПРИМАНКА for cute songs with a dark core (seed: Sewerslvt, Utsu-P, Purity
    Filter; + artists you mark; + the brain's guess from the sound): mask, cracks, strings, sweet shout, two faces, sugar.
    ДЕЛИКАТЕС also: Excision, HE$H, Must Die!, Space Laces, 12th Planet + artists you mark (German hard techno: mark them).
    Right-click > ♪ This song… > ДЕЛИКАТЕС / ПРИМАНКА · mark <artist>. Marks: ~/.config/zarya/classes.conf. lure_auto=1.
Config ~/.config/zarya/daemon.conf: unit=5 (pixel size), music=1, x=20, y=20 (margins from the bottom-left),
    break=60 (minutes at the desk before a break reminder, 0 = off), downloads=1, steam=1, games=1, game_min=5 (shortest session that gets a report)
```

## zarya-dock

**k7 (mint-pack v47, 2026-11-05):** ПОДМЕНЫШ is the face: its own dock body (ДЕМОН's 14×10 silhouette worn by it, red edge, red 2×2 eyes in the visor, dark flesh) whole inside the strip with a 1-cell margin on every side; it uses all 6 dock rows and the rule runs on to the right of its horns; no laptop; never tweens (holds, row skips, ВПЕРЕДИ lean, eye cuts, dead edge cells when hungry or rotting). Eyes back at your prompt / on the running command / wide on a failure. The k6 body (zarya-hurt's Form, 18×14) was cropped by the 10-pixel strip. Also ПОДМЕНЫШ when the desktop ДЕМОН is not running and `resident=1` («ЖИВЁТ ЗДЕСЬ · desktop ДЕМОН off»). ДЕМОН with his laptop when he is out (calm songs).

```
ZARYA ⇢ SLMAEVE :: ДЕМОН dock (Mint guest, k6: while ПОДМЕНЫШ is in the desktop ДЕМОН it is in the dock too: closes the
laptop, stares at your prompt, «НЕ ОН ✕rc» on failures, waits on your commands; k5: holds still while you select text (GNOME Terminal drops a selection
when output lands during the drag, or on rows inside it); the desktop ДЕМОН d6 writes select-hold. k4: ♪ line shows the desktop ДЕМОН's music mode; k3: fixed the random crash on indented code lines; k2: no hands, lines clipped + autowrap off). k1: A fixed strip at the bottom of the terminal where ДЕМОН sits
with a little laptop and keeps typing. The shell scrolls above it (scroll region 1..rows-6), so scrollback works.
  at the prompt   types code on the laptop, glances at you, blinks; sleeps after 10 min (lid closes)
  command running visor scans, laptop shows a progress sweep and the command + elapsed time
  command failed  Blackwall glitch burst, laptop screen corrupts red, СБОЙ ✕code until the next success
  long job done   poke + green check on the screen
Pauses (draws nothing) while a full-screen / raw-mode program owns the terminal (vim, less, htop, ssh, pet…)
and while apt / dpkg draw their own progress bar. Started by the ZARYA terminal bashrc block; `dock off` stops it.
  zarya-dock --tty /dev/pts/N --shell PID [--rows 6]
```

## zarya-greet

**k7 (mint-pack v47, 2026-11-05):** ПОДМЕНЫШ face: red ▚▚, blood-pale phrase with one letter it got wrong (same letter per phrase); without the dock: «НЕ ОН ⇢ SLMAEVE» header and red eyes (the pet body is zarya-daemon's and stays violet). Who is the face: the desktop ДЕМОН's stats.json, or `resident` when it is not running.

```
ZAЯYA terminal greeting v29: ДЕМОН header + one stats line + the ▚▚ phrase.
MINT adapter m1 (crossover guest on SLMaeve): visitor label, weather from a status file, GPU temp, phrases in ~/.config/zarya.
MINT adapter m2: hands the phrase line to the pet so it can reprint the greeting after a resize.
Old framed HUD kept as zarya-greet.pre-v29. ZARYA_GREET_STATIC=1 skips the animation.
```

## zarya-hurt

**h22 (mint-pack v56, 2026-11-07):** the pieces on other songs (`hurt/03e-spread.py`): hard songs blast in turns (the old one, ПЕРЕМОТКА, ПИТЧ, КОНФЕТТИ; normal speed; ДЕЛИКАТЕС skips КОНФЕТТИ); ПРИМАНКА songs (and its preview) get УШКИ in choruses, ЗВЁЗДОЧКИ on hats, СЕРДЕЧКО in sung parts when the mask is off; loud parts (level > 0.6) of any song get ПЫЛЬ (≤ 30) and СБОЙ (≤ 5 drops) at normal speed. Edits keep h20 / h21 alone. 03d: `_nc2_dust_rain` takes caps; `_nc2_heart` finds the eye wherever ТИК put it (it vanished in ~a third of ТИК frames). Tests `tests/spread-v56.py` 16/16 (×5), forgery-v55 61/61 (×3, version + menu checks updated).

**h21 (mint-pack v55, 2026-11-07):** ПОДДЕЛКА 2 (ШУМ 22:31: "there is only movement … make new explotions and make more fast … pixels everywhere … some kawaiiish things but all following the main concept of creepish"; 22:32 "all 1 to 12"). `hurt/03d-forgery2.py`: БОЛЬШЕ ВЗРЫВОВ (an edit counts as hard: 2 blasts, 3 from ×1.30; v54's Cascada edit had none) · three blasts in turns, shards ×r: ПЕРЕМОТКА (rebuilds like a tape scrubbed backwards, one pixel left in the wrong place for the song), ПИТЧ (rips apart in strips, upper rows faster, rows alternate sides), КОНФЕТТИ (pink / white pixel hearts and stars; hearts crack on the floor and leave red stains that rot, stars blink into a red eye) · ХЛОПОК (6-10 pixels pop off its body every 4 bars in loud parts / chorus start, ≥ 3 s apart) · ПЕРЕГРУЗ (loud parts: 2 of every 5 frames held) · ПОЛОСЫ (streaks behind jumps) · ПЫЛЬ (dark-red dust rising r× fast, hops on kicks) · СБОЙ (pixel rain, freezes a frame on kicks) · УШКИ (choruses: horns bend into cat ears, a red horn tip inside the left one, flick on hats, a blast snaps them back) · ЗВЁЗДОЧКИ (sparkles on hats, each one an eye for a frame) · СЕРДЕЧКО (sung parts: heart eye with a red pupil, cracks on hard hits). All inside his window. 03c: jolts 0.45 (was 0.2), jumps 2-3 cells, more of them; the preview is 22.6 s with the three blasts; its own shouts can't be covered by a random line. Tests `tests/forgery-v55.py` 61/61 (×5).

**h20 (mint-pack v54, 2026-11-07):** ПОДДЕЛКА + НЕТЕРПЕНИЕ (`hurt/03c-forgery.py`): on an edit ПОДМЕНЫШ runs at its speed ratio r. РАЗГОН (2 bars at the original speed, 4 snaps a second, then a hard cut on a kick, «×r»); ТАКТ ×r (moves change every 22 / r s); ДВОЙНОЙ ШАГ (steps on the 8ths, 16ths from ×1.25, plus hats); ПРЫЖОК ((r − 1) × 1.5 of steps teleport 1-2 cells for 0.1 s); ВЗГЛЯД (the slit jumps every step); НЕ СТОИТ (calm parts: horn flick / foot tap / nudge / blink every 0.2-0.3 s / r); ВПЕРЕДИ ×r (≤ 150 ms); НЕ ДОСЛУШАЛ (acts last 1 / r, (r − 1) × 2 dropped halfway, the next act r times sooner); ОРИГИНАЛ (ДЕМОН's dim ghost bobs on beat × r behind it; every 8 beats of drift they line up on a kick and it loses a row bottom up; gone by ~85 % of the song); СЛЕД (2-3 stale copies in fast parts); ПОДПИСЬ (the label starts as the original artist and is overwritten into ПОДМЕНЫШ in 0.3 / (r − 1) s, then «×r»); ОБРЫВ (shouts lose (r − 1) × 1.2 of their letters, the cut flickers once) + ТОН (each repeat of a shout higher by the semitone shift / 2 cells); УКРАДЕННОЕ ВРЕМЯ (an edit heard past half ends with «−m:ss.» and feeds ГОЛОД up to +0.12). Not during ПАСТЬ or ПРОПУСК; the arc keeps its look (ghost only). Tests `tests/forgery-v54.py` 43/43.

**h19 (mint-pack v52, 2026-11-05):** РАСЩЕПЛЕНИЕ's two see-through side copies skip the horn cells (ШУМ's "cropped horns" screenshot 2026-11-05 06:24: the copies smeared the horn tips into a flat bar; nothing clipped). Form.part_feel (set by desk d36) is read by the d36 wrappers.

**h18 (mint-pack v45, 2026-11-04):** ПАСТЬ hunts (ШУМ: "different velocities… sometimes it stalks, sometimes he's scared, sometimes it misses, sometimes fast and more bloody"): ОХОТА (as h16), ВЫСЛЕЖИВАНИЕ (peeks in and out ~1.6 s first), СТРАХ (he sees it: eye hard left, shakes row by row; faster bites), ПРОМАХ (one lunge, he hops clear, it backs off; he is not eaten), БОЙНЯ (6 bites on every half beat, blood spray). Blood on every eaten bite: snaps to the floor, red → dark → rots away in 3-4 s. МИМИКРИЯ pool (`hurt/03b-act.py`): 23 acts from a shuffle bag, no repeat until all played. ПРОВАЛ: 1 in 4 acts with music is the wrong one for the song; its last 1.2 s the disguise breaks (red rim, visor slit, rows slip, a horn skips); then it snaps back or (1 in 2, not twice in 90 s) ПАСТЬ eats the failed copy.

**h17 (mint-pack v44, 2026-11-03):** СМЕНА (ШУМ: the change "just shows the changeling, no transition… feels off"). `Morph` + `form_cells` (`hurt/06a-morph.py`). Way in: ЗАРАЖЕНИЕ (red spreads from one cell, rows slice) → РАЗРЫВ on a kick (3 hard hops; some cells leave, some freeze) → ВИСИТ one beat (purple / red flicker, glyphs) → СБОРКА (slams back in a new order as ПОДМЕНЫШ, eyes last). Every Form.start asks for it; the lightning (СОШЕСТВИЕ) plays it on its final strike instead of a hard swap. Way out by ritual: ПРИЗЫВ (circle, horned shadow, dragged down 2 rows a kick, ДЕМОН rises from the light), КУЛЬТ (six hoods, a strip torn off per chant hit, purple underneath), ЯЗЫЧЕСТВО (bonfire burns it from the feet up, red moon turns white, antlers fall), ЦИФРА (deleted row by row, scanline tears, re-render), ГНИЛЬ (rots off, burst backwards). Nothing tweens; whole cells, steps or kicks.

**h16 (mint-pack v43, 2026-11-03):** ПАСТЬ fix (ШУМ: the changeling sometimes eats invisible or in "code form"): the eater copied ПОДМЕНЫШ's last live frame, so a vanished / glitched moment carried over. Now one clean snapshot at the start (base frame, no music, no mouse, state restored), body + outline + eyes, fully solid. Logs `ПАСТЬ body N cells`.

**h15 (mint-pack v42, 2026-11-03):** ПАСТЬ redone again (ШУМ: drawn teeth look silly / cliché; "it just eats it", left to right, nothing after): it comes in from the left edge and takes 4 bites across ДЕМОН, a hair before each kick (predicted from the last kicks; its own rhythm, a fast double bite, a pause, a slow one, with no music or no kick heard). No teeth drawn: a scalloped wound, red for a moment, then bitten flesh. What is left of him keeps dancing a beat late. Visor blinks once before the last bite. Then it stands in his place. h12-h14 jaws retired.

**h14 (mint-pack v41, 2026-11-03):** ПАСТЬ: fewer teeth (ШУМ: "excess of teeth… looks a bit silly"): 4 uneven fangs on top, 3 below, gaps between them, drawn in front of ДЕМОН while he is in the mouth; the bite closes as an overbite.

**h13 (mint-pack v40, 2026-11-03):** ПАСТЬ redone as ПОДМЕНЫШ's own mouth (ШУМ: "the jaw should be the changeling's, eating ДЕМОН"): it rears up behind the fake 1.45× bigger, its body split at the visor line into two jaws with ДЕМОН standing in the mouth; half frame; the bite (gone, jolt, violet out of the seam); it chews; snaps down to 1.2× then its own size. The separate skull of h12 is gone.

**h12 (mint-pack v39, 2026-11-03):** ПАСТЬ (ШУМ's sketch): at the end of a mimicry act, about 1 in 3, once per song, a huge red jaw (deep skull, tapering snout, fangs) snaps shut on the fake ДЕМОН: open (shivers), one half frame, shut with a jolt (violet squeezed out, dripping a cell at a time), a crack open: empty, gone. Held frames only, inside his window.

**h11 (mint-pack v38, 2026-11-03):** ПОДМЕНЫШ's live arc (no song map) waits until 25 s into the song (was 8 s): the band coming in after an intro no longer reads as build → gap → slam (seen on Crystal Castles "Kept" and Deftones "Headup", 0:08-0:10). Mapped drops are unchanged.

```
ZARYA ⇢ SLMAEVE :: ДЕМОН gets hurt (h9, mint-pack v33; h8 v32; h7 v31; h6 v27; h5, mint-pack v21; h4 v20; h3 v19; h2 v18; h1 v17).
h9: ПРИМАНКА, the lure (cute songs with a dark core: Sewerslvt, Utsu-P, Purity Filter…): it wears a cute mask it does not
    understand (one eye a cell low, the smile a cell too wide) that flickers to the slit on hard hits (МАСКА), cracks at every
    dark turn and falls off at the drop (ТРЕЩИНА), hangs on pink strings and snaps pose on breakcore chops (КУКЛА), shouts
    pink lowercase with ♡ that turns into red caps ✕ on the dark hits (СЛАДКИЙ КРИК), switches face with no transition at
    section changes (ДВА ЛИЦА), and the song feeds it a little but makes it twitchy (САХАР). Never summons it.
h8: the drop, live: ЗАВОД starts on the build (loudness rising / snare roll speeding up), ДУША ВОН in the gap (drums cut or
    the level falls), ДЕТОНАЦИЯ on the first kick of the slam; no slam in 3 s = the soul comes back. A flat-loud song with no
    build (Death Grips) still blows up on a big kick. With a map the blast snaps to the real kick within 0.12 s. Songs with a
    drop count even when not "hard" (only the build -> gap -> slam pattern); calm and epic songs never.
h7: ПОДМЕНЫШ moves like Death Grips sound: it never tweens (snaps, holds, skips), lands AHEAD of the kick (ВПЕРЕДИ), its voice
    clips the visor (ГЛОТКА), a crushed master flattens it (БРИКВОЛЛ), section cuts skip frames and silence makes it vanish
    (ПРОПУСК), it rots over a long hard song (ГНИЛЬ), flies when starving (ПАДАЛЬ). Once per hard song the hype blows it up:
    ЧУЕТ → ЗАВОД → ДУША ВОН → ДЕТОНАЦИЯ → СБОРКА (inside his window; the drop's own hits put it back together; РЕКОРД).
    ДЕЛИКАТЕС (Death Grips): earlier wind-up, two detonations, Steroids four. КРИК: the red line follows the song: silent
    verses, chorus words one per vocal hit, its own lines on the build.
h5: ПОСЛЕДНИЙ РУБЕЖ is now dark and inside his own window (LastStand): black sun, red sky, cape, iron blade, the horde,
    «…ЕЩЁ ДЫШУ.»; cape + blade stay for the rest of the song. The gold full-screen version (h4) is archived as stand_gold.
h4: ПОСЛЕДНИЙ РУБЕЖ, the last stand for epic songs (gold light, spear, leap into a star flare, impact burst, «…ЕЩЁ НЕ ВСЁ.»),
    then he is blessed (gold rim, rising motes) for the rest of the song.
h3: СОШЕСТВИЕ v4 = the crack's lightning strikes him on the hits and rewrites him into ПОДМЕНЫШ (no hand). ARCHIVED (code kept,
    the desk no longer triggers them; previews still work): ТРИ ГВОЗДЯ, THE HAND, the hand descent, ТЕНЬ. Module for zarya-daemon-desk (no CLI of its own).
Everything here happens TO him: he sees it coming, reacts, fights, wins or loses, and remembers.
  ТРИ ГВОЗДЯ   nails fly in on the hard hits of a hard song; he dodges on the beat, or one sticks: ear droops, limp,
               eye flicker. Click a stuck nail to pull it out. Shift+click him = you stab him. Three failed sudo
               passwords = three nails. Three nails stuck = THE HAND.
  THE HAND     (h2) no arm: a rift opens in the top edge, the hand comes out of it (its wrist frays into smoke), five
               fingers too long with one joint too many, long black nails, ash skin, an original bind-rune carved in the
               palm (Thurisaz + Naudiz on one stave, our own combination). It grabs him and pulls: click him 6 times to
               free him, else it takes him into the rift and slams him back.
  СОШЕСТВИЕ v3 the bottom of the screen cracks; the hand climbs out of the crack under him, takes him and drags him
               under. The crack pulses. Something climbs back out in his shape: ПОДМЕНЫШ.
  ПОДМЕНЫШ     (the changeling) a lasting form (45 min by default, right-click > Изгнать ends it): black body, red rim,
               slit eye, long horns, its own moves (ЛОМКА contort, ТИК teleport twitch, ПАУК eight legs, РАСЩЕПЛЕНИЕ split,
               ПЕРЕЗАПИСЬ rewritten as glyphs, ВЗГЛЯД stares at your cursor and lunges), machine lines, corrupted caption.
  ТЕНЬ         while ПОДМЕНЫШ, at the hardest moment his true shape (the big demon) rises half-transparent behind him.
  He is always drawn in front of these scenes. ПРЕИСПОДНЯЯ (h1) is gone.
  MEMORY       scars (fade over 3 days), fear (after a hand, he flinches when a window slides over his corner),
               grudges (songs that hurt him make him nervous when they start again). ~/.local/share/zarya/demon/memory.json
Original designs only (mood references: Chainsaw Man's hands, Berserk's Hand of God figure; nothing copied).
```

## zarya-journal

**j4 (mint-pack v49, 2026-11-05):** ДНЕВНИК shows zarya-mind's reading under each song (what it is about, mood, dark core) and the newest week read at the top of WEEK / MONTH / ALL. Nothing changes when zarya-mind never ran.

```
ZARYA ⇢ SLMAEVE :: ДЕМОН's listening journal (j3, mint-pack v26: Spotify history summary, light ДНЕВНИК; j2 mint-pack v18; j1 v17: plays as ПОДМЕНЫШ show as their own mode). Module for zarya-daemon-desk + a CLI.
The desktop ДЕМОН writes one line per play: what played, how long you really listened, skipped / finished / replayed,
♥, volume changes, the mode + weather he chose and why, his peaks, what hurt him, the ear (BPM, loudness, 808, beat),
the app in front, Lima weather, hour. You never write a note per song: he asks only about songs you keep playing
that he still can't read.
  zarya-journal                today: plays, top songs, skips
  zarya-journal week | top [DAYS]
  zarya-journal diary          build + open ДНЕВНИК (interactive page) ~/.local/share/zarya/listening/dnevnik.html
  zarya-journal ask            songs he would like your feeling about (played ≥ 3×, mode only from the ear)
  zarya-journal lastfm USER    pull your Last.fm scrobbles (phone, other PCs) into the journal (API key: ~/.config/zarya/lastfm.key)
  zarya-journal import PATH    Spotify extended streaming history (the zip or its folder, or one .json) → backfill
  zarya-journal history        your whole Spotify history: hours per year, top artists and songs (j3)
  zarya-journal export         ~/Downloads/demon-journal-<stamp>.tar.gz (journal + reports) to attach for Claude
  zarya-journal path
Files: ~/.local/share/zarya/listening/{plays-YYYY-MM.jsonl, lastfm.jsonl, spotify.jsonl, spotify-summary.json, asked.json, dnevnik.html}
       ~/.config/zarya/journal.conf  (lastfm_user=…)
```

## zarya-mind

**m4 (mint-pack v53, 2026-11-05):** the ears prompt also answers `deli` (Death Grips-grade voice-as-drum + abrasive electronics + hard cuts, heavy dubstep, German hard techno; false for metal, punk, rock, plain EDM, trap, phonk, clean rap, soft songs). Heard readings store `ears_id`. On start, songs heard by m3 (no `deli`) lose their ears-done marker once, so the brain clips them again on their next full play.

**m3 (mint-pack v52, 2026-11-05):** EARS: Gemini hears the song. A clip the brain cut goes out with the lyrics (if known) as one inline `audio/wav` part; the answer adds `sound` (one line on delivery / instruments), section feel judged by hearing each excerpt, dark core from sound + words; songs without lyrics get read from the sound. The reading is marked `heard`; the clip is deleted and `~/.local/share/zarya/mind/ears-done/<id>` written. 400 with audio → the text reading stays, clip dropped; bad answer twice → given up; 429 / 503 → backoff, clip waits. Lowest priority after the song playing now. `zarya-mind ears`, status shows ears. `reread` now only redoes m1 readings.

**m2 (mint-pack v50, 2026-11-05):** first real calls: Steroids read as "barrage of industrial beats… identity exploration" (sound guessed, filler) with sections only to 3:20 of a 22-min mix (lyrics cut at 3,500 characters); `backfill` died on a Google 503. Now: lyrics sampled evenly over the whole song; "about" must say what the words say, never the sound, banned filler words, medleys named as such; 500/502/503/504 → the fallback model, then a 2-min wait (not a failure); `backfill` / `reread` wait out short backoffs; `reread` redoes m1 readings.

**m1 (mint-pack v49, 2026-11-05):** new. ДЕМОН's reading of songs, free only: Gemini free tier (`~/.config/zarya/gemini.key`, billing never linked). Per song with lyrics, once, cached forever in `~/.local/share/zarya/mind/songs/`: what it is about (≤ 2 sentences, no lyric quotes), ≤ 3 mood words from a fixed list, mood per lyric section, cute-surface / dark-core flag. Once a week (Sunday from 20:00): a ≤ 110-word read of the week from play counts only. Never in games (ДЕМОН's `game:` bus lines, or Steam's `SteamLaunch` process), daily cap 60, 20 s gap, 429 backoff (Retry-After / retryDelay, else 10 min doubling to 6 h), 404 → fallback model, 400 in JSON mode → plain retry, unusable answers never cached. Model `gemini-3.5-flash-lite`, fallback `gemini-3.1-flash-lite` (Google model list 2026-10-28). Service `zarya-mind.service` (Nice 15). Key never printed or logged.

## zarya-music

```
ZARYA ⇢ SLMAEVE :: ДЕМОН music modes (m5, mint-pack v16; m4 v15, m3 v14, m2 v12). Module for zarya-daemon-desk + a small CLI.
  zarya-music                 what is playing, which mode + weather, and why (read from the desktop ДЕМОН)
  zarya-music tags            what the lookups found for this song: Last.fm tags, credits, lyrics mood
  zarya-music teach MODE      the current artist always gets MODE        (artist rule)
  zarya-music song MODE       only this song gets MODE                    (song rule)
  zarya-music feel WEATHER    this song feels rain | clear | storm | dawn | auto
  zarya-music forget          drop the taught rule for the current artist
  zarya-music try MODE [S]    force MODE for S seconds (default 30) to preview it
  zarya-music listen [S]      print what the ear hears every second (tuning)
  zarya-music rules           show the rules files
  zarya-music show ascend     preview a whole-screen event (m4; m5: show descend; m6: show nails | hand; m7: shadow | form | unform)
  zarya-music possess [summon|cult|pagan|none]   preview ОДЕРЖИМОСТЬ while a song plays (m5)
  zarya-music peak possess|stand|rift|auto [--artist]   the big moment for this song (or every song by this artist) (m11)
  zarya-music show            list the animations you can preview (m11)
  zarya-music ctl play|next|prev|vol+|vol-|like|stop-in MIN|stop-cancel   (global shortcuts call these)
Modes: break (liquid / jungle) · memory · nod (loose) · mosh · kendrick · grips · groove · epic · kawaii
Two layers: the BODY moves with the sound (mode, per section); the WEATHER is the mood (rain, clear, storm, dawn).
Mood sources, in order: your song teaching > rules > Last.fm tags (~/.config/zarya/lastfm.key) > synced lyrics (LRCLIB).
The ear: cava 0.7.x raw output (16 bars, 60 fps) from the default output's monitor; runs only while music plays.
```

## zarya-report

**r3 (mint-pack v38):** digest: one block per song (a hunger line written just before the song start no longer splits it); empty `peak: drop (charge 0.00)` flags hidden.

**r2 (mint-pack v37, 2026-11-03):** `digest [DAY] [--all]` reads the bus per song: what fired at which second, what was held
back and why, your stamps. `feel wrong | right | list`: Super+Alt+F / Super+Alt+G stamp song + second + the last 10 s of bus
events into `~/.local/share/zarya/feedback/`; felt-wrong asks one word (too much / too little / wrong moment / wrong mood,
Esc = none, 12 s timeout). `export` also packs the stamps and the last 3 days of bus.

```
ZARYA ⇢ SLMAEVE :: zarya-report r1 (mint-pack v14). Reads the reports saved from right-click ДЕМОН > Report….
  zarya-report                 last 15 reports (newest last)
  zarya-report list [N]        last N (all: 0)
  zarya-report show [ID|#N]    one report in full (default: the newest): what you wrote + what he was doing
  zarya-report export          everything into ~/Downloads/demon-reports-<date-time>.tar.gz (attach that in the chat)
  zarya-report path            where they live
Files: ~/.local/share/zarya/reports/<YYYYmmdd-HHMMSS>.json + index.log. Uninstalling mint-pack never deletes them.
```

## zarya-say

```
ZARYA v29 (Mint guest d1) :: hand a report to the desktop ДЕМОН.  zarya-say [-l info|ok|warn|crit] [-a zd|backup|top|disk|portal] TITLE [BODY] [HINT]
```

## zarya-spotify-login

```
ZARYA (Mint guest d5) :: connect ДЕМОН to the Spotify Web API: the song that plays next, full credits (feat. artists), ♥ like.
d5 adds the library scope for ♥ like: run it once more if you connected before mint-pack v12.
One time. Spotify needs a developer app owned by a Premium account (Spotify rule since 2026-02).
  1. https://developer.spotify.com/dashboard → Create app
     Redirect URI: http://127.0.0.1:8899/callback   ·   API: Web API
  2. Copy the app's Client ID, then run: zarya-spotify-login <CLIENT_ID>
Uses Authorization Code + PKCE (no client secret). Token saved to ~/.config/zarya/spotify-token.json (0600).
Undo: delete that file (or Spotify → Settings → Apps → remove access).
```

**m13 (mint-pack v45, 2026-11-04):** fix: the dance's particle list resets when the mode changes. Rain drops from МЕМОРИ (3 values) crashed the Kendrick sparks (5 values) on a mode switch; mimicry switches modes often.
