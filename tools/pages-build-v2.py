#!/usr/bin/env python3
# ШУМ pages: плёнки (music) + следы (takes). Usage: pages-build-v2.py <repo>/docs
# concept + direction: ШУМ (shum) · built with Claude (Anthropic) · code GPLv3, art/text CC BY-SA 4.0
import sys, json, html, pathlib, re
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pages_data_v1 import OUAT, SALON, parse
e = lambda s: html.escape(s, quote=True)
SP = 'https://open.spotify.com/playlist/'

def wrong(word, i, letter):  # one wrong letter in every title; aria-label keeps the real word
    return f'<span aria-hidden="true">{word[:i]}<b class="w">{letter}</b>{word[i+1:]}</span>'

CSS = """
:root{--void:#0A0406;--stage:#2B1C21;--card:#170B0F;--line:#34171F;--line2:#5A2532;--red:#FF2244;--blood:#881B22;--wine:#4C0D1C;--ink:#F2DCE0;--mut:#D9B3BA;--dim:#A47782;--rust:#FF7A3D;--pink:#FF8FB1;
--disp:"Unbounded","Golos Text",system-ui,sans-serif;--sans:"Golos Text",system-ui,sans-serif;--mono:"JetBrains Mono",ui-monospace,monospace}
*{box-sizing:border-box;border-radius:0}
body{margin:0;background:var(--void);color:var(--ink);font:19px/1.55 var(--sans);overflow-x:hidden}
a{color:var(--ink);text-decoration-color:var(--red);text-underline-offset:4px}a:hover{color:var(--red)}
:focus-visible{outline:3px solid var(--red);outline-offset:3px}
::selection{background:var(--red);color:var(--void)}
.wrap{max-width:1240px;margin:0 auto;padding:0 24px}
.w{color:var(--red);font-weight:inherit}
nav{border-bottom:1px solid var(--line)}
nav .wrap{display:flex;flex-wrap:wrap;align-items:center;gap:6px 26px;min-height:62px;font:700 13px var(--mono);letter-spacing:.14em;text-transform:uppercase}
nav a{text-decoration:none;color:var(--mut);padding:10px 0}
nav .brand{font:900 17px var(--disp);color:var(--ink);margin-right:auto;letter-spacing:.02em}
nav a[aria-current]{color:var(--void);background:var(--red);padding:4px 8px}
h1{font:900 clamp(44px,15vw,196px)/.86 var(--disp);letter-spacing:-.05em;margin:56px 0 18px;text-transform:lowercase}
h2{font:900 clamp(30px,6.4vw,82px)/.98 var(--disp);letter-spacing:-.035em;margin:0;overflow-wrap:break-word}
.gl{font:400 15px var(--mono);letter-spacing:.08em;color:var(--dim);display:block}
.lede{font-size:clamp(22px,3.4vw,46px);line-height:1.28;max-width:34ch;color:var(--mut);margin:0 0 10px}
footer{margin-top:90px;border-top:1px solid var(--line);padding:34px 0 60px;color:var(--mut);font-size:15px}
footer p{margin:0 0 8px}
@media(max-width:560px){nav .brand{width:100%}nav .wrap{gap:0 18px;padding-bottom:6px}}
"""

def shell(slug, title, desc, body, css='', js=''):
    cur = lambda s: ' aria-current="page"' if s == slug else ''
    return f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://zumdudd.github.io/demon/assets/img/card-v3.jpg">
<meta property="og:url" content="https://zumdudd.github.io/demon/{slug}/">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0A0406">
<link rel="icon" type="image/png" href="../assets/img/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@500;700;900&family=Golos+Text:wght@400;600&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>{CSS}{css}</style>
</head>
<body>
<nav><div class="wrap"><a class="brand" href="../" aria-label="ДЕМОН и ПОДМЕНЫШ">ПОДМЕНЫ<span class="w">Щ</span></a>
<a href="../plenki/"{cur("plenki")}>плёнки</a><a href="../sledy/"{cur("sledy")}>следы</a><a href="https://github.com/zumdudd/demon">GitHub</a></div></nav>
<main class="wrap">
{body}
</main>
<footer><div class="wrap">
<p>ШУМ <span class="gl" style="display:inline">shum · noise</span></p>
<p>Идея, выбор и порядок: ШУМ. Страница и русский текст: Claude (Anthropic), по заметкам ШУМа.</p>
<p>Код: GNU GPL v3 · Тексты и графика страницы: CC BY-SA 4.0. Названия песен и произведений принадлежат их авторам. <a href="https://github.com/zumdudd/demon/blob/main/LEGAL.md">LEGAL</a></p>
</div></footer>
{f"<script>{js}</script>" if js else ""}
</body>
</html>
'''

# ---------------- плёнки ----------------
TAPES = [
 dict(id='ouat', name='Once Upon a Time', pid='280YRxSc0yR7Iyb5OZU6Mn', tr=parse(OUAT), span='1948 → тёмное будущее', gl='no way out',
      lore=['Он притворялся человеком.','Приговор: быть им. Жизнь за жизнью.'], end='ВЫХОДА НЕТ.',
      acts=[(1,83,None,None)], ramp=['#8A4A2A','#C4602F','#FF7A3D','#FF8FB1','#FF5C7C','#FF2244'], note=None),
 dict(id='salon', name='El Salón y Las Cenizas', pid='6iunwUFs4vP8HRviRLQBnO', tr=parse(SALON), span='1930 → 2001', gl='ballroom to ashes',
      lore=['Один и тот же. В каждом акте новое тело.','Смотрит. Терпит. Ничего не меняет.'], end='И ПОСЛЕ НИЧЕГО.',
      acts=[(1,16,'САЛОН','the ballroom'),(17,51,'ГОРОД, КОТОРЫЙ ТЕБЯ ЕСТ','the city that eats you'),(52,68,'КРОВАВЫЙ РАССВЕТ','bloody dawn'),(69,91,'ПЕПЕЛ','ashes'),(92,93,'ПРОЩАНИЕ','farewell')],
      ramp=['#F2DCE0','#D9B3BA','#FF2244','#8A5A66','#5E4A50'],
      note='<b>ОТРЕЗАНО: кольцо.</b> Первая песня не возвращается в конце. Круг значил бы, что всё начнётся снова.'),
]

def ramp(stops, f):
    x = f*(len(stops)-1); i = min(int(x), len(stops)-2); u = x-i
    a, b = (bytes.fromhex(c[1:]) for c in stops[i:i+2])
    return '#' + ''.join(f'{round(a[j]+(b[j]-a[j])*u):02X}' for j in range(3))

def tape_html(t):
    N = len(t['tr']); groups = []
    for k,(a,b,ru,en) in enumerate(t['acts']):
        cells = []
        for n in range(a,b+1):
            col = t['ramp'][k] if len(t['acts'])>1 else ramp(t['ramp'], (n-1)/(N-1))
            cells.append(f'<i data-n="{n}" style="--c:{col}"></i>')
        groups.append(f'<span class="seg" style="flex:{b-a+1} 1 0">{"".join(cells)}</span>')
    lists = []
    for k,(a,b,ru,en) in enumerate(t['acts']):
        lis = ''.join(f'<li value="{n}"><button type="button" data-n="{n}"><b>{e(t["tr"][n-1][0])}</b> <span>{e(t["tr"][n-1][1])}</span></button></li>' for n in range(a,b+1))
        head = f'<summary><span class="an">{ru}</span><span class="gl">{a}–{b}</span></summary>' if ru else f'<summary><span class="an">все {N}</span><span class="gl">1–{N}</span></summary>'
        lists.append(f'<details>{head}<ol>{lis}</ol></details>')
    data = json.dumps({'tr':t['tr']}, ensure_ascii=False).replace('<','\\u003c')
    note = f'<p class="cut">{t["note"]}</p>' if t['note'] else ''
    return f'''<section class="tape" id="{t['id']}">
<h2 lang="{'es' if t['id']=='salon' else 'en'}">{e(t['name'])}</h2>
<div class="meta"><span class="count">{N}</span><div><p class="lore"><span>{t['lore'][0]}</span><span>{t['lore'][1]}</span></p><p><span class="span">{t['span']}</span><span class="gl">{t['gl']}</span></p></div></div>
<div class="strip" role="slider" tabindex="0" aria-label="Лента: {N} песен. Стрелки листают." aria-valuemin="1" aria-valuemax="{N}" aria-valuenow="1">{''.join(groups)}</div>
<div class="read" aria-live="polite"><span class="no">01</span><p><b class="tt">{e(t['tr'][0][0])}</b><span class="ar">{e(t['tr'][0][1])}</span><span class="ac gl">{t['acts'][0][2] or ''}</span></p></div>
{note}
<p class="end">{t['end']}</p>
<a class="play" href="{SP}{t['pid']}" target="_blank" rel="noopener">▶ слушать в Spotify</a>
<div class="lists">{''.join(lists)}</div>
<script type="application/json" class="data">{data}</script>
</section>'''

SHELF = [('e v e r y w h e r e,  nowhere','3Mw6Bo9JqtQTxZ5s9BSXjH','Была везде. Не знает, где она.'),
 ('S A B B A T H','1AhZHQHMZBySxBEqI2jfyF',None),('D R E A D','27ykwcFrMmFJ6gwKpB908J',None),
 ('▓⍫⍫▓ ∰ Č H ª Ø S T H e A TE R ≼⍬⍫⍰ ∰','7rXmR53Qo9xwEfIdyKjtqH',None),('P L A Y A','0IK4d4AnlszcW7q7TXjRKt',None),
 ('a ll day','2m7flfoDpc6kT7ubGNQqNo',None),('YuNg BrAtZ','1usYMi2Z6WeTroXc5UTER8',None),('Audubon','5HGg3fs5habav2ILtpJZOi',None)]

P_CSS = """
.tape{padding:92px 0 20px;border-top:2px solid var(--line2);margin-top:70px}
.meta{display:grid;grid-template-columns:auto 1fr;gap:20px 44px;align-items:center;margin:34px 0 8px}
.lore{font-size:clamp(23px,3vw,40px);line-height:1.3;margin:0 0 18px!important;color:var(--ink)}.lore span{display:block}
@media(max-width:760px){.meta{grid-template-columns:1fr}}
.count{font:900 clamp(90px,17vw,220px)/.76 var(--disp);color:transparent;-webkit-text-stroke:2px var(--red);letter-spacing:-.06em}
.meta p{margin:0}.span{display:block;font:700 clamp(20px,3vw,36px)/1.2 var(--disp);margin-bottom:6px}
.strip{display:flex;gap:6px;height:clamp(120px,19vw,230px);cursor:crosshair;touch-action:pan-y;user-select:none;margin-top:30px}
.seg{display:flex;gap:1px;min-width:0}
.strip i{flex:1 1 0;min-width:0;background:var(--c);opacity:.78}
.strip i.same{opacity:1;box-shadow:0 -12px 0 var(--ink)}
.strip i.on{background:var(--ink);opacity:1;transform:translateY(10px);box-shadow:0 -20px 0 var(--red)}
.read{display:flex;gap:22px;align-items:flex-start;border-top:2px solid var(--ink);margin-top:20px;padding-top:16px;min-height:172px}
.read .no{font:900 clamp(40px,7vw,92px)/1 var(--disp);color:var(--red);min-width:2.1ch}
.read p{margin:0;min-width:0}.read .tt{display:block;font:700 clamp(21px,3.3vw,42px)/1.14 var(--disp);overflow-wrap:anywhere}
.read .ar{display:block;color:var(--mut);font-size:clamp(18px,2vw,26px);margin-top:6px}.read .ac{margin-top:6px}
.cut{border-left:6px solid var(--red);padding:4px 0 4px 20px;margin:20px 0;font-size:clamp(19px,2.2vw,27px);max-width:46ch;color:var(--mut)}.cut b{color:var(--ink)}
.end{font:900 clamp(26px,4.6vw,60px)/1.05 var(--disp);color:var(--red);margin:38px 0 22px;letter-spacing:-.02em}
.play{display:block;background:var(--red);color:var(--void);font:900 clamp(18px,3vw,34px)/1.2 var(--disp);text-decoration:none;padding:24px 26px;clip-path:polygon(0 0,100% 0,100% 52%,98.6% 52%,98.6% 64%,100% 64%,100% 100%,0 100%)}
.play:hover{background:var(--ink);color:var(--void)}
.lists{margin-top:10px}
details{border-bottom:1px solid var(--line2)}
summary{cursor:pointer;padding:18px 0;display:flex;gap:6px 18px;align-items:baseline;flex-wrap:wrap;list-style:none}
summary::-webkit-details-marker{display:none}summary::before{content:"+";font:700 22px var(--mono);color:var(--red)}details[open] summary::before{content:"−"}
.an{font:700 clamp(18px,2.4vw,28px) var(--disp)}
ol{margin:0 0 20px;padding:0 0 0 3.2ch;columns:2 380px;column-gap:60px}
li{break-inside:avoid;font:400 15px/1.4 var(--mono);color:var(--dim)}
li button{all:unset;cursor:pointer;display:block;padding:7px 0;font:400 17px/1.4 var(--sans);overflow-wrap:anywhere}
li button b{font-weight:600;color:var(--ink)}li button span{color:var(--dim)}li button:hover b{color:var(--red)}li button:focus-visible{outline:2px solid var(--red)}
.rest{padding-top:92px;border-top:2px solid var(--line2);margin-top:70px}
.rest ul{list-style:none;margin:34px 0 0;padding:0}
.rest li{font:inherit;border-bottom:1px solid var(--line2)}
.rest li a{display:flex;justify-content:space-between;gap:6px 24px;align-items:baseline;flex-wrap:wrap;padding:20px 0;text-decoration:none;font:700 clamp(21px,4.2vw,52px)/1.2 var(--disp)}
.rest li a:hover{background:var(--red);color:var(--void)}.rest li small{font:400 18px var(--sans);color:var(--mut)}.rest li a:hover small{color:var(--void)}
@media(max-width:600px){.strip{gap:3px}.seg{gap:0}.strip i{border-right:1px solid var(--void)}.read{min-height:200px;gap:14px}}
"""

P_JS = r"""
document.querySelectorAll('.tape').forEach(function(s){
 var D=JSON.parse(s.querySelector('.data').textContent).tr, strip=s.querySelector('.strip'), cells=[].slice.call(s.querySelectorAll('.strip i')), cur=1;
 var acts=[].slice.call(s.querySelectorAll('.lists details')).map(function(d){var b=d.querySelectorAll('button'),an=d.querySelector('.an').textContent;return [+b[0].dataset.n,+b[b.length-1].dataset.n,an]});
 function lead(a){return a.split(',')[0].trim().toLowerCase()}
 function set(n){cur=Math.max(1,Math.min(D.length,n));var t=D[cur-1],L=lead(t[1]);
  cells.forEach(function(c,i){c.className=(i+1===cur)?'on':(D[i][1].toLowerCase().split(', ').indexOf(L)>-1?'same':'')});
  s.querySelector('.no').textContent=(cur<10?'0':'')+cur;s.querySelector('.tt').textContent=t[0];s.querySelector('.ar').textContent=t[1];
  var a=acts.filter(function(x){return cur>=x[0]&&cur<=x[1]})[0];s.querySelector('.ac').textContent=acts.length>1?a[2]:'';
  strip.setAttribute('aria-valuenow',cur);strip.setAttribute('aria-valuetext',cur+'. '+t[0]+', '+t[1])}
 function at(x){var best=1,d=1e9;cells.forEach(function(c,i){var r=c.getBoundingClientRect(),k=Math.abs(x-(r.left+r.width/2));if(k<d){d=k;best=i+1}});set(best)}
 strip.addEventListener('pointerdown',function(ev){at(ev.clientX)});
 strip.addEventListener('pointermove',function(ev){if(ev.pointerType==='mouse'||ev.buttons)at(ev.clientX)});
 strip.addEventListener('keydown',function(ev){var m={ArrowLeft:-1,ArrowRight:1,PageDown:-10,PageUp:10}[ev.key];
  if(m){set(cur+m);ev.preventDefault()}else if(ev.key==='Home'){set(1);ev.preventDefault()}else if(ev.key==='End'){set(D.length);ev.preventDefault()}});
 s.querySelectorAll('.lists button').forEach(function(b){b.addEventListener('click',function(){set(+b.dataset.n);strip.scrollIntoView({block:'center'})})});
 set(1);
});
"""

def plenki():
    shelf = ''.join(f'<li><a href="{SP}{p}" target="_blank" rel="noopener"><span>{e(n)}</span>{f"<small>{l}</small>" if l else ""}</a></li>' for n,p,l in SHELF)
    body = f'''<header><h1 aria-label="плёнки">{wrong('плёнки',5,'ы')}</h1><span class="gl">tapes</span>
<p class="lede" style="margin-top:22px">Они слышат живую музыку. Вот что крутит сам ШУМ. Две плёнки с началом и концом. Проведи по ленте.</p></header>
{''.join(tape_html(t) for t in TAPES)}
<section class="rest"><h2 aria-label="остальное">{wrong('остальное',8,'ё')}</h2><span class="gl">the rest</span><ul>{shelf}</ul></section>'''
    return shell('plenki','плёнки · by ШУМ','Две плёнки с началом и концом: 83 и 93 песни. By ШУМ (shum).', body, P_CSS, P_JS)

# ---------------- следы ----------------
# source: ШУМ's own reference notes. Captions are impressions; checkable facts were searched 2026-11-26.
TAKES = [
 ('StarCraft: Brood War','игра · интро','Окоп. Для тех, кто внизу, крейсер только тень. И тень уходит.','nobody comes down','l'),
 ('Zerg','выше всего','Сверхразуму хватает глаза и голоса.','above everything','r'),
 ('Warcraft III','нежить','Старый Blizzard: пока сырой и жуткий. Отсюда берём нежить.','the undead','l'),
 ('Diablo II','акт IV · по слухам','Свет гаснет карта за картой и возвращается только после седьмой. Говорят, так задумывали. Источника нет. Идея остаётся: чувствуешь путь раньше, чем его назовут.','rumour','r'),
 ('Dune','кино · сардаукары','Горловой чант на выдуманном языке. Ни слова не понятно, и поэтому страшно. И то, как Вильнёв это ставит.','unreadable','l'),
 ('Empire Earth','та же нить','Сначала голос. Смысл потом, если вообще.','same thread','r'),
 ('Saga of Tanya the Evil','аниме · склейка','Палитра. Военный металл. Пулевая дыра вместо перехода.','a bullet hole as the cut','l'),
]
S_CSS = """
.rule{font:900 clamp(34px,7.4vw,96px)/1.04 var(--disp);letter-spacing:-.035em;margin:34px 0 8px;max-width:13ch}
.rule em{font-style:normal;color:var(--red)}
.take{border-top:2px solid var(--line2);margin-top:76px;padding-top:30px;display:grid;grid-template-columns:repeat(12,1fr);column-gap:20px}
.take>*{grid-column:1/-1}
.take .tag{font:700 14px var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--red);margin:0 0 12px}
.take h2{font-size:clamp(38px,8.6vw,118px);overflow-wrap:normal}
.take p.c{grid-column:1/10;font-size:clamp(24px,3.7vw,46px);line-height:1.3;margin:24px 0 12px;color:var(--ink)}
.take.r p.c,.take.r .gl{grid-column:4/13}
.no-list{margin-top:100px;background:var(--stage);padding:34px 28px}
.no-list h2{font-size:clamp(40px,8vw,100px)}
.no-list ul{list-style:none;padding:0;margin:24px 0 0}
.no-list li{font:700 clamp(20px,3.4vw,42px)/1.25 var(--disp);color:var(--mut);text-decoration:line-through;text-decoration-color:var(--red);text-decoration-thickness:2px;padding:10px 0}
@media(max-width:760px){.take p.c,.take.r p.c,.take.r .gl{grid-column:1/-1}.take h2{font-size:clamp(34px,11vw,70px)}}
"""
def sledy():
    arts = ''.join(f'<article class="take {s}"><p class="tag">{t}</p><h2 lang="en">{e(n)}</h2><p class="c">{c}</p><span class="gl">{g}</span></article>' for n,t,c,g,s in TAKES)
    body = f'''<header><h1 aria-label="следы">{wrong('следы',2,'я')}</h1><span class="gl">traces</span>
<p class="rule">Сырое лучше гладкого. <em>Жутко, но круто.</em></p></header>
{arts}
<section class="no-list"><h2 aria-label="мимо">{wrong('мимо',3,'а')}</h2><span class="gl">not this</span>
<ul><li>мультяшный Blizzard после <span lang="en">Warcraft III</span></li><li>гладкое фэнтези</li><li>милое ради милого</li><li>глянцевое 3D на пикселях</li></ul></section>'''
    return shell('sledy','следы · by ШУМ','Игры, кино, аниме: из чего сделан шум. By ШУМ (shum).', body, S_CSS)

# ---------------- write + patch the main page ----------------
docs = pathlib.Path(sys.argv[1])
for slug, fn in (('plenki', plenki), ('sledy', sledy)):
    (docs/slug).mkdir(exist_ok=True); (docs/slug/'index.html').write_text(fn(), encoding='utf-8')

p = docs/'index.html'; s = p.read_text(encoding='utf-8')
EDITS = [
 ('Всё лежит в открытом репо. Код MIT, арт и музыка CC BY 4.0.', 'Всё лежит в открытом репо. Код GNU GPL v3, арт и музыка CC BY-SA 4.0.'),
 ('Код: MIT · Арт: CC BY 4.0 · Музыка: ШУМ × Claude, синтез с нуля, CC BY 4.0.<br>', 'Код: GNU GPL v3 · Арт: CC BY-SA 4.0 · Музыка: ШУМ × Claude, синтез с нуля, CC BY-SA 4.0.<br>\n   <a href="https://github.com/zumdudd/demon/blob/main/LEGAL.md">LEGAL</a> · '),
 ('<a href="#get">Скачать</a><a href="https://github.com/zumdudd/demon">GitHub</a></div>', '<a href="#get">Скачать</a><a href="plenki/">Плёнки</a><a href="sledy/">Следы</a><a href="https://github.com/zumdudd/demon">GitHub</a></div>'),
 ('</main>\n\n<footer id="foot">', '<div class="wrap more"><a href="plenki/"><b>плёнки</b><i>что крутит ШУМ</i></a><a href="sledy/"><b>следы</b><i>из чего сделан шум</i></a></div>\n</main>\n\n<footer id="foot">'),
 ('@media (prefers-reduced-motion:reduce){.ticker div,.st-rec::before{animation:none}}', '@media (prefers-reduced-motion:reduce){.ticker div,.st-rec::before{animation:none}}\n/* doors to the other pages: hard edges, visible on phones too (nav links hide below 1040px) */\n.more{border-top:2px solid var(--line2)}.more a{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;gap:6px 24px;padding:30px 0;border-bottom:2px solid var(--line2);text-decoration:none}.more b{font:900 clamp(44px,10vw,130px)/1 var(--disp);letter-spacing:-.04em}.more i{font:400 15px var(--mono);font-style:normal;color:var(--mut)}.more a:hover{background:var(--red);color:var(--void)}.more a:hover i{color:var(--void)}'),
]
for old, new in EDITS:
    if new in s: continue
    assert s.count(old) == 1, ('anchor not found exactly once', old[:60])
    s = s.replace(old, new)
p.write_text(s, encoding='utf-8')
print('built plenki, sledy; patched index.html')
