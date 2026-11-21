"""diag_any.py <mirror.py-relpath> <Class:name|name> — port the LIVE body into the mirror,
emit, and print the WhyML around the first type error, then RESTORE the mirror.
Run from a worktree root. Read-only w.r.t. everything but the one mirror file (restored)."""
import ast, os, re, subprocess, sys
ROOT = os.getcwd()
rel = sys.argv[1]
spec = sys.argv[2]
cls, _, name = spec.rpartition(':')
MIR = os.path.join(ROOT, "src/self-annotate/src", rel)
LIVE = os.path.join(ROOT, "src/pycsl", rel)
MLW = MIR[:-3] + ".mlw"
ms = open(MIR).read(); ls = open(LIVE).read()
ml = ms.split('\n'); ll = ls.split('\n')
def find(t, cls, name):
    scope = t.body
    if cls:
        c = [n for n in ast.walk(t) if isinstance(n, ast.ClassDef) and n.name == cls]
        if not c: return None
        scope = c[0].body
    f = [n for n in scope if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name]
    return f[0] if f else None
mm = find(ast.parse(ms), cls, name); lm = find(ast.parse(ls), cls, name)
assert mm is not None, "no mirror def"
assert lm is not None, "no live def"
mstart = min([d.lineno for d in mm.decorator_list] + [mm.lineno]) - 1
mend = mm.end_lineno
j = mstart - 1; tline = None
while j >= 0 and (ml[j].strip().startswith('#') or ml[j].strip().startswith('@') or ml[j].strip() == ''):
    if '\\trusted' in ml[j]: tline = j; break
    j -= 1
assert tline is not None, "no trusted marker"
ind = ml[tline][:len(ml[tline]) - len(ml[tline].lstrip())]
lstart = min([d.lineno for d in lm.decorator_list] + [lm.lineno]) - 1
body = ll[lstart:lm.end_lineno]
lind = body[0][:len(body[0]) - len(body[0].lstrip())]
ported = [(ind + l[len(lind):] if l.startswith(lind) else ind + l.lstrip()) if l.strip() else l for l in body]
new = '\n'.join(ml[:tline] + ml[tline+1:mstart] + ported + ml[mend:])
try:
    open(MIR, 'w').write(new)
    env = dict(os.environ, PATH="/home/fabrice/.opam/framac-coq8/bin:" + os.environ["PATH"], PYTHONHASHSEED="0")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "src/pycsl/pycsl.py"), MIR,
                        "--import-path", os.path.join(ROOT, "src/pycsl"), "--no-proof", "--keep-mlw"],
                       capture_output=True, text=True, cwd=ROOT, env=env, timeout=600)
    out = r.stdout + r.stderr
    m = re.search(r'File "[^"]*", line (\d+), character[s]? (\d+)(?: to line (\d+), character (\d+))?', out)
    diag = [l for l in out.split("\n") if re.search(r"but is expected|cannot be applied|unbound|syntax error|Error:|has type", l)]
    print("DIAG:", " | ".join(diag[:4]))
    if m and os.path.exists(MLW):
        a = int(m.group(1)); b = int(m.group(3) or m.group(1))
        L = open(MLW).read().split("\n")
        lo = max(0, a - 14); hi = min(len(L), b + 4)
        for i in range(lo, hi):
            mark = ">>" if a - 1 <= i <= b - 1 else "  "
            print(f"{mark}{i+1:6d}  {L[i]}")
    else:
        print(out[-2500:])
finally:
    open(MIR, 'w').write(ms)
