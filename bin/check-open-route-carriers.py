#!/usr/bin/env python3
r"""L-PLANE ORACLE: the OPEN routes' carriers still behave exactly as recorded — so the day
one of them changes, somebody notices.

WHY THIS EXISTS (gen #30). A route that is CLOSED gets a corpus witness: an expected-FAIL
file that fails, and an expected-PASS control that proves. A route that is DEMONSTRATED BUT
OPEN gets neither, and the reason is worth stating because it is not laziness:

>>> AN OPEN ROUTE'S CARRIER **PROVES A FALSE CONTRACT TODAY**. Marking it
>>> `# pycsl-expected: FAIL` makes the suite red (it is an XPASS, and the XPASS rule is
>>> there precisely so a negative witness that starts proving is a failure). Marking it
>>> `PASS` writes "this false proof is expected" into the corpus. Neither is acceptable, so
>>> the carrier lives OUTSIDE the corpus — and then nothing runs it.

This gate runs it. Each entry records the verdict the route's ledger row says the carrier
produces TODAY, and a CHANGE IS THE POINT: if a carrier stops proving, the route is
probably closed and this file must be updated in the same commit that closes it. The
message says so, so a green battery cannot quietly outlive a fixed route.

THE CARRIERS (gen #30):

  route #213 — two carriers, `route213-carrier-two-reads-across-a-mutation.py` and
    `route213-carrier-three-argument-form.py`. Two reads of the SAME `getattr` are one
    per-site constant (route #197's device), so a call that writes the attribute between
    them is invisible: `x = getattr(o,"a"); mutate(o); y = getattr(o,"a"); return x - y`
    PROVES `== 0` where CPython answers -98. A refusal WAS written and then REVERTED after
    a proper blast-radius census: 212 live and 14 mirror functions read the same `getattr`
    twice with an intervening call, because `getattr(self, "_x", {})` and `getattr(args,
    …)` are ubiquitous idioms — the mirror stopped emitting and four planes went red.
    Narrowing to a non-`self` `Any`-parameter receiver still leaves 12 live and 4 mirror
    hits, including `pycsl.py::_run_pipeline` itself. The separating fact is the
    receiver's static CLASS, which only Module 6 knows, so the faithful repair is the
    state-keyed device priced in the route doc.

  route #214 — `getting-better/open-routes/route214-carrier-two-unknown-receivers.py`.
    Two `getattr` reads on DIFFERENT unknown-class objects with DIFFERENT attribute names
    share route #47's DEFAULT-KEYED constant, so `d == e` is provable and
    `#@ ensures \result == 0` PROVES. CPython answers 1. Both repairs were measured and
    are blocked — the faithful one breaks corpus 1073 (a true equality) because a local
    built from a known class is typed `Any` at that point; the refusal would hit 104 sites,
    nearly all in the mirror.

Route #212's carrier is NOT here: its single-file half (corpus 1721) genuinely FAILS, so it
is an ordinary expected-FAIL witness, and its two-file halves live in the probe ledger with
their commands.

Usage:  bin/check-open-route-carriers.py [--verbose]
"""
import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(ROOT, ".venv", "bin", "python3")
PY = PY if os.path.exists(PY) else "python3"
DRIVER = os.path.join(ROOT, "src", "pycsl", "pycsl.py")

# carrier path -> (expected verdict TODAY, route, what the verdict means)
CARRIERS = {
    # (#49) ROUTE #219 — EVERY check, VC and UB detector is switched off by the method's
    # NAME. `_should_skip_method` drops every dunder before any IR is built, so the method
    # never enters `ir_data["functions"]` and nothing that iterates that list can see it.
    # Two carriers and their one-identifier-apart controls; the controls are registered too,
    # because a carrier that "still proves" means nothing unless the control still fails.
    "getting-better/open-routes/route219-carrier-no-exception-inside-a-dunder.py": (
        "SUCCESS", "#219",
        "`#@ no_exception \\all` over `10 // 0` inside `__enter__` reports All contracts "
        "formally proven; renamed `enter`, the identical file FAILS"),
    "getting-better/open-routes/route219-control-no-exception-non-dunder.py": (
        "FAILED", "#219",
        "the control: the same body under the same contract in a NON-dunder method, which "
        "is what makes #219 a route and not a missing feature"),
    "getting-better/open-routes/route219-carrier-ub71-inside-a-dunder.py": (
        "SUCCESS", "#219",
        "UB-7.1 (mutation during iteration) is a HARD REFUSAL and it is evaded by putting "
        "the loop in `__enter__`"),
    "getting-better/open-routes/route219-control-ub71-plain-function.py": (
        "REFUSED", "#219",
        "the control: the identical loop in a plain function IS refused by the UB detector"),
    "getting-better/open-routes/route219-carrier-happy-policy-on-a-dunder.py": (
        "SUCCESS", "#219",
        "a `#@ happy ... postcond` SECURITY policy targeting a dunder is ACCEPTED by "
        "Module 3 (which walks the AST and finds the target) and then never checked, "
        "because Module 5 drops the method"),
    "getting-better/open-routes/route219-control-happy-policy-on-a-method.py": (
        "FAILED", "#219",
        "the control: the same policy on a NON-dunder target is enforced and the file fails"),
    # (#49) ROUTE #221 — `--fun` ASSUMES A FRAME NOBODY WROTE AND NOTHING CHECKS. Found by
    # the independent fable reviewer of the emit-dunders report, as a finding EXPLICITLY NOT
    # about that build (it reproduces at base, for ORDINARY methods). Three entries: the
    # carrier under `--fun`, its TRUE twin under `--fun` (which must keep failing, or the
    # flag is merely broken rather than unsound), and the SAME file whole-file (which must
    # keep failing, which is what localises the defect to the flag).
    "getting-better/open-routes/route221-carrier-fun-assumes-a-synthesized-frame.py": (
        "SUCCESS", "#221",
        "`--fun use` proves `\\result == 0` for a callee whose body sets `self.v = 7` and "
        "declares no `#@ assigns`; CPython answers -7"),
    "getting-better/open-routes/route221-control-fun-true-twin-still-fails.py": (
        "FAILED", "#221",
        "the TRUE twin under the same flag still fails — a false contract proves while the "
        "true one is rejected, which is the route standard"),
    "getting-better/open-routes/route221-control-whole-file-still-fails.py": (
        "FAILED", "#221",
        "the identical file WITHOUT `--fun` fails, which is what localises the defect to "
        "the flag rather than to the model"),
    # (#49) ROUTE #218 IS CLOSED (gen #31) — the carrier moved INTO the corpus as witness
    # 1815 (expected FAIL), with controls 1816 (read-only dunder still verifies) and 1817
    # (the non-dunder spelling, which always failed). `Module5._record_skipped_dunder_writes`
    # keeps the dropped dunder's self-writes, and the call site frames the minted `val` with
    # them, so the FALSE purity claim became an ABSENT one. The carrier file is retained as
    # the route's historical evidence and is no longer gated here: it now FAILS, and an entry
    # asserting SUCCESS would make this plane red for the right reason at the wrong time.
    "getting-better/open-routes/route213-carrier-two-reads-across-a-mutation.py": (
        "SUCCESS", "#213",
        "two reads of the same `getattr` are ONE per-site constant across a call that "
        "writes the attribute, so `\\result == 0` PROVES where CPython answers -98"),
    "getting-better/open-routes/route213-carrier-three-argument-form.py": (
        "SUCCESS", "#213",
        "the same defect through the THREE-ARGUMENT `getattr(o, \"a\", 0)` spelling"),
    "getting-better/open-routes/route214-carrier-two-unknown-receivers.py": (
        "SUCCESS", "#214",
        "two `getattr` reads on different unknown receivers share route #47's "
        "default-keyed constant, so `\\result == 0` PROVES while CPython answers 1"),
}
FLAGS = ["--memory-model", "hoare"]

# (#49) gen #31 — PER-CARRIER EXTRA FLAGS. Route #221's carrier is a false certificate
# produced by a SHIPPING FLAG (`--fun`), so the carrier is only a carrier when that flag is
# passed; run bare it merely fails, like any honest file. A gate that can only run one flag
# combination cannot hold a route whose defect lives in another one.
EXTRA_FLAGS = {
    "getting-better/open-routes/route221-carrier-fun-assumes-a-synthesized-frame.py":
        ["--fun", "use"],
    "getting-better/open-routes/route221-control-fun-true-twin-still-fails.py":
        ["--fun", "use"],
    "getting-better/open-routes/route221-control-whole-file-still-fails.py": [],
}


def verdict(path, rel=None):
    # The caller passes an ABSOLUTE path; EXTRA_FLAGS is keyed on the REPO-RELATIVE one, so
    # the lookup takes `rel` explicitly rather than guessing. A first draft keyed it on
    # `path` and the route #221 carrier silently ran WITHOUT `--fun` — reporting FAILED and
    # looking like a closed route. A flags table that can miss must not miss SILENTLY, so
    # an unknown `rel` for a path listed in EXTRA_FLAGS is impossible by construction here:
    # both dicts are keyed the same way and the guard below checks it.
    p = subprocess.run([PY, DRIVER] + FLAGS + EXTRA_FLAGS.get(rel, []) + [path],
                       capture_output=True, text=True, timeout=600)
    out = (p.stdout or "") + (p.stderr or "")
    if "PIPELINE ERROR" in out:
        return "REFUSED"
    if "Verification SUCCESS" in out:
        return "SUCCESS"
    return "FAILED"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    import shutil
    if shutil.which("why3") is None:
        print("[!] open-route-carriers: REFUSING — `why3` is not on PATH, so every carrier "
              "would report FAILED. Source the environment first.", file=sys.stderr)
        return 2

    _orphan = sorted(set(EXTRA_FLAGS) - set(CARRIERS))
    if _orphan:
        print("[!] open-route-carriers: REFUSING — EXTRA_FLAGS names %d path(s) that are "
              "not carriers: %s. A flags entry that matches nothing is a carrier running "
              "under the WRONG flags and reporting a verdict about a different question."
              % (len(_orphan), ", ".join(_orphan)), file=sys.stderr)
        return 2

    rc = 0
    for rel, (want, route, why) in sorted(CARRIERS.items()):
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            print("[!]   MISSING CARRIER %s (route %s). An open route with no carrier is "
                  "an open route nobody can reproduce." % (rel, route), file=sys.stderr)
            rc = 1
            continue
        got = verdict(path, rel)
        if args.verbose:
            print("    %-9s %s (route %s)" % (got, rel, route))
        if got != want:
            print("[+]   CARRIER CHANGED: %s (route %s) now reports %s, recorded as %s. "
                  "If the route is CLOSED, give it a corpus witness and remove this entry "
                  "IN THE SAME COMMIT — %s." % (rel, route, got, want, why),
                  file=sys.stderr)
            rc = 1

    print("[*] open-route-carriers: %d carrier(s) checked." % len(CARRIERS))
    if rc:
        print("[!] open-route-carriers: NOT OK — and a change here is usually GOOD news "
              "that needs recording, not a regression.", file=sys.stderr)
    else:
        print("[+] open-route-carriers: OK — every open route's carrier still reproduces "
              "exactly as its ledger row says.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
