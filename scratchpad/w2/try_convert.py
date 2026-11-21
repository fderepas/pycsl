"""Try converting a list of module-level \trusted stubs one at a time: port the LIVE
body verbatim into the mirror, re-emit with --no-proof, keep it if L3-tc passes."""
import ast, os, re, subprocess, sys

REPO = sys.argv[1]
LIVE = sys.argv[2]
MIRROR = sys.argv[3]
NAMES = sys.argv[4:]

env = dict(os.environ)
env["PATH"] = "/home/fabrice/.opam/framac-coq8/bin:" + env["PATH"]
env["PYTHONHASHSEED"] = "0"

live_src = open(os.path.join(REPO, LIVE)).read()
live_lines = live_src.splitlines(True)
live_tree = ast.parse(live_src)
live_fn = {n.name: n for n in live_tree.body if isinstance(n, ast.FunctionDef)}


def live_body_text(name):
    n = live_fn[name]
    start = n.lineno - 1
    # skip decorators
    end = n.end_lineno
    return "".join(live_lines[start:end])


for nm in NAMES:
    p = os.path.join(REPO, MIRROR)
    orig = open(p).read()
    m = re.search(r"#@ \\trusted reviewer: pycsl-self-annotate\n(#@ [^\n]*\n)*def %s\(" % re.escape(nm), orig)
    if not m:
        print("SKIP  %s (no trusted stub)" % nm); continue
    # locate the stub's full def
    mt = ast.parse(orig)
    tgt = None
    for n in mt.body:
        if isinstance(n, ast.FunctionDef) and n.name == nm:
            tgt = n
    if tgt is None:
        print("SKIP  %s (not module-level)" % nm); continue
    ol = orig.splitlines(True)
    new = "".join(ol[:tgt.lineno - 1]) + live_body_text(nm) + "".join(ol[tgt.end_lineno:])
    new = new.replace("#@ \\trusted reviewer: pycsl-self-annotate\n#@ requires True\n#@ ensures True\n#@ assigns \\nothing\ndef %s(" % nm,
                      "#@ requires True\n#@ ensures True\n#@ assigns \\nothing\ndef %s(" % nm, 1)
    open(p, "w").write(new)
    r = subprocess.run([sys.executable, "src/pycsl/pycsl.py", MIRROR,
                        "--import-path", "src/pycsl", "--no-proof"],
                       cwd=REPO, capture_output=True, text=True, env=env)
    out = r.stdout + r.stderr
    if "L3-tc ✓" in out:
        print("KEEP  %s" % nm)
    else:
        err = [l for l in out.splitlines() if "line" in l and "characters" in l]
        nxt = [l for l in out.splitlines() if ("expected" in l or "unbound" in l or "type" in l) and not l.startswith("Warning")]
        print("DROP  %s   %s" % (nm, (nxt[:1] or err[-1:] or ["?"])[0][:130]))
        open(p, "w").write(orig)
