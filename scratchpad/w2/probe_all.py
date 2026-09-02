"""Cheap-win census: for every `\trusted` stub in a mirror file, port the LIVE body
verbatim (methods and module-level functions), re-emit with --no-proof, and report
whether L3-tc passes. ALWAYS restores the file. Foreground only."""
import ast, os, re, subprocess, sys

REPO = sys.argv[1]
REL = sys.argv[2]                     # e.g. frontend/ir_inline.py
LIVE = os.path.join(REPO, "src/pycsl", REL)
MIRROR_REL = "src/self-annotate/src/" + REL
MIRROR = os.path.join(REPO, MIRROR_REL)

env = dict(os.environ)
env["PATH"] = "/home/fabrice/.opam/framac-coq8/bin:" + env["PATH"]
env["PYTHONHASHSEED"] = "0"

live_src = open(LIVE).read()
live_lines = live_src.splitlines(True)


def index_defs(src):
    """(cls, name) -> ast.FunctionDef, over module functions and class methods."""
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

print("[*] %s: %d trusted stubs with a live body" % (REL, len(targets)))
for key, node, first in sorted(targets, key=lambda x: -x[2]):
    cls, nm = key
    ln = live_defs[key]
    lfirst = ln.decorator_list[0].lineno if ln.decorator_list else ln.lineno
    body_txt = "".join(live_lines[lfirst - 1: ln.end_lineno])
    # re-indent to the mirror's indentation
    mind = re.match(r"\s*", mir_lines[first - 1]).group(0)
    lind = re.match(r"\s*", live_lines[lfirst - 1]).group(0)
    if lind != mind:
        body_txt = "".join(
            (mind + l[len(lind):]) if l.startswith(lind) else l
            for l in body_txt.splitlines(True))
    cur = open(MIRROR).read().splitlines(True)
    # drop THIS stub's own `\trusted` marker line (search upward from the def)
    k = first - 2
    tline = None
    while k >= 0 and (cur[k].lstrip().startswith("#") or cur[k].lstrip().startswith("@")):
        if cur[k].lstrip().startswith("#@ \\trusted"):
            tline = k; break
        k -= 1
    head = cur[:first - 1]
    if tline is not None:
        head = cur[:tline] + cur[tline + 1:first - 1]
    new = "".join(head) + body_txt + "".join(cur[node.end_lineno:])
    open(MIRROR, "w").write(new)
    if tline is None:
        print("  BUG   %s%s (marker not removed)" % ((cls + ".") if cls else "", nm))
        open(MIRROR, "w").write(orig); continue
    r = subprocess.run([sys.executable, "src/pycsl/pycsl.py", MIRROR_REL,
                        "--import-path", "src/pycsl", "--no-proof"],
                       cwd=REPO, capture_output=True, text=True, env=env, timeout=1200)
    out = r.stdout + r.stderr
    tag = "KEEP" if "L3-tc ✓" in out else "drop"
    if tag == "KEEP":
        print("  KEEP  %s%s" % ((cls + ".") if cls else "", nm), flush=True)
    open(MIRROR, "w").write(orig)
assert open(MIRROR).read() == orig
print("[*] done %s (restored)" % REL)
