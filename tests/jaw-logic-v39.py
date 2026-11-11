import os, time
H = os.path.expanduser('~'); P = f'{H}/.local/lib/zarya/desk'
g = {'__name__': 'x', '__file__': f'{H}/.local/bin/zarya-daemon-desk'}
for f in sorted(x for x in os.listdir(P) if x.endswith('.py')): exec(compile(open(f'{P}/{f}').read(), f, 'exec'), g)
d = g['Demon'](); F = d.form; F.start(time.time(), 45, 'test'); F.song_key = 'song-a'
class R:  # dice: always the jaw
    def random(self): return 0.1
    def uniform(self, a, b): return a
F.rng = R(); t = time.time()
F.mimic = t - 0.01; assert F.mimic_tick(t, True) and F.jaw_t == t, 'jaw should start'
assert F.mimic_on(t + 1.0); F.mimic_tick(t + 1.9, True); assert F.mimic is None and F.jaw_t is None, 'jaw should end into ПОДМЕНЫШ'
F.mimic = t + 2.0; F.mimic_tick(t + 2.1, True); assert F.mimic is None, 'second act same song: no jaw'
F.song_key = 'song-b'; F.mimic = t + 3; F.mimic_tick(t + 3.1, False); assert F.mimic is None, 'no music: no jaw'
F.mimic = t + 4; assert F.mimic_tick(t + 4.1, True) and F.jaw_t, 'new song: jaw again'
F.arc = {'ph': 'smell'}; F.mimic_tick(t + 4.5, True); assert F.mimic is None and F.jaw_t is None, 'hype arc cuts the jaw'
print('JAW LOGIC OK')
