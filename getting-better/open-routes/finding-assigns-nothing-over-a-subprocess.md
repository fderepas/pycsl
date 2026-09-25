# `#@ assigns \nothing` over a subprocess — 17 confirmed `\trusted` stubs

**Status: FINDING, 17 receiver-confirmed instances (plus two more confirmed by hand), measured. A gap in an existing plane's POPULATION, not in
its reasoning.**

## What the clause means

`test-suite/annotations.md` (§926) and `docs/pycsl-static-semantics-reference.md` (§2398)
both gloss it the same way:

> `#@ assigns \nothing` (pure, side-effect-free) / (no side effects)

Not "writes no modelled state" — **side-effect-free**.

## What 21 stubs declare

First census (LOOSE — kept because the tightening below is the instructive part): mirror
functions carrying BOTH `#@ \trusted` and `#@ assigns \nothing`, whose LIVE body performs
what looked like an external effect (`subprocess.run`/`Popen`, `os.makedirs`,
`Path.mkdir`, `os.remove`). Ambiguous names were excluded on purpose — `str.replace` is pure
and dominates `Path.replace`, and a `.write` may be a local buffer's — so this is a floor,
not a ceiling:

    audit_proof_reverify.py   _cache_root  mkdir      _cache_store      mkdir
                              _coqc_version run       _lean_version     run
                              verify_lean_file run    verify_rocq_file  run
    proof2why3/extract.py     extract_lean_statements run
                              extract_rocq_statements run
    proof2why3/extract_lean_meta.py  extract_lean_statements_meta run
    proof2why3/sertop.py      extract_via_sertop run  run_sertop_batch  Popen
                              sertop_version run
    frontend/Module1_Ingestor.py     process run
    pycsl.py                  _check_rocq_proofs run  _generate_rocq_obligations makedirs
                              _probe_one remove       _run_pipeline     run
                              _run_proofs remove      _run_vacuity_gate remove
                              _run_why3_prove run     _why3_typecheck   run

**TIGHTENED, because the first list was a candidate list and I said so in the same breath
as printing it.** Re-censused requiring a CONFIRMED RECEIVER (`subprocess.`/`os.`), which
removes the guessing:

    11x  subprocess.run    audit_proof_reverify.py  _coqc_version, _lean_version,
                                                    verify_lean_file, verify_rocq_file
                           proof2why3/extract.py    extract_lean_statements,
                                                    extract_rocq_statements
                           proof2why3/extract_lean_meta.py  extract_lean_statements_meta
                           proof2why3/sertop.py     extract_via_sertop, sertop_version
                           pycsl.py                 _check_rocq_proofs, _run_why3_prove,
                                                    _why3_typecheck
     1x  subprocess.Popen  proof2why3/sertop.py     run_sertop_batch
     1x  os.makedirs       pycsl.py                 _generate_rocq_obligations
     3x  os.remove         pycsl.py                 _probe_one, _run_proofs,
                                                    _run_vacuity_gate
    ----
    17 CONFIRMED BY RECEIVER, plus `audit_proof_reverify.py::_cache_root`
       (`root.mkdir(parents=True, exist_ok=True)` — a Path variable, so the strict filter
       cannot see it) and `_cache_store` beside it, confirmed by hand.

**And the two FALSE POSITIVES the loose filter produced, named because they are the reason
the tightening happened:** `frontend/Module1_Ingestor.py::process` calls
`_Harvester(coms).run(tree)` — a local method named `run`, nothing to do with
`subprocess` — and `Module6_WhyMLTranspiler::_sig_val_from_let` / `pycsl.py::_run_pipeline`
matched `replace()`, which is `str.replace` and pure. One hand check on the first entry I
looked at found one of them.

## Why the existing plane does not see them

`bin/check-trusted-frame-honesty.py` was built for exactly this shape and says so in its own
header — *"a stub that declares `#@ assigns \nothing` while the LIVE method it stands for
really does mutate `self` state states something FALSE"*. Its analysis computes each
function's direct `self.<attr> = ...` stores and propagates along the call graph.

**`self.<attr>` is the whole population.** A module-level function that shells out to
`why3 prove` mutates no attribute, so the plane is silent — correctly, by its own
definition, and incompletely by the clause's.

## Why it matters NOW rather than as a curiosity

While the marker is there the false clause is ASSUMED, and `\trusted` is the flag that says
so. **The moment one of these is converted, the clause becomes CERTIFIED.** That is not
hypothetical: `audit_proof_reverify.py::_cache_root` converts cleanly and its whole file
PROVES in 28 seconds — the conversion emits `val root_mkdir_0 () : int`, nullary, no
`writes`, so the model sees no effect and discharges `assigns \nothing` over a `mkdir`.

It was caught by the four-check discipline in
`finding-two-trusted-stubs-that-convert-and-prove.md`, on the FIRST check, in four minutes —
and if the check had not been run, a green whole-file proof would have retired a marker and
certified a falsehood in the same commit.

So this list is also a DO-NOT-CONVERT list until the clause is repaired, and that is its
most immediate use.

## The two repairs, neither of them attempted here

1. **Extend the plane.** Add external-effect calls to
   `check-trusted-frame-honesty`'s notion of "mutates", with a named allowlist for the
   stubs whose clause is then corrected. Cheap, and it makes the 21 visible on every gate.
2. **Correct the clauses.** `#@ assigns \nothing` on a function that shells out is simply
   wrong under the documented reading; what it should say is a separate design question
   (PyCSL has no external-effect frame vocabulary — `docs/formal-filesystem.md` models a
   filesystem for VERIFIED programs, not for the emitter's own subprocess calls).

Repair 1 is an instrument change with a measured population. Repair 2 is a vocabulary
question. Recorded with both, attempted with neither.

## Bounded: NOT load-bearing today — zero converted callers

The obvious next question, and the one that decides whether this is a live unsoundness or a
trap waiting: **does anything already RELY on one of these false `assigns \nothing`
clauses?** Censused — every UN-trusted (i.e. verified) mirror function, checked for a call
to any of the nineteen:

    UNTRUSTED mirror functions calling one of them:  **0**

So no proof in the mirror currently leans on a frame that is false of the program. The
clauses are assumed, flagged by their markers, and unconsumed.

That makes this a TRAP rather than a HOLE, and it is worth saying plainly because the two
deserve different urgency. A hole gets fixed now; a trap gets a sign on it, which is what the
DO-NOT-CONVERT list above is. The sign matters because the trap is exactly one green
whole-file proof away from being a hole — and a green whole-file proof is precisely what a
conversion session is looking for.
