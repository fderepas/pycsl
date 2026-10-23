"""Port ONE trusted stub's live body into the mirror IN PLACE (no restore).
Optionally insert extra `#@` lines. Usage: port_one.py <repo> <rel.py> <CLS|""> <NAME> [extra-directive ...]"""
import ast, os, re, sys
REPO, REL, CLS, NAME = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
EXTRA = sys.argv[5:]
LIVE = os.path.join(REPO, "src/pycsl", REL)
MIRROR = os.path.join(REPO, "src/self-annotate/src", REL)
def index_defs(src):
    out = {}
    t = ast.parse(src)
    for n in t.body:
        if isinstance(n, ast.FunctionDef): out[("", n.name)] = n
        elif isinstance(n, ast.ClassDef):
            for m in n.body:
                if isinstance(m, ast.FunctionDef): out[(n.name, m.name)] = m
    return out
live_src = open(LIVE).read(); ll = live_src.splitlines(True); ld = index_defs(live_src)
mir = open(MIRROR).read(); ml = mir.splitlines(True); md = index_defs(mir)
key = (CLS, NAME)
node = md[key]; ln = ld[key]
first = node.decorator_list[0].lineno if node.decorator_list else node.lineno
lfirst = ln.decorator_list[0].lineno if ln.decorator_list else ln.lineno
body = "".join(ll[lfirst - 1: ln.end_lineno])
mind = re.match(r"\s*", ml[first - 1]).group(0)
lind = re.match(r"\s*", ll[lfirst - 1]).group(0)
if lind != mind:
    body = "".join((mind + l[len(lind):]) if l.startswith(lind) else l for l in body.splitlines(True))
k = first - 2; tline = None
while k >= 0 and (ml[k].lstrip().startswith("#") or ml[k].lstrip().startswith("@")):
    if ml[k].lstrip().startswith("#@ \\trusted"): tline = k; break
    k -= 1
assert tline is not None, "no trusted marker"
head = ml[:tline] + [mind + e + "\n" for e in EXTRA] + ml[tline + 1:first - 1]
open(MIRROR, "w").write("".join(head) + body + "".join(ml[node.end_lineno:]))
print("ported %s.%s into %s (+%d directives)" % (CLS, NAME, REL, len(EXTRA)))
