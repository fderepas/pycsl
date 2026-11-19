"""Census of call-site (#267) probe bodies: for EVERY body-bearing function of every given
.mlw, build the probe the way <tree>'s pycsl rewriter does and run `why3 prove --type-only`
on it. No prover runs. usage: census.py <tree> <out.tsv> <mlw>..."""
import sys, os, subprocess, types, re, threading
tree, out, *mlws = sys.argv[1:]
sys.path.insert(0, os.path.join(tree, "src", "pycsl"))
import pycsl as P
lock = threading.Lock()
rows = []
if len(mlws) == 1 and mlws[0].endswith(".list"):
    mlws = [l.strip() for l in open(mlws[0]) if l.strip()]
for mlw in mlws:
  try:
    code = open(mlw).read()
    fns, _ = P._function_body_eqs(code)
    def fake(base_cmd, prover, tl, path, sels=None, _fns=fns, _mlw=mlw):
        txt = open(path).read()
        if "[@expl:vacprobe]" in txt or "[@expl:vacpost" not in txt:
            return subprocess.CompletedProcess([], 0, "", "")
        tl_ = txt.split("\n")
        first = min(i for i, l in enumerate(tl_) if "[@expl:vacpre" in l)
        fname = max((f for f in _fns if f[1] <= first), key=lambda f: f[1])[0]
        nsite = len(set(re.findall(r"\[@expl:vacpost (\d+)\]", txt)))
        sites = re.findall(r"let __vac_r(\d+) = (.*?) in\n check \{ \[@expl:vacpost \1\]", txt, re.S)
        sitetxt = " ## ".join(re.sub(r"\s+", " ", t)[:160] for _, t in sorted(sites, key=lambda x: int(x[0])))
        r = subprocess.run(["why3", "prove", "--type-only", path], capture_output=True, text=True)
        err = " | ".join(l for l in r.stderr.splitlines() if not l.startswith("Warning"))
        err = re.sub(r'"/tmp/\.pycsl_vac_\w+\.mlw"', "PROBE", err)
        with lock:
            rows.append((os.path.basename(_mlw), fname, nsite, r.returncode, err[:300], sitetxt))
        return subprocess.CompletedProcess([], 1, "", "census")
    P._run_why3_prove = fake
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        P._run_vacuity_gate(code, ["Alt-Ergo,2.6.3,"], types.SimpleNamespace(vacuity_timelimit="5"), set())
    nrej = sum(1 for r in rows if r[0]==os.path.basename(mlw) and r[3]!=0)
    if len(mlws) < 100 or nrej: print(f"{os.path.basename(mlw)}: {len(fns)} fns, {sum(1 for r in rows if r[0]==os.path.basename(mlw))} with sites, "
          f"{sum(1 for r in rows if r[0]==os.path.basename(mlw) and r[3]!=0)} rejected", flush=True)
  except Exception as e:
    print(f"ERROR {mlw}: {e!r}", flush=True)
with open(out, "w") as fh:
    for r in sorted(rows):
        fh.write("\t".join(map(str, r)) + "\n")
print("TOTAL with-sites", len(rows), "rejected", sum(1 for r in rows if r[3] != 0))
