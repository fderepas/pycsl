# `#@ assigns \nothing` over a subprocess — 21 `\trusted` stubs

**Status: FINDING, 21 instances, measured. A gap in an existing plane's POPULATION, not in
its reasoning.**

## What the clause means

`test-suite/annotations.md` (§926) and `docs/pycsl-static-semantics-reference.md` (§2398)
both gloss it the same way:

> `#@ assigns \nothing` (pure, side-effect-free) / (no side effects)

Not "writes no modelled state" — **side-effect-free**.

## What 21 stubs declare

Censused: mirror functions carrying BOTH `#@ \trusted` and `#@ assigns \nothing`, whose LIVE
body performs an UNAMBIGUOUS external effect (`subprocess.run`/`Popen`, `os.makedirs`,
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

Every entry needs the same per-item confirmation a conversion candidate does (is that `run`
really `subprocess.run`?), which is why the list is a CANDIDATE list. `_cache_root` is
confirmed by hand: `root.mkdir(parents=True, exist_ok=True)`.

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
