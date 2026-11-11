"""v35 physical split. Concept + direction: ШУМ (shum) · built with Claude.
Each big script -> ~/.local/lib/zarya/<pkg>/NN-slug.py parts run in order in ONE namespace by a stub
with the same name in ~/.local/bin. Big classes -> contiguous method groups as mixins."""
import ast, os, re, json, sys
LIM = 24000
ARCH = {'HandArt2','Hand2','HandGrab','DescendHand','Shadow','Stand'}
JOBS = [('zarya-daemon-desk','desk','Demon',3,("'d26'","'d27'")),
        ('zarya-music','music','Dance',None,("'m11'","'m12'")),
        ('zarya-hurt','hurt','Form',3,("'h9'","'h10'"))]
OUT = 'out'
def slug(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')[:40]
index = {}
for f, pkg, C, keep_hdr, (vo, vn) in JOBS:
    src = open('base/'+f, encoding='utf-8').read(); L = src.splitlines(True); t = ast.parse(src)
    first = t.body[0].lineno - 1
    # music: the first node's leading comment lines are part of its usage header up to the first code line
    header = L[:first]
    body_start = first
    parts = []          # (slug, text, names)
    cur = []; cur_len = 0; cur_names = []
    def flush():
        global cur, cur_len, cur_names
        if cur: parts.append((None, ''.join(cur), cur_names))
        cur, cur_len, cur_names = [], 0, []
    prev = body_start
    nodes = t.body
    for i, n in enumerate(nodes):
        a, b = prev, n.end_lineno
        if i == len(nodes) - 1: b = len(L)
        seg_lines = L[a:b]; seg = ''.join(seg_lines); prev = n.end_lineno
        nm = getattr(n, 'name', None)
        if isinstance(n, ast.ClassDef) and nm == C:
            flush()
            cls_line = n.lineno - 1
            assert L[cls_line].startswith(f'class {C}') and L[cls_line].rstrip().endswith(':')
            lead = ''.join(L[a:cls_line])           # comments before the class
            groups = []; g = []; gl = 0; gn = []; p = n.lineno
            for m in n.body:
                ms = ''.join(L[p:m.end_lineno]); p = m.end_lineno
                if gl + len(ms) > LIM and g: groups.append((''.join(g), gn)); g, gl, gn = [], 0, []
                g.append(ms); gl += len(ms); gn.append(getattr(m, 'name', None) or ('/'.join(x.id for t_ in getattr(m, 'targets', []) for x in ast.walk(t_) if isinstance(x, ast.Name)) or 'doc'))
            tail = ''.join(L[p:b])                  # blank lines after the class
            groups.append((''.join(g), gn))
            mix = []
            for k, (txt, gn) in enumerate(groups[1:], 1):
                mname = f'_{C}{k}'
                mix.append(mname)
                parts.append((f'{C.lower()}-{k}-{slug(gn[0])}' + ('' if gn[0] == gn[-1] else f'-{slug(gn[-1])}'), f'class {mname}:     # mixin of {C} (v35 split; one class in the original)\n' + txt + '\n', [f'{C} (mixin {mname}): ' + ', '.join(gn)]))
            line = L[cls_line]
            if '(' in line: line = line.replace(f'class {C}(', f'class {C}(' + ', '.join(mix) + ', ', 1)
            else: line = line.replace(f'class {C}:', f'class {C}(' + ', '.join(mix) + '):', 1)
            parts.append((f'{C.lower()}-0-core', lead + line + groups[0][0] + tail, [f'{C}: ' + ', '.join(groups[0][1])]))
            continue
        if cur_len + len(seg) > LIM and cur: flush()
        cur.append(seg); cur_len += len(seg)
        if nm: cur_names.append(nm + (' (archived)' if nm in ARCH else ''))
        elif isinstance(n, (ast.Assign, ast.AnnAssign)):
            tg = n.targets if isinstance(n, ast.Assign) else [n.target]
            cur_names += [x.id for t_ in tg for x in ast.walk(t_) if isinstance(x, ast.Name)][:3]
        elif isinstance(n, (ast.Import, ast.ImportFrom)): cur_names.append('imports') if 'imports' not in cur_names else None
        elif isinstance(n, ast.If) and 'main' in ast.unparse(n.test + 0 if False else n)[:80]: cur_names.append('run main')
    flush()
    # name the plain parts
    named = []
    for k, (sl, txt, names) in enumerate(parts):
        if sl is None:
            defs = [x.split(' ')[0] for x in names if x[:1].islower() or x[:1].isupper()]
            defs = [x for x in defs if x not in ('imports','run','Expr','If','Try','For','With','AugAssign')]
            sl = slug((defs[0] + ('-' + defs[-1] if len(defs) > 1 else '')) if defs else ('setup' if k == 0 else 'globals'))
        named.append((f'{k:02d}-{sl}.py', txt, names))
    os.makedirs(f'{OUT}/lib/zarya/{pkg}', exist_ok=True)
    for fn, txt, names in named:
        if vo in txt and fn.startswith(('00','01','02')): pass
        open(f'{OUT}/lib/zarya/{pkg}/{fn}', 'w', encoding='utf-8').write(txt)
    # version bump (only the VERSION assignment line)
    for fn, txt, names in named:
        p_ = f'{OUT}/lib/zarya/{pkg}/{fn}'; s_ = open(p_, encoding='utf-8').read()
        if re.search(rf"^VERSION = {re.escape(vo)}", s_, re.M):
            s_ = re.sub(rf"^VERSION = {re.escape(vo)}", f"VERSION = {vn}", s_, count=1, flags=re.M); open(p_, 'w', encoding='utf-8').write(s_)
    hdr = header if keep_hdr is None else header[:keep_hdr]
    stub = ''.join(hdr) + (
        "import os as _zos\n"
        f"# v35: the code lives in ~/.local/lib/zarya/{pkg}/ (parts run in order, one namespace, behaviour unchanged).\n"
        f"# Map of the parts: ~/.local/lib/zarya/INDEX.md · history: ~/shum/demon/CHANGELOG.md\n"
        f"_zP = _zos.path.join(_zos.path.expanduser('~'), '.local', 'lib', 'zarya', '{pkg}')\n"
        "for _zf in sorted(_n for _n in _zos.listdir(_zP) if _n.endswith('.py')):\n"
        "    with open(_zos.path.join(_zP, _zf), encoding='utf-8') as _zh:\n"
        "        exec(compile(_zh.read(), _zos.path.join(_zP, _zf), 'exec'), globals())\n")
    os.makedirs(f'{OUT}/bin', exist_ok=True)
    open(f'{OUT}/bin/{f}', 'w', encoding='utf-8').write(stub); os.chmod(f'{OUT}/bin/{f}', 0o755)
    index[pkg] = [(fn, len(txt), names) for fn, txt, names in named]
# INDEX.md
out = ['# ДЕМОН code index (v35)\n', '\nConcept + direction: ШУМ (shum) · built with Claude. Each folder = one script; its parts run in order in one namespace (`~/.local/bin/zarya-<name>` is the launcher). Read this, then only the part you need.\n']
for pkg, items in index.items():
    out.append(f'\n## {pkg}/  (`zarya-{"daemon-desk" if pkg=="desk" else pkg}`)\n\n| Part | Size | Holds |\n|---|---|---|\n')
    for fn, sz, names in items:
        out.append(f'| `{fn}` | {sz//1024} KB | ' + '; '.join(names).replace('|','/') + ' |\n')
open(f'{OUT}/lib/zarya/INDEX.md', 'w', encoding='utf-8').write(''.join(out))
print(json.dumps({k: [(a, b) for a, b, _ in v] for k, v in index.items()}, indent=0))
