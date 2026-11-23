"""names.py <tree> <mlw>... : print the per-function probe names this tree's _run_vacuity_gate builds (no prover)."""
import sys, os, types, subprocess, io, contextlib
tree, *mlws = sys.argv[1:]
sys.path.insert(0, os.path.join(tree, "src", "pycsl"))
import pycsl as P
for mlw in mlws:
    code = open(mlw).read(); got = []
    def fake(base_cmd, prover, tl, path, sels=None):
        txt = open(path).read()
        if "[@expl:vacprobe]" in txt:
            ln = int(sels[0].rsplit(":", 1)[1]); L = txt.split("\n")
            j = ln - 1
            while j > 0 and not L[j].startswith(("  let ", "  with ")): j -= 1
            got.append((ln, L[j].strip()[:60]))
        return subprocess.CompletedProcess([], 0, "", "")
    P._run_why3_prove = fake
    with contextlib.redirect_stdout(io.StringIO()):
        P._run_vacuity_gate(code, ["Alt-Ergo,2.6.3,"], types.SimpleNamespace(vacuity_timelimit="5"), set())
    print(os.path.basename(mlw), len(got))
    for g in sorted(got): print("   ", g)
