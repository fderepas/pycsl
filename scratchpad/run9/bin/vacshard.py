"""vacshard.py <tree> <k> <N> <pycsl args...>
Run <tree>'s REAL pycsl pipeline on the file (same flags as a whole-file proof); at _run_proofs, instead of
the main proof phase, run <tree>'s REAL _run_vacuity_gate on the SAME mlw_code / provers / args, with the
SAME exempt set (args._vacuity_exempt) PLUS every probed function whose index i (in the gate's own fns
order, obtained by a recorder pass) has i % N != k. So shard k of N probes exactly the functions
{fns[i] : i % N == k}; the union of shards 0..N-1 is the whole gate (per-function probes are independent
why3 runs, each probe file carrying ONE probe). Every why3 call is logged; the shard verdict is the gate's
own return value. k = -1: list the functions only. The main proof phase is NOT run here: it comes from a
separate real run of the same file under the same tree (--no-check-vacuity or a full run's results)."""
import sys, os, types, re, hashlib, subprocess, io, contextlib
tree, k, N, *pargs = sys.argv[1:]; k = int(k); N = int(N)
sys.path.insert(0, os.path.join(tree, "src", "pycsl"))
import pycsl as P
orig_gate = P._run_vacuity_gate; orig_prove = P._run_why3_prove
def order(mlw_code, provers, args):
    seen = set()
    def fake(base_cmd, prover, tl, path, sels=None):
        txt = open(path).read()
        if "[@expl:vacprobe]" in txt:
            ln = int(sels[0].rsplit(":", 1)[1]); pl = txt.split("\n")
            j = ln - 2
            while j > 0 and not re.match(r"^  let ", pl[j]): j -= 1
            m = P._LET_FN_RE.match(pl[j]); seen.add((ln, m.group(1) if m else "?"))
        return subprocess.CompletedProcess([], 0, "", "")
    P._run_why3_prove = fake
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            orig_gate(mlw_code, provers, types.SimpleNamespace(vacuity_timelimit=getattr(args, "vacuity_timelimit", "5")), set())
    finally:
        P._run_why3_prove = orig_prove
    return [n for _, n in sorted(seen)]   # file order, one entry per probed function (deduped over provers)
def logged(base_cmd, prover, tl, path, sels=None):
    txt = open(path).read(); kind = "perfn" if "[@expl:vacprobe]" in txt else "callsite"
    r = orig_prove(base_cmd, prover, tl, path, sels)
    recs = P._json_goal_records(r.stdout)
    print(f"[vs-run] {kind} prover={prover} rc={r.returncode} sels={len(sels or [])} records={len(recs)} "
          f"answers={sorted(set(P._record_answer(x) for x in recs))}", flush=True)
    return r
def fake_proofs(mlw_code, mlw_filename, provers, args):
    h = hashlib.sha256(mlw_code.encode()).hexdigest()
    ex = set(getattr(args, "_vacuity_exempt", set()) or set())
    names = order(mlw_code, provers, args)
    print(f"[vs] mlw sha256 {h} lines {mlw_code.count(chr(10))} provers {provers} check_vacuity {getattr(args,'check_vacuity',None)} "
          f"timelimit {getattr(args,'vacuity_timelimit',None)} exempt {sorted(ex)} probes {len(names)} cpu {os.cpu_count()}", flush=True)
    if k < 0:
        for i, n in enumerate(names): print(f"[vs-fn] {i} {n}")
        return
    mine = {names[i] for i in range(len(names)) if i % N == k}
    skip = ex | (set(names) - mine)
    print(f"[vs] shard {k}/{N}: probing {sorted(mine)}", flush=True)
    P._run_why3_prove = logged
    vac = orig_gate(mlw_code, provers, args, skip)
    print(f"[vs] SHARD-RESULT {k}/{N} {'NONE(why3 absent)' if vac is None else ('CLEAN' if not vac else 'NOT-CLEAN')} {vac}", flush=True)
P._run_proofs = fake_proofs
sys.argv = ["pycsl.py"] + pargs
P.main()
