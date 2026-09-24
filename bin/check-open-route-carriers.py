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
    # (#49) ROUTE #219 IS CLOSED (gen #31) — dunders are now EMITTED, so every check that
    # iterates `ir_data["functions"]` sees them. The six carriers moved INTO the corpus as
    # witnesses 1828-1832 (plus 1827, the Liskov override that is now CERTIFIED rather than
    # merely un-lied-about), each with its one-identifier-apart control. The carrier files
    # are retained in this directory as the route's historical evidence and are no longer
    # gated here: they now FAIL or are REFUSED, and entries asserting SUCCESS would make
    # this plane red for the right reason at the wrong time.
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
    # (#49) ROUTE #224 IS CLOSED (gen #31, the same day it was found) — the carrier moved
    # INTO the corpus as witness 1855 (expected FAIL, NO `# pycsl-flags`), with control 1856
    # (a REFINING conformance still verifies by default). A `#@ conforms_to` pair is now
    # tagged `from_conforms_to` in the `overrides` IR list and Module 6 emits the refinement
    # goal for THOSE pairs whether or not `--check-behavioral-subtyping` is passed — route
    # #224's own priced repair 2, "the goal follows the DIRECTIVE". The implicit inheritance
    # overrides keep their opt-in behaviour, which is what control 1856 pins. Both carrier
    # files are retained as the route's historical evidence and are no longer gated here:
    # the carrier now FAILS, and an entry asserting SUCCESS would make this plane red for
    # the right reason at the wrong time — the same disposition route #218's entry took.
    # (#49) ROUTE #218 IS CLOSED (gen #31) — the carrier moved INTO the corpus as witness
    # 1815 (expected FAIL), with controls 1816 (read-only dunder still verifies) and 1817
    # (the non-dunder spelling, which always failed). `Module5._record_skipped_dunder_writes`
    # keeps the dropped dunder's self-writes, and the call site frames the minted `val` with
    # them, so the FALSE purity claim became an ABSENT one. The carrier file is retained as
    # the route's historical evidence and is no longer gated here: it now FAILS, and an entry
    # asserting SUCCESS would make this plane red for the right reason at the wrong time.
    # (#49) ROUTE #213 IS CLOSED (gen #31) — BOTH carriers moved INTO the corpus, as
    # witnesses 1859 (no-default) and 1860 (the three-argument spelling), with control 1727
    # (two reads with NO intervening call still agree) already there. The per-site device
    # is now APPLIED TO `!_pyobj_state`, which is the repair the route's own record priced
    # as "the faithful fix": #197's equality is kept exactly where #197 justified it and
    # lost exactly across a write. Inside a pure `let function` or a contract term the
    # device stays a CONSTANT — a mutable ref cannot be dereferenced there, and a pure
    # function has no effects, so no write can occur between two reads inside it. The
    # carrier files are retained as the route's historical evidence and are no longer
    # gated here: both now FAIL, and an entry asserting SUCCESS would make this plane red
    # for the right reason at the wrong time (the disposition routes #218 and #224 took).
    "getting-better/open-routes/route214-carrier-two-unknown-receivers.py": (
        "SUCCESS", "#214",
        "two `getattr` reads on different unknown receivers share route #47's "
        "default-keyed constant, so `\\result == 0` PROVES while CPython answers 1"),
    # (#49) gen #31 — ROUTE #226. `__init__` sets `self.n = 0`, the invariant says
    # `self.n >= 5`, and a method returning `self.n` proves `\result >= 5`. The emitted
    # record is `invariant { n >= 5 } by { n = 10 }` — the inhabitation witness is
    # SYNTHESIZED FROM THE INVARIANT — and `__init__` is not emitted at all, so nothing
    # checks that the real constructor establishes it; every method then gets the invariant
    # free, because a Why3 type invariant holds at every boundary for a value of that type.
    # annotations.md says the invariant "must hold at every method boundary", and the
    # constructor's exit is one.
    # (#49) gen #31 — THE LITERAL-CONSTRUCTOR CARRIER IS CLOSED. Increment 1 emits
    # `goal _check_class_inv_<C>` over `__init__`'s literals for a paramless constructor,
    # so `route226-carrier-constructor-never-establishes-the-invariant.py` no longer
    # verifies. It stays on disk as the closed carrier; the route is NOT closed, because
    # three shapes still carry it, and the live one is registered below.
    # (#49) gen #31 — THE PARAMETER CARRIER IS CLOSED TOO. Increment 2 quantifies over the
    # parameter and makes `__init__`'s binding a premise, carrying its `#@ requires` along,
    # so both that shape and `@dataclass` now fail. Two of route #226's four carriers were
    # closed by increment 1, a third and fourth by increment 2; the COMPUTED store is what
    # is left, and it is left because the honest obligation there needs the CALLEE'S
    # postcondition rather than a literal.
    "getting-better/open-routes/route226-carrier-computed-constructor-store.py": (
        "SUCCESS", "#226",
        "a `#@ class invariant` over a field the constructor COMPUTES (`self.n = three()`) "
        "is marked unknown and gets no obligation, so `\\result >= 5` still PROVES while "
        "CPython answers 3"),
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
