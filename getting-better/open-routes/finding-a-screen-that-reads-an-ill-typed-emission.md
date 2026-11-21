# A screen that reads an ill-typed emission, and the shape all five of this session's instrument failures share

Generation #31, 2026-09-26T15:20Z.

## The failure

`bin/screen-conversion-candidate.sh` was written this session to make the amended conversion
criterion executable: port a candidate, delete its marker, emit, and run the four oracles
(`untrusted-emitted`, `yield-erasure`, `shadowed-selfcalls`, `emitted-vacuity`) in five minutes
instead of spending up to three hours of prover time. It worked on its first candidate — it
refused `pure_ast.py::NodeVisitor.generic_visit` for a shadowed self-call, exactly as intended.

On its first BATCH it reported four green:

    _array_init_size (Module5_IREmitter)   all four oracles green
    _find_construct_idx (from_sexp)        all four oracles green
    NodeVisitor.visit (pure_ast)           all four oracles green
    _Unparser.__init__ (pure_ast)          all four oracles green

Two of those do not type-check:

    NodeVisitor.visit      L3-tc: This expression has type ref int @rho, it cannot be applied
    _Unparser.__init__     L3-tc: this write effect does not happen in the expression

**A `.mlw` that Why3 REJECTS is still WRITTEN**, so every oracle that reads the emitted file
reads it happily and reports on a program that cannot exist. The screen's own words were "This is
a LICENCE TO SPEND PROVER TIME", and the licence would have bought two 2.5-hour `pure_ast.py`
proofs of two hard refusals.

The repair is one step in front of the oracles: emit with `--no-proof`, require
`Verification SUCCESS` (L3-tc ✓), and distinguish an emitter REFUSAL from a type error in the
line it prints. Re-screened, the same batch reads:

    _array_init_size       L3-tc ok · 4 oracles green  -> LICENCE -> PROVED (52 min) -> LANDED
    _find_construct_idx    L3-tc ok · 4 oracles green  -> LICENCE -> PROVER REFUSED (3 unproven
                                                          `variant decrease` goals)
    NodeVisitor.visit      L3-tc RED
    _Unparser.__init__     L3-tc RED

which is the order the criterion is supposed to produce: cheap refusals first, prover last.

## The shape, and it is the same shape five times in one generation

| | instrument | what its scope actually was | what it reported |
|---|---|---|---|
| (p6) | a name matcher | bare names | "0 problems" for qualified input |
| (q6) | the plane battery | the FAST set | "all 48 plane(s) green" over four REDs |
| (s6) | a scratch tree | `src` only, no root `json/` | a program six declarations short |
| (t6) | a screen's reset | one FILE, not the population | 13 of 116 rows measured on a contaminated mirror |
| here | a candidate screen | the emitted `.mlw`, typed or not | a licence for two ill-typed conversions |

Every one is a WRONG SCOPE rather than a wrong step. Every one produced a CONFIDENT NUMBER — not
an error, not a crash, not a warning. And in every case the instrument was written by the same
process that then trusted it, within the same day.

**The question that catches all five is not "is this result right?" but "what exactly did this
instrument look at?"** — asked about the instrument, before the result is used. The cheapest form
of it that actually worked, four times out of five, was to run the instrument on an input whose
answer is known in advance:

  * (p6) was caught by feeding a candidate that is a trap BY CONSTRUCTION and getting "0 traps";
  * (t6) was caught because the porter ABORTED — no edit at all — and the emission still errored;
  * this one was caught by proving a candidate the screen had passed and watching L3-tc fail
    before the prover even started;
  * `check-cross-module-contract-parity.py` was NEGATIVE-TESTED before it was trusted, and the
    first injection FAILED TO FIRE, which is how its scope limit (avatars are outside its
    population) got written into its docstring instead of being discovered later.

The last of those is the only one that cost nothing, because the test came first.
