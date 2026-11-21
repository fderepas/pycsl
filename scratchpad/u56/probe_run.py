"""Run the REAL #267 call-site probe (and the per-function probe) of ONE function of a
whole-file mirror emission, exactly as the whole-file proof's vacuity gate would, through
<tree>'s pycsl `_run_vacuity_gate` with the default provers and --vacuity-timelimit 5.
Only the function list is narrowed to the one function. Every why3 call is logged.
usage: probe_run.py <tree> <mlw> <fn>"""
import sys, os, types, re
tree, mlw, fn = sys.argv[1:]
sys.path.insert(0, os.path.join(tree, "src", "pycsl"))
import pycsl as P
code = open(mlw).read()
_fbe = P._function_body_eqs
def fbe(c):
    fns, lines = _fbe(c)
    return [f for f in fns if f[0] == fn], lines
P._function_body_eqs = fbe
_run = P._run_why3_prove
def logged(base_cmd, prover, tl, path, sels=None):
    txt = open(path).read()
    kind = "callsite" if "[@expl:vacpost" in txt and "[@expl:vacprobe]" not in txt else "perfn"
    pl = txt.split("\n")
    if kind == "perfn" and (os.environ.get("U56_SKIP_PERFN") or os.path.exists("/home/fabrice/git/pycsl-u56/scratchpad/u56/SKIP_PERFN")):
        # the per-function `ensures false` probe already ran in the landed whole-file proofs;
        # skipped here to save time: this run's RESULT reflects the CALL-SITE probe only.
        print(f"[run] perfn prover={prover} SKIPPED (U56_SKIP_PERFN)", flush=True)
        import subprocess
        return subprocess.CompletedProcess([], 0, "", "")
    r = _run(base_cmd, prover, tl, path, sels)
    recs = P._json_goal_records(r.stdout)
    want = {int(s.rsplit(":", 1)[1]) for s in (sels or [])}
    lab = {}
    for i, l in enumerate(pl):
        m = re.search(r"\[@expl:(vac(?:pre|post) \d+|vacprobe)\]", l)
        if m:
            lab[i + 1] = m.group(1)
    got = {}
    for rec in recs:
        sl = ((rec.get("term") or {}).get("loc") or {}).get("start-line")
        if sl in want:
            got.setdefault(lab.get(sl, sl), []).append(P._record_answer(rec))
    print(f"[run] {kind} prover={prover} rc={r.returncode} selectors={len(sels or [])} "
          f"records={len(recs)} probe-goals={ {k: v for k, v in sorted(got.items(), key=str)} } "
          f"stderr={(' | '.join(x for x in (r.stderr or '').splitlines() if not x.startswith('Warning')))[:300]!r}",
          flush=True)
    return r
P._run_why3_prove = logged
print("fns:", fbe(code)[0], flush=True)
res = P._run_vacuity_gate(code, P._resolve_runtime_config(types.SimpleNamespace(
    memory_model=None, prover=None, provers=None))[1], types.SimpleNamespace(vacuity_timelimit="5"), set())
print("RESULT:", res, flush=True)
