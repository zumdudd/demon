"""Static parity: rebuild each original module from its parts (merge mixins back into the class) and compare ASTs."""
import ast, os, sys, re
JOBS = [('zarya-daemon-desk','desk','Demon',("'d26'","'d27'")),('zarya-music','music','Dance',("'m11'","'m12'")),('zarya-hurt','hurt','Form',("'h9'","'h10'"))]
ok = True
for f, pkg, C, (vo, vn) in JOBS:
    P = f'out/lib/zarya/{pkg}'
    src = ''.join(open(f'{P}/{x}', encoding='utf-8').read() for x in sorted(os.listdir(P)) if x.endswith('.py'))
    src = re.sub(rf"^VERSION = {re.escape(vn)}", f"VERSION = {vo}", src, count=1, flags=re.M)
    new = ast.parse(src); orig = ast.parse(open(f'base/{f}', encoding='utf-8').read())
    mix = {n.name: n for n in new.body if isinstance(n, ast.ClassDef) and re.fullmatch(rf'_{C}\d+', n.name)}
    body = []
    for n in new.body:
        if n.name in mix if isinstance(n, ast.ClassDef) else False: continue
        if isinstance(n, ast.ClassDef) and n.name == C:
            names = [ast.unparse(b) for b in n.bases]
            assert names[:len(mix)] == list(mix), names
            n.bases = n.bases[len(mix):]
            for m in mix.values(): n.body += m.body
        body.append(n)
    new.body = body
    same = ast.dump(new) == ast.dump(orig)
    # stub keeps what the help printer reads
    stub = open(f'out/bin/{f}', encoding='utf-8').read()
    print(f'{f}: parts={len([x for x in os.listdir(P) if x.endswith(".py")])} AST identical to v34.1 (version line aside): {same}; stub {len(stub)} B')
    ok &= same
    for x in sorted(os.listdir(P)):
        if x.endswith('.py'): compile(open(f'{P}/{x}').read(), x, 'exec')
print('ALL PARITY OK' if ok else 'PARITY FAILED'); sys.exit(0 if ok else 1)
