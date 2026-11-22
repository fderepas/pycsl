"""Census of PER-FUNCTION vacuity probes (`ensures { [@expl:vacprobe] false }`): run <tree>'s
real _run_vacuity_gate on each .mlw with _run_why3_prove replaced by a recorder (no prover
runs), then `why3 prove --type-only` the recorded probes: all at once, then each suspect
alone (bisection by error line). usage: pfcensus.py <tree> <out.tsv> <mlw>..."""
import sys, os, subprocess, types, re, threading, tempfile, io, contextlib
tree, out, *mlws = sys.argv[1:]
sys.path.insert(0, os.path.join(tree, "src", "pycsl"))
import pycsl as P
lock = threading.Lock()
def tc(lines):
    fd, p = tempfile.mkstemp(suffix=".mlw", prefix=".u62_")
    with os.fdopen(fd, "w") as f: f.write("\n".join(lines) + "\n")
    r = subprocess.run(["why3", "prove", "--type-only", p], capture_output=True, text=True)
    os.remove(p)
    err = " | ".join(l for l in r.stderr.splitlines() if not l.startswith("Warning"))
    m = re.search(r'line (\d+)', err)
    return r.returncode, (int(m.group(1)) if m else None), re.sub(r'"/tmp/\.u62_\w+\.mlw"', "F", err)[:300]
rows = []; tot_p = tot_r = 0
for mlw in mlws:
    code = open(mlw).read()
    rec = {"lines": None, "idx": []}
    def fake(base_cmd, prover, tl, path, sels=None):
        txt = open(path).read()
        if "[@expl:vacprobe]" in txt:
            ln = int(sels[0].rsplit(":", 1)[1])
            tl_ = txt.split("\n")[:-1]
            with lock:
                if rec["lines"] is None: rec["lines"] = tl_[:ln-1] + tl_[ln:]
                rec["idx"].append(ln - 1)
        return subprocess.CompletedProcess([], 0, "", "")
    P._run_why3_prove = fake
    with contextlib.redirect_stdout(io.StringIO()):
        P._run_vacuity_gate(code, ["Alt-Ergo,2.6.3,"], types.SimpleNamespace(vacuity_timelimit="5"), set())
    L = rec["lines"] or []; idxs = sorted(set(rec["idx"]))
    def fname(i):
        j = i
        while j > 0 and not re.match(r"^  let ", L[j]): j -= 1
        return re.sub(r"\s+", " ", L[j].strip())[:70]
    def build(sel):
        o = []; s = set(sel)
        for i, l in enumerate(L):
            if i in s: o.append("    ensures { [@expl:vacprobe] false }")
            o.append(l)
        return o
    base_rc = tc(L)[0] if L else 0
    live = list(idxs); rej = []
    while live:
        rc, eln, err = tc(build(live))
        if rc == 0: break
        # positions of inserted lines in the batch file (1-based)
        pos = {i: i + 1 + k for k, i in enumerate(live)}
        cand = [i for i in live if eln is not None and pos[i] <= eln]
        sus = max(cand, key=lambda i: pos[i]) if cand else None
        if sus is not None and tc(build([sus]))[0] != 0:
            rej.append((sus, tc(build([sus]))[2])); live.remove(sus); continue
        # fallback: check each alone
        bad = [(i, e) for i in live for (r_, _, e) in [tc(build([i]))] if r_ != 0]
        rej += bad
        for i, _ in bad: live.remove(i)
        if not bad: rej.append((-1, "BATCH-ONLY FAILURE: " + err)); break
    tot_p += len(idxs); tot_r += len(rej)
    print(f"{os.path.basename(mlw)}: base-tc rc {base_rc}, {len(idxs)} probes, {len(rej)} rejected", flush=True)
    for i, e in rej:
        rows.append((os.path.basename(mlw), i + 1, fname(i) if i >= 0 else "-", e))
with open(out, "w") as fh:
    for r in rows: fh.write("\t".join(map(str, r)) + "\n")
print("TOTAL probes", tot_p, "rejected", tot_r)
