"""Dump the call-site (#267) probe .mlw that pycsl's rewriter builds for named functions,
and run `why3 prove --type-only` on each, without any proof. Imports the TREE's pycsl.
usage: probe_dump.py <tree> <mlw> <outdir> fn1 fn2 ..."""
import sys, os, shutil, subprocess, types
tree, mlw, outdir, *names = sys.argv[1:]
sys.path.insert(0, os.path.join(tree, "src", "pycsl"))
import pycsl as P
os.makedirs(outdir, exist_ok=True)
code = open(mlw).read()
_orig_fbe = P._function_body_eqs
def fbe(c):
    fns, lines = _orig_fbe(c)
    return [f for f in fns if f[0] in names], lines
P._function_body_eqs = fbe
cur = {"n": 0}
def fake(base_cmd, prover, tl, path, sels=None):
    txt = open(path).read()
    if "[@expl:vacpost" in txt and "[@expl:vacprobe]" not in txt:
        cur["n"] += 1
        # which function? the first vacpost line's enclosing let
        dst = os.path.join(outdir, f"probe{cur['n']}.mlw")
        shutil.copy(path, dst)
        r = subprocess.run(["why3", "prove", "--type-only", path], capture_output=True, text=True)
        open(dst + ".typeonly", "w").write(f"rc={r.returncode}\nSELS={sels}\n--stderr--\n{r.stderr}\n--stdout--\n{r.stdout}")
        print(f"[dump] probe{cur['n']} prover={prover} type-only rc={r.returncode} stderr={r.stderr.strip()[:400]!r}", flush=True)
        return subprocess.CompletedProcess([], 1, "", "dumped")
    return subprocess.CompletedProcess([], 0, "", "")
P._run_why3_prove = fake
args = types.SimpleNamespace(vacuity_timelimit="5")
print("fns:", [f for f in fbe(code)[0]], flush=True)
res = P._run_vacuity_gate(code, ["Alt-Ergo,2.6.3,"], args, set())
print("result:", res)
