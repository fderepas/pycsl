"""Cheap-win census v2: port the LIVE body of every `\trusted` stub, emit with
--keep-mlw, and score the EMITTED BODY for erasure. Foreground only; always restores.
Usage: probe_all2.py <repo> <rel.py> [outdir]
"""
import ast, os, re, subprocess, sys, json

REPO = sys.argv[1]
REL = sys.argv[2]
OUT = sys.argv[3] if len(sys.argv) > 3 else None
LIVE = os.path.join(REPO, "src/pycsl", REL)
MIRROR_REL = "src/self-annotate/src/" + REL
MIRROR = os.path.join(REPO, MIRROR_REL)
MLW = os.path.join(REPO, MIRROR_REL[:-3] + ".mlw")

env = dict(os.environ)
env["PATH"] = "/home/fabrice/.opam/framac-coq8/bin:" + env["PATH"]
env["PYTHONHASHSEED"] = "0"

def index_defs(src):
    out = {}
    t = ast.parse(src)
    for n in t.body:
        if isinstance(n, ast.FunctionDef):
            out[(None, n.name)] = n
        elif isinstance(n, ast.ClassDef):
            for m in n.body:
                if isinstance(m, ast.FunctionDef):
                    out[(n.name, m.name)] = m
    return out

try:
    live_src = open(LIVE).read()
except OSError:
    print("[*] %s: no live file" % REL); sys.exit(0)
live_lines = live_src.splitlines(True)
live_defs = index_defs(live_src)
orig = open(MIRROR).read()
mir_lines = orig.splitlines(True)
mir_defs = index_defs(orig)

targets = []
for key, node in mir_defs.items():
    first = node.decorator_list[0].lineno if node.decorator_list else node.lineno
    i = first - 2
    blk = []
    while i >= 0 and (mir_lines[i].lstrip().startswith("#")
                      or mir_lines[i].lstrip().startswith("@")):
        blk.append(mir_lines[i]); i -= 1
    if any(b.lstrip().startswith("#@ \\trusted") for b in blk) and key in live_defs:
        targets.append((key, node, first))

ERASE = [
    ("hash",    re.compile(r"str_hash_op")),
    ("getattr", re.compile(r"\bgetattr_\w*")),
    ("setattr", re.compile(r"\bsetattr_\w*")),
    # FALSE NEGATIVE FIXED (relaunch #19): the old pattern required the oracle's name to end
    # in `_<digits>`, so `(str_dunder_op ())` -- the WHOLE emitted body of `PyCSLError.message`
    # -- scored 0 and the stub read as a cheap win. Any ARGUMENT-LESS application is an oracle
    # that cannot depend on the receiver or the arguments, whatever its name.
    ("nilop",   re.compile(r"\b[a-z]\w*\s*\(\)")),
    ("truelit", re.compile(r"if\s+(true|false)\s+then")),
    ("fresharr",re.compile(r"Array\.make\s+\d+")),
]

def extract_body(mlw_txt, name):
    lines = mlw_txt.splitlines()
    ln = name.lower()
    pat = re.compile(r"^(\s*)let\s+(rec\s+)?([A-Za-z0-9_']+)")
    best = None
    for i, l in enumerate(lines):
        m = pat.match(l)
        if not m: continue
        ident = m.group(3)
        if ident.lower().endswith(ln.lstrip("_")) or ident.lower().endswith(ln):
            best = (i, len(m.group(1)))
    if best is None: return None
    i, ind = best
    j = i + 1
    stop = re.compile(r"^\s{0,%d}(let|val|predicate|function|type|exception|clone|end)\b" % ind)
    while j < len(lines):
        if stop.match(lines[j]) and len(lines[j]) - len(lines[j].lstrip()) <= ind:
            break
        j += 1
    return "\n".join(lines[i:j])

results = []
print("[*] %s: %d trusted stubs with a live body" % (REL, len(targets)), flush=True)
for key, node, first in sorted(targets, key=lambda x: -x[2]):
    cls, nm = key
    ln = live_defs[key]
    lfirst = ln.decorator_list[0].lineno if ln.decorator_list else ln.lineno
    body_txt = "".join(live_lines[lfirst - 1: ln.end_lineno])
    mind = re.match(r"\s*", mir_lines[first - 1]).group(0)
    lind = re.match(r"\s*", live_lines[lfirst - 1]).group(0)
    if lind != mind:
        body_txt = "".join((mind + l[len(lind):]) if l.startswith(lind) else l
                           for l in body_txt.splitlines(True))
    cur = open(MIRROR).read().splitlines(True)
    k = first - 2; tline = None
    while k >= 0 and (cur[k].lstrip().startswith("#") or cur[k].lstrip().startswith("@")):
        if cur[k].lstrip().startswith("#@ \\trusted"):
            tline = k; break
        k -= 1
    if tline is None:
        open(MIRROR, "w").write(orig); continue
    head = cur[:tline] + cur[tline + 1:first - 1]
    new = "".join(head) + body_txt + "".join(cur[node.end_lineno:])
    open(MIRROR, "w").write(new)
    if os.path.exists(MLW): os.remove(MLW)
    try:
        r = subprocess.run([sys.executable, "src/pycsl/pycsl.py", MIRROR_REL,
                            "--import-path", "src/pycsl", "--no-proof", "--keep-mlw"],
                           cwd=REPO, capture_output=True, text=True, env=env, timeout=1800)
        out = r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        out = "TIMEOUT"
    ok = "L3-tc ✓" in out
    rec = {"file": REL, "cls": cls, "name": nm, "tc": ok}
    if ok and os.path.exists(MLW):
        mlw = open(MLW).read()
        body = extract_body(mlw, nm)
        if body is None:
            rec["score"] = None; rec["why"] = "no-let-found"
        else:
            counts = {}
            for tag, rx in ERASE:
                c = len(rx.findall(body))
                if c: counts[tag] = c
            sig = body.splitlines()[0]
            nint = len(re.findall(r":\s*int\b", sig))
            if nint: counts["int_param"] = nint
            rec["score"] = sum(counts.values()); rec["marks"] = counts; rec["sig"] = sig.strip()
            rec["blen"] = len(body.splitlines())
        print("  KEEP  %-50s score=%s %s" % (((cls + ".") if cls else "") + nm,
              rec.get("score"), rec.get("marks", "")), flush=True)
    results.append(rec)
    if os.path.exists(MLW): os.remove(MLW)
    open(MIRROR, "w").write(orig)
assert open(MIRROR).read() == orig
if OUT:
    key = REL.replace("/", "_")
    json.dump(results, open(os.path.join(OUT, key + ".json"), "w"))
print("[*] done %s (restored)" % REL, flush=True)
