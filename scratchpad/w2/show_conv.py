"""Convert ONE trusted stub (port the live body) and print its emitted WhyML body.
Always restores the mirror."""
import ast, os, re, subprocess, sys
REPO, REL, CLS, NAME = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
KEEP = len(sys.argv) > 5 and sys.argv[5] == "keep"
LIVE = os.path.join(REPO, "src/pycsl", REL)
MIRROR_REL = "src/self-annotate/src/" + REL
MIRROR = os.path.join(REPO, MIRROR_REL)
env = dict(os.environ); env["PATH"] = "/home/fabrice/.opam/framac-coq8/bin:" + env["PATH"]
env["PYTHONHASHSEED"] = "0"
def index_defs(src):
    out = {}
    t = ast.parse(src)
    for n in t.body:
        if isinstance(n, ast.FunctionDef):
            out[("", n.name)] = n
        elif isinstance(n, ast.ClassDef):
            for m in n.body:
                if isinstance(m, ast.FunctionDef):
                    out[(n.name, m.name)] = m
    return out
live_src = open(LIVE).read(); live_lines = live_src.splitlines(True)
ld = index_defs(live_src)
orig = open(MIRROR).read(); ml = orig.splitlines(True); md = index_defs(orig)
key = (CLS, NAME)
node = md[key]; ln = ld[key]
first = node.decorator_list[0].lineno if node.decorator_list else node.lineno
lfirst = ln.decorator_list[0].lineno if ln.decorator_list else ln.lineno
body = "".join(live_lines[lfirst - 1: ln.end_lineno])
mind = re.match(r"\s*", ml[first - 1]).group(0)
lind = re.match(r"\s*", live_lines[lfirst - 1]).group(0)
if lind != mind:
    body = "".join((mind + l[len(lind):]) if l.startswith(lind) else l
                   for l in body.splitlines(True))
k = first - 2; tline = None
while k >= 0 and (ml[k].lstrip().startswith("#") or ml[k].lstrip().startswith("@")):
    if ml[k].lstrip().startswith("#@ \\trusted"):
        tline = k; break
    k -= 1
head = ml[:tline] + ml[tline + 1:first - 1] if tline is not None else ml[:first - 1]
open(MIRROR, "w").write("".join(head) + body + "".join(ml[node.end_lineno:]))
r = subprocess.run([sys.executable, "src/pycsl/pycsl.py", MIRROR_REL,
                    "--import-path", "src/pycsl", "--no-proof", "--keep-mlw"],
                   cwd=REPO, capture_output=True, text=True, env=env, timeout=2400)
mlw = os.path.join(REPO, MIRROR_REL[:-3] + ".mlw")
if os.path.exists(mlw):
    txt = open(mlw).read().splitlines()
    pat = re.compile(r"^  (let rec|let|with|val) \S*%s\b" % re.escape(
        (CLS.lower() + "__" if CLS else "") + NAME))
    for i, l in enumerate(txt):
        if pat.match(l) or (NAME in l and l.startswith("  let ")):
            print("\n".join(txt[i:i + 26])); break
    os.remove(mlw)
else:
    print("NO MLW"); print((r.stdout + r.stderr)[-600:])
if not KEEP:
    open(MIRROR, "w").write(orig)
