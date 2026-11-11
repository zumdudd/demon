#!/usr/bin/env python3
# ДЕМОН · concept + direction: ШУМ (shum) · built with Claude (Anthropic)
"""showcase-video v1: the showcase video, 1920×1080, 25 fps, every pet frame from the real engine, synced to the track.

The track's map (kicks, snares, hats, sections, vocal spans) and its audio loudness drive the ear; a timeline starts
the scenes at the right moments the way a real song or the menu would (ЗАРАЖЕНИЕ, the mapped ДЕТОНАЦИЯ on the drop,
ПРИМАНКА, ПОДДЕЛКА, ПАСТЬ, КАДР, ГНИЛЬ). English captions (Cyrillic names, romanized once), burned in.

    python3 tools/showcase-video-v1.py media/track/map.json media/track/track.mp3 OUTDIR     # needs a display (Xvfb ok)

OUTDIR gets showcase.mp4 (H.264, faststart) and showcase.webm (VP9). Built on showcase-render-v2.py.
"""
import os, sys, subprocess, tempfile, importlib.util, json
os.environ.setdefault('SHOWCASE_U', '24')
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('R', os.path.join(HERE, 'showcase-render-v2.py'))
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
from PIL import Image, ImageDraw, ImageFont

MAP, AUDIO, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)
W, H = 1920, 1080; FPS = R.FPS; d, F, CLOCK = R.d, R.F, R.CLOCK
BG = R.BG; INK = (236, 232, 250); MUTE = (173, 167, 211); RED = (255, 34, 68); VIO = (157, 123, 255)

def font(size, bold=True):
    for p in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
              '/usr/share/fonts/TTF/DejaVuSans-Bold.ttf', '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf'):
        if os.path.exists(p): return ImageFont.truetype(p, size, layout_engine=ImageFont.Layout.BASIC)   # raqm clashes with GTK's harfbuzz
    return ImageFont.load_default()
F_CAP, F_SMALL, F_CRED = font(46), font(26), font(40)

# ---- the audio as the ear hears it
tmpd = tempfile.mkdtemp(prefix='showcase-video-'); wav = f'{tmpd}/track.wav'
subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', AUDIO, '-ac', '2', '-ar', '44100', wav], check=True)
m = json.load(open(MAP)); seg = {s['name']: s for s in m['segments']}
S = lambda name, off=0.0: seg[name]['start'] + off
lure, epic = seg['lure'], seg['epic']
lure_bar = 4 * 60 / lure['bpm']
dark = [(lure['start'] + b * lure_bar, lure['start'] + (b + 1) * lure_bar) for b in (3, 7)]
def aggr(pos):
    if lure['start'] <= pos < lure['end']: return 0.8 if any(a <= pos < b for a, b in dark) else 0.3
    return 0.8
deli_bar = 4 * 60 / seg['deli']['bpm']; drop_bar = 4 * 60 / seg['drop']['bpm']
def first_kick(t):                                                          # snap a target to the real kick in the map
    return min(m['kick'], key=lambda k: abs(k - t))
targets = [first_kick(S('deli')), first_kick(S('deli', 4 * deli_bar)), first_kick(S('drop', drop_bar))]   # the drops it blows up on
song = R.MapSong(MAP, wav, aggr=aggr, targets=targets)
WEATHER = dict(calm='rain', build='storm', deli='storm', lure='dawn', nightcore='clear', drop='storm', epic='clear', outro='rain')
MODE = dict(calm=('rest', ''), epic=('epic', ''), outro=('hum', ''))          # ДЕМОН's dance per part (he is out in these)
song.weather_fn = lambda: WEATHER[song.seg(d.music.position() or 0)['name']]
song.mode_fn = lambda: MODE.get(song.seg(d.music.position() or 0)['name'])

# ---- the timeline: (time, action)
key = [0]
def new_song(**kw):
    key[0] += 1; F.song(CLOCK.t, f'showcase-video-{key[0]}', **kw)
def take_him(dg=False):                                                       # ЗАРАЖЕНИЕ: the real way in (Form.start → СМЕНА)
    F.morph_skip = -99; F.start(CLOCK.t, 0, 'showcase', song=f'sv-{key[0]}'); F.next_mimic = CLOCK.t + 1e6
def arm(n, kind_i=None):                                                      # n detonations allowed from here, blast style picked
    F.det_max = n; F.dets = 0; F.det_t = -1e9; F.live_cd = 0; F.targets = None; F.smelled = False
    if kind_i is not None: F._sp_state(CLOCK.t)['kind_i'] = kind_i
def leave(rit_user=True):                                                     # it leaves him: the draw plays the way out
    d._exit_why = 'preview' if rit_user else ''; F.end(CLOCK.t, 'showcase')

TL = [
    (S('build', 0.05), lambda: (new_song(dg=True), take_him(), setattr(F, 'det_max', 0))),
    (S('build', 1.8),  lambda: (F.set_hard(True), arm(2, 0))),                # ЧУЕТ → ЗАВОД → ДУША ВОН → ДЕТОНАЦИЯ on the slam (classic)
    (S('deli', 4 * deli_bar - 4.0), lambda: (setattr(F, 'det_t', -1e9), setattr(F, 'live_cd', 0), F._sp_state(CLOCK.t).__setitem__('kind_i', 2))),   # the 2nd: ПИТЧ
    (S('lure', 0.02),  lambda: (new_song(lure=True), F.set_hard(False), setattr(F, 'det_max', 0), setattr(F, 'next_mimic', CLOCK.t + 1e6))),
    (S('nightcore', 0.02), lambda: (new_song(), F.forgery(CLOCK.t, dict(r=1.30, src='showcase', oartist='ПРИМАНКА', otitle='',
                                                                         orig_len=lure['end'] - lure['start'], edit_len=seg['nightcore']['end'] - seg['nightcore']['start'])))),
    (S('drop', 0.02),  lambda: (new_song(), F.set_hard(True), arm(1, 1), setattr(F, 'next_mimic', CLOCK.t + 1e6))),   # ПЕРЕМОТКА on the drop
    (S('drop', 5.6),   lambda: F.jaw_preview(CLOCK.t, True, 'hunt')),         # ПАСТЬ · ОХОТА
    (S('epic', 0.05),  lambda: leave(True)),                                  # a ritual way out, ДЕМОН is back
    (S('epic', 2 * 4 * 60 / epic['bpm']), lambda: d.react.start('frame', CLOCK.t, 'showcase')),   # КАДР «ВОТ ОНО.»
    (S('epic', 3 * 4 * 60 / epic['bpm']), lambda: (new_song(), take_him())),  # it never really leaves
    (S('outro', 1.0),  lambda: leave(False)),                                 # ГНИЛЬ: no song rule → it rots off
]

CAPS = [
    (S('calm', 0.6), S('calm', 5.0), 'ДЕМОН (demon) · a desktop pet'),
    (S('calm', 5.3), S('calm', 11.6), 'he listens to every song and dances'),
    (S('build', 0.1), S('build', 2.4), 'something takes his place'),
    (S('build', 2.6), S('build', 6.6), 'ПОДМЕНЫШ (podmenysh) · the changeling'),
    (S('deli', 0.05), S('deli', 3.6), 'ДЕТОНАЦИЯ · it blows up on the drop'),
    (S('deli', 3.9), S('deli', 8.4), 'ДЕЛИКАТЕС · its favourite songs'),
    (S('deli', 8.7), S('deli', 13.4), 'it moves a hair before the beat'),
    (S('lure', 0.1), S('lure', 4.3), 'ПРИМАНКА · a cute mask on a dark song'),
    (dark[0][0], dark[0][1] + 1.0, 'the mask slips'),
    (dark[1][0] - 1.2, seg['lure']['end'] - 0.1, 'ДВА ЛИЦА · two faces'),
    (S('nightcore', 0.1), S('nightcore', 4.2), 'ПОДДЕЛКА · a sped-up forgery'),
    (S('nightcore', 4.4), seg['nightcore']['end'] - 0.1, 'it knows a fake when it hears one'),
    (S('drop', 0.1), S('drop', 5.2), 'ПЕРЕМОТКА · the blast plays backwards'),
    (S('drop', 5.6), seg['drop']['end'] - 0.2, 'ПАСТЬ · it eats the copy of him'),
    (S('epic', 0.2), S('epic', 5.0), 'ДЕМОН comes back for the big moment'),
    (S('epic', 2 * 4 * 60 / epic['bpm']), S('epic', 2 * 4 * 60 / epic['bpm'] + 2.6), '«ВОТ ОНО.» · this is it'),
    (S('epic', 3 * 4 * 60 / epic['bpm']), seg['epic']['end'] - 0.1, 'it never really leaves'),
    (S('outro', 0.3), S('outro', 4.6), 'ГНИЛЬ · it rots off on calm songs'),
]
CREDITS_AT = S('outro', 5.2)
CREDITS = ['ДЕМОН & ПОДМЕНЫШ', 'by ШУМ (shum)', 'github.com/zumdudd/demon', 'music: ШУМ × Claude · synthesized from scratch · CC BY 4.0']

# ---- compose one 1920×1080 frame
STAGE = R.CANVAS; SX = (W - STAGE[0]) // 2 // 2 * 2; SY = 20
def caption(img, text, alpha=1.0):
    dr = ImageDraw.Draw(img, 'RGBA'); tw = dr.textlength(text, font=F_CAP); bw, bh = tw + 64, 84
    x0 = (W - bw) / 2; y0 = 900
    dr.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=18, fill=(12, 10, 28, int(200 * alpha)), outline=(59, 51, 115, int(255 * alpha)), width=3)
    dr.text((W / 2, y0 + bh / 2), text, font=F_CAP, fill=INK + (int(255 * alpha),), anchor='mm')
def chrome(img, pos):
    dr = ImageDraw.Draw(img, 'RGBA')
    dr.text((48, 40), 'ДЕМОН & ПОДМЕНЫШ', font=F_SMALL, fill=MUTE)
    sg = song.seg(pos)
    dr.text((W - 48, 40), f"{sg['n']:02d} · {sg['title']}", font=F_SMALL, fill=MUTE, anchor='ra')
    L = m['length']; y = 1046; dr.rectangle([48, y, W - 48, y + 6], fill=(35, 29, 69))
    for s_ in m['segments']:
        x = 48 + (W - 96) * s_['start'] / L; dr.rectangle([x - 1, y - 4, x + 1, y + 10], fill=(59, 51, 115))
    dr.rectangle([48, y, 48 + (W - 96) * pos / L, y + 6], fill=RED if sg['kind'] in ('slam', 'build') else VIO)
def credits(img, k):
    dr = ImageDraw.Draw(img, 'RGBA'); a = int(255 * min(1, k))
    dr.rectangle([0, 0, W, H], fill=BG + (int(222 * min(1, k)),))
    for i, line in enumerate(CREDITS):
        f_ = font(64) if i == 0 else F_CRED if i < 3 else F_SMALL
        dr.text((W / 2, 400 + i * 86 + (20 if i == 3 else 0)), line, font=f_, fill=(INK if i != 2 else RED) + (a,), anchor='mm')

# ---- render
R.reset(); R.set_song(song, at=0.0, brain=True); F.next_mimic = CLOCK.t + 1e6
n = int(min(m['length'], float(os.environ.get('SHOWCASE_LIMIT', '1e9'))) * FPS); tl = sorted(TL, key=lambda x: x[0]); ti = 0
mp4 = f'{OUT}/showcase.mp4'
ff = subprocess.Popen(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                       '-i', '-', '-i', AUDIO, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-tune', 'animation',
                       '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-shortest', mp4], stdin=subprocess.PIPE)
for i in range(n):
    CLOCK.t = round(CLOCK.t + 1 / FPS, 4); pos = d.music.position()
    d.ear.ear.snap = song.snap(pos)
    while ti < len(tl) and tl[ti][0] <= pos:
        try: tl[ti][1]()
        except Exception as e: print(f'  action at {tl[ti][0]:.2f}s failed: {e!r}')
        ti += 1
    pet = R.frame_rgb()
    img = Image.new('RGB', (W, H), BG); img.paste(pet, (SX, SY))
    chrome(img, pos)
    for a, b, text in CAPS:
        if a <= pos < b: caption(img, text, min(1.0, (pos - a) / 0.12, (b - pos) / 0.12))
    if pos >= CREDITS_AT: credits(img, (pos - CREDITS_AT) / 0.8)
    ff.stdin.write(img.tobytes())
    if i % 250 == 0: print(f'  {pos:6.1f} s / {m["length"]:.1f}', flush=True)
ff.stdin.close(); ff.wait()
subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', mp4, '-c:v', 'libvpx-vp9', '-crf', '32', '-b:v', '0', '-row-mt', '1',
                '-deadline', 'good', '-cpu-used', '4', '-c:a', 'libopus', '-b:a', '128k', f'{OUT}/showcase.webm'], check=True)
open(f'{OUT}/log.txt', 'w').write('\n'.join(R.LOGS))
print('done', mp4, os.path.getsize(mp4) // 1024, 'KB')
