# Crossover: ДЕМОН module map + repo plan

Version 3 · 2026-11-03 11:25 (Lima) · owner: ШУМ (shum) · device: SLMaeve · status: **v34.1 installed** (repo + credits); **v35 delivered** (physical split); v36-v37 planned
Read this before touching any ДЕМОН code. **Since v35: read `~/.local/lib/zarya/INDEX.md` (part → classes / methods), then only the part you need.**

## 0. Credit (binding, 2026-11-03 09:00)
- **Handle: ШУМ** (Cyrillic, in visuals, headers, About) / **shum** (Latin, anywhere typed: git, GitHub, Twitch, URLs). Meaning: "noise".
- **Never** a real name, email or username in code, headers, commits, credits or anything that could be published.
- Header line in every file: `# ДЕМОН · concept + direction: ШУМ (shum) · built with Claude (Anthropic)`
- Git author: `ШУМ (shum) <zumdudd@users.noreply.github.com>` (GitHub zumdudd, display name ШУМ). Commits carry `Co-Authored-By: Claude <noreply@anthropic.com>`.
- `CREDITS.md` in the repo: who had the idea (ШУМ), how it was built (direction by ШУМ, code by Claude, decisions dated), how it ran (link to change log), contact (shum's GitHub, when it exists).
- Menu: More > **About · ОБ АВТОРЕ** shows «ДЕМОН · ШУМ» + version.

## 1. Measured state (2026-11-03 09:05, read from SLMaeve through the bridge)
| File | Size | Lines | Shape |
|---|---|---|---|
| `zarya-daemon-desk` d25 | 165 KB | 2500 | **`Demon` = 1607 lines, 90 methods** (window, Steam, downloads, menus, music, events, caption, report, ghost, speech all in one class); `Reactions` 227, `Music` 111, `Stats` 59, `ScreenFX` 36. 11 KB of d1-d25 changelog comments at the top. 33 config keys read inline |
| `zarya-music` m11 | 147 KB | 2442 | **`Dance` = 1288 lines, 52 methods** (modes, possess, breach, rituals, peaks, Death Grips); `Ear` 187; 55 top-level functions (CLI, Spotify, Last.fm, LRCLIB, rules) |
| `zarya-hurt` h9 | 133 KB | 2085 | `Form` (ПОДМЕНЫШ) 694 lines; `Hurt` 245; `LastStand` 150; **408 lines of archived classes** (HandGrab, DescendHand, HandArt2, Shadow, gold Stand) |
| `zarya-brain` b5 | 39 KB | 661 | `study()` 177 lines; `Brain` 189 |
| `zarya-journal` j3 | 33 KB | 446 | fine as is |
| `zarya-daemon` v29.2 | 23 KB | 506 | terminal pet; loaded by desk as a module |
| `zarya-dock` k6 | 19 KB | 365 | loads desk / hurt for sprites |
| Total | **~560 KB** | | |

How they connect today: each script loads the others with `SourceFileLoader` (desk loads zarya-daemon, zarya-music, zarya-hurt, zarya-brain…; dock loads desk + hurt). Executables used as libraries.

Where "what fires when" lives today (scattered): `Demon.event_tick`, `hurt_tick`, `stand_tick`, `music_tick`, `decide`, `screen_event`, `Reactions.tick/_fire`, `Dance.possess/breach/_peaks_post`, `Form._arc_tick`, plus inline `cfg.get(...)` gates.

**Token cost today:** a ПРИМАНКА change reads desk + hurt (~300 KB) to edit ~5 KB, then a patch script on top of the d24 patch. Target after split: this map (~6 KB) + 1-2 modules (10-30 KB). Rough estimate (inference): **~10x less read per change.**

## 2. Target layout
Source repo on SLMaeve: `~/shum/demon/` (git). Installed package: `~/.local/lib/zarya/` (Python package `zarya`). The `~/.local/bin/zarya-*` commands stay with the same names, each a 5-line launcher (`from zarya.cli import music; music()`), so shortcuts, autostart, dock and habits keep working.

```
zarya/
  core/      config.py (all 33+ keys, one place, defaults + docs) · paths.py · log.py · state.py (stats.json, music.json)
  bus.py     Event(kind, t, song, sec, data) · emit() · subscribe() · every event logged (the digest source)
  director.py  priorities, cooldowns, "once per song", "not while ПОДМЕНЫШ fights", soft-song rules, history weights
  sensors/   ear.py (cava + Onset) · player.py (MPRIS, Spotify API) · brain_client.py (maps → section/drop/chorus events)
             · desktop.py (fullscreen, Steam, downloads, games) · stats.py (CPU/GPU/RAM) · clock.py (weather, night)
  brain/     study.py · essentia_study.py · grit.py · lure.py · weights.py · cli.py   (= zarya-brain)
  music/     modes.py (Dance minus possess/breach) · rules.py · lyrics.py (LRCLIB) · lastfm.py · spotify.py · cli.py
  actors/    one file per thing that plays:
             reactions/ (ogon, sdulo, murashki, kadr, sleza, iskry, obida, vozn) · possess.py (ОДЕРЖИМОСТЬ + rituals)
             · rift.py · descend.py (СОШЕСТВИЕ) · ascend.py (ВОЗНЕСЕНИЕ) · laststand.py · catharsis.py
             changeling/ form.py (ПОДМЕНЫШ body + law) · arc.py (ЧУЕТ → СБОРКА) · deli.py (ДЕЛИКАТЕС) · primanka.py · krik.py
  view/      window.py (GTK, place, ghost, hover) · sprite.py (ДЕМОН cells, palette) · caption.py · overlay.py · screenfx.py · menu.py
  apps/      desk.py (wires sensors → bus → director → actors → view) · dock.py · term_pet.py (zarya-daemon) · journal.py · report.py
  archive/   nails, hand, shadow, descend_hand, stand_gold (previews only, never loaded by desk)
CHANGELOG.md (the d1-d25 / h1-h9 / m1-m11 / b1-b5 comment headers, moved out of the code)
CREDITS.md · MODULES.md (= §3 of this doc, kept in sync) · tests/
```
Rule: no module over ~25 KB. If one grows past it, split it.

## 3. The bus and the director
```
sensors ──emit──▶ BUS ──▶ DIRECTOR ──trigger(name, event)──▶ actor.play()
                   │          │                                   │
                   ▼          ▼                                   ▼
          ~/.cache/zarya/bus-YYYYmmdd.jsonl   skip reasons      view (window, caption, overlay)
```
- **Events** (initial set): `song_start`, `song_end`, `section`, `build`, `gap`, `drop`, `chorus`, `vocal_hit`, `peak` (МАКС), `class` (ДЕЛИКАТЕС / ПРИМАНКА), `mode`, `weather`, `fullscreen`, `idle`, `menu`, `hotkey`, `external` (Twitch later).
- **Director** holds every "when" rule that is now inline: cooldowns (reactions 75 s × weight, СОШЕСТВИЕ 180 min, breach_gap 45 s), once-per-kind-per-song, blocks (soft songs, fullscreen, ПОДМЕНЫШ fighting), class routing (§3.5 of the Mint spec). Each decision logs `fired` or `skipped: <reason>`.
- **One door:** `trigger("ДЕТОНАЦИЯ")` is the same call from the director, the ▶ Animations menu, `zarya-music show`, tests, and later the Twitch adapter. External triggers go through the director too (cooldowns + kill switch).
- **Digest:** `zarya-report digest [today]` = per song: what fired at which second, what was skipped and why. Claude reads the jsonl through the bridge at the start of each session.
- **Felt-wrong hotkey:** Super+Alt+F (free in the current keybindings, to confirm) stamps song + second + last 10 s of bus events into `~/.local/share/zarya/feedback/`, then a 3-choice popup: *too much · too little · wrong moment · wrong mood* (or Esc = no word). Super+Alt+G = "felt right" (same stamp). Claude reads them through the bridge.

## 4. Migration order (each step = one mint-pack, installs / undoes like the others)
1. **v34 repo + credits (no behaviour change). Delivered 2026-11-03.** Create `~/shum/demon/`, `git init` with the current installed d25 / h9 / m11 / b5 / k6 / j3 / v29.2 / r1 as commit 1 (author shum), `CREDITS.md`, `CHANGELOG.md` (headers copied out, code unchanged), header line added to each file, About item. Installer checks `git` (apt if missing, the one sudo step). Test: installed files differ from d25 only by the header line + About.
2. **v35 the split (no behaviour change). Delivered 2026-11-03 11:25 as a *physical* split:** `zarya-daemon-desk`, `zarya-music`, `zarya-hurt` became 12-line launchers (same names, same `__file__`, same loaders) that run `~/.local/lib/zarya/{desk,music,hurt}/NN-*.py` in order **in one namespace**; 24 parts, each ≤ 24 KB; the three big classes (`Demon`, `Dance`, `Form`) are cut into contiguous method groups as mixins (`_Demon1…4`, `_Dance1…3`, `_Form1…2`), the class keeps `__init__` and its first methods. Changelog headers removed from the code (in `CHANGELOG.md`). **Parity:** rebuilding each script from its parts (mixins merged back) gives an AST identical to v34.1 except the version line (d27 / m12 / h10); runtime in Xvfb: same full menu tree, same method count, same `zarya-music --help` and `show`, same start log, dock loads hurt through the launcher, ДЕМОН runs as main. Tools: `tools/split.py`, `tools/parity.py` in the repo. Not done in v35 (needs real logic changes, moved to v36): the package / sensors / actors layout below, config into `core/config.py`, archive out of the load path (archived hurt classes still load, marked in INDEX.md). The original plan for step 2 follows, now the target of v36: Package `zarya/` as above, launchers in `~/.local/bin`, archive moved out, config into `core/config.py`. **Parity test:** the old d25 desk and the new desk run in Xvfb on the same scripted ear / MPRIS input (Creepshow-like EDM, a Death Grips-like track, a calm track, a lure track); decision logs and frame hashes must match. Ships only when they match.
3. **v36 bus + director + real modules.** Inline "when" rules move into the director one by one, parity test after each (decision logs on scripted input, old vs new). Bus log on. Parts become real modules (sensors / actors / view) as the director takes their rules; config into `core/config.py`; archive out of the load path.
4. **v37 digest + felt-wrong / felt-right hotkeys.**
5. Then features again (ДЕЛИКАТЕС by sound v34 plan becomes an actor + director rule). Twitch = `sensors/twitch.py` emitting `external` events, after this.

Build chain for Claude after v35: edit the module in a sandbox copy of the repo, run tests, ship the diff as a commit bundle (`git bundle`) or patch, installer does `git am` + copies to `~/.local/lib/zarya/`. Undo = `git checkout <previous tag>` + reinstall. No more patch-on-patch scripts.

## 5. Public copy
This repo is the public copy: personal data (listening history, journal, song maps, keys, tokens) never lives in the code; it stays in `~/.config/zarya` and `~/.local/share/zarya` on the owner's PC. Code: MIT. Art: CC BY 4.0.

## 6. Open
- ~~git on SLMaeve~~ 2.43.0 (confirmed 09:07). ~~Super+Alt+F / G~~ free (confirmed 09:07). ~~GitHub~~ zumdudd, display name ШУМ, no real name on the profile (checked 09:10); not linked to Claude, repo stays local.
- v34.1 installed 09:18; v35 delivered 11:25 (status in the Mint spec).

## Change log
- 2026-11-03 11:25 v3: v35 delivered as a physical split (launchers + parts + mixins, AST parity); logical layout moved to v36.
- 2026-11-03 09:25 v2: open items answered (git, keys, GitHub zumdudd); v34 built; names generalised for the repo copy.
- 2026-11-03 09:10 v1: measured the installed code through the bridge; layout, bus / director, migration order, handle ШУМ.
