"""port_sig.py <mirror-relpath> <Class:name|:name> — SIGNATURE-PRESERVING port.

Deletes the `#@ \trusted` marker, KEEPS the mirror's `def` header (its model
annotations), and splices in the LIVE body. This is what a real conversion is, and what
`bin/probe-conversion-candidates.py` measures since the #31 repair. Run from the repo root.
"""
import ast, sys, os
ROOT = os.getcwd()
rel, spec = sys.argv[1], sys.argv[2]
cls, _, name = spec.rpartition(':')
MIR = os.path.join(ROOT, "src/self-annotate/src", rel)
LIVE = os.path.join(ROOT, "src/pycsl", rel)
ms, ls = open(MIR).read(), open(LIVE).read()
ml, ll = ms.split('\n'), ls.split('\n')

def find(src_text, cls, name):
    t = ast.parse(src_text)
    scope = t.body
    if cls:
        c = [n for n in ast.walk(t) if isinstance(n, ast.ClassDef) and n.name == cls]
        assert c, "class not found: " + cls
        scope = c[0].body
    f = [n for n in scope if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name]
    assert f, "fn not found: " + name
    return f[0]

def params(fn):
    a = fn.args
    return ([x.arg for x in a.posonlyargs] + [x.arg for x in a.args]
            + ([a.vararg.arg] if a.vararg else []) + [x.arg for x in a.kwonlyargs]
            + ([a.kwarg.arg] if a.kwarg else []))

mm, lm = find(ms, cls, name), find(ls, cls, name)
assert params(mm) == params(lm), f"PARAM LISTS DIFFER: {params(mm)} vs {params(lm)}"
mstart = min([d.lineno for d in mm.decorator_list] + [mm.lineno]) - 1
mend = mm.end_lineno
import re as _re
# The marker must be matched ANCHORED (`^#@ \trusted`), exactly as
# `bin/probe-conversion-candidates.py` does. A loose `"\\trusted" in line` test also
# matches a PROSE comment that mentions the directive — the mirror has several — and then
# deletes the wrong line while leaving the real marker in place, so the "conversion"
# silently does nothing and the stub stays trusted.
_MARK = _re.compile(r"^#@\s*\\trusted\b")
j = mstart - 1
tline = None
while j >= 0 and (ml[j].strip().startswith('#') or ml[j].strip().startswith('@') or ml[j].strip() == ''):
    if _MARK.match(ml[j].strip()):
        tline = j
        break
    j -= 1
assert tline is not None, "no \\trusted marker"
hdr = ml[mm.lineno - 1: mm.body[0].lineno - 1]
hind = hdr[0][:len(hdr[0]) - len(hdr[0].lstrip())]
lb = ll[lm.body[0].lineno - 1: lm.body[-1].end_lineno]
bind = lb[0][:len(lb[0]) - len(lb[0].lstrip())] if lb else ""
want = hind + "    "
body = [(want + l[len(bind):] if l.startswith(bind) else want + l.lstrip()) if l.strip() else l
        for l in lb]
open(MIR, 'w').write('\n'.join(ml[:tline] + ml[tline + 1:mm.lineno - 1] + hdr + body + ml[mend:]))
print("ported (signature-preserving):", rel, spec)
