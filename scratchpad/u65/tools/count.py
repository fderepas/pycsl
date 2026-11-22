"""count.py <tree> <out.tsv> <listfile> : per-file count of per-function vacuity probes built by <tree>'s
_run_vacuity_gate (prover replaced by a recorder; no why3 run), with the probe owner names."""
import sys, os, types, subprocess, io, contextlib, re
tree, out, lst = sys.argv[1:]
sys.path.insert(0, os.path.join(tree, "src", "pycsl"))
import pycsl as P
rows = []
for mlw in open(lst).read().split():
    code = open(mlw).read(); got = []
    def fake(base_cmd, prover, tl, path, sels=None):
        txt = open(path).read()
        if "[@expl:vacprobe]" in txt:
            ln = int(sels[0].rsplit(":", 1)[1]); L = txt.split("\n"); j = ln - 1
            while j > 0 and not L[j].startswith(("  let ", "  with ")): j -= 1
            got.append(re.sub(r"\s+", " ", L[j].strip())[:50])
        return subprocess.CompletedProcess([], 0, "", "")
    P._run_why3_prove = fake
    with contextlib.redirect_stdout(io.StringIO()):
        P._run_vacuity_gate(code, ["Alt-Ergo,2.6.3,"], types.SimpleNamespace(vacuity_timelimit="5"), set())
    cls = "mir" if "/mir-int/" in mlw else ("pyref" if "/pyref/" in mlw else "root")
    rows.append(f"{cls}\t{os.path.basename(mlw)}\t{len(got)}\t{'|'.join(sorted(got))}")
open(out, "w").write("\n".join(rows) + "\n")
print("files", len(rows), "probes", sum(int(r.split('\t')[2]) for r in rows))
