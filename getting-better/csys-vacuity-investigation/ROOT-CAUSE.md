# Root-cause: vacuous "green" when de-trusting csys (colorsys)

**Status:** tool-level soundness hole confirmed and characterized. The csys
de-trust is **blocked** until the verifier is made fail-closed on vacuous
contexts. `main` is untouched (4 honest `\trusted` retained).

## Symptom

De-trusting `rgb_to_hsv` (and, intermittently, `rgb_to_hls`) and proof-engineering
the bodies produces a verification that reports **SUCCESS** — but the proof is
**vacuous**: an unconditional *false* postcondition (e.g. `#@ ensures \result[2] == 0`,
which is false because `\result[2]` is the value channel and can be 1000) **also
proves SUCCESS**. A vacuous (logically inconsistent) verification context discharges
every goal, axiom-backed or not, so the "green" means nothing.

## How it was found / measured

- The reliable vacuity probe is a **false POSTCONDITION twin** (`ensures <false>`),
  which is evaluation-position-independent. A vacuous context proves it **instantly**;
  a sound context cannot (times out or FAILs).
- The **body `#@ assert 1==2` probe is unreliable**: its result depends on where in
  the body it is placed (assert immediately before an `if` proved vacuously while the
  same assert inside either branch was sound — logically impossible for a real
  inconsistency). Do **not** use body-assert injection to judge vacuity; use a false
  postcondition.

## Bisection result (the root cause)

Reproduced in a hand-written 5-function file (`repro-vacuous-5fn.py`):
`_rgb_max`, `_rgb_min` (each `ensures result==r or result==g or result==b` +
inequalities), `_hsv_saturation` (`ensures mx>0 ==> result == (mx-mn)*1000//mx`),
`_hue_offset` (`ensures -167 <= result <= 167` over `(num*1000)//(6*diff)`), and
`rgb_to_hsv` calling them. With a false postcondition on `rgb_to_hsv` it proves
**vacuously**.

Removing **either**:
- the disjunctive `or` ensures on `_rgb_max`/`_rgb_min`, **or**
- `_hue_offset` (inlining the hue division)

makes it **non-vacuous** again. A **single** nonlinear-division-equation helper
consumed by a caller is **sound** (`repro-sound-single-div.py` correctly FAILs the
false twin). The early form of the bug (before those helpers existed) was triggered
instead by `_hls_channel` emitted as a `let function` (a module-global logic axiom
whose body contains division).

## Conclusion

The vacuity is **not**:
- a custom/unsound axiom (the module emits no axioms — just `use int.EuclideanDivision`),
- a contract-content bug in any single helper (each is individually sound),
- a `--fun`-only artifact (reproduced in the full-file gate too).

It **is** an **SMT-level instability in nonlinear integer-division reasoning**: when a
function's assumed context accumulates **several** facts that pin values to nonlinear
integer divisions (helper `result == …//…` equations, division-bound inequalities,
disjunctive value-equalities, or a `let function` logic axiom with division), the
solver (Alt-Ergo / Z3 over `int.EuclideanDivision`) derives `false` from a set that is
actually satisfiable. One such fact is fine; the combination tips it over.

This is precisely the **non-vacuity gap** flagged in `pycsl-audit-dual-tp.md`: the two
trust layers (attribution + 3-way cross-check) guarantee a cited axiom is faithful, but
**nothing checks that the consuming function's context is consistent**, so a vacuous
proof sails through as green.

## Recommended fix (fail-closed non-vacuity gate)

Add a per-function **non-vacuity gate** to the pipeline: for every verified function,
emit an auxiliary VC that its assumed context (preconditions + the assumed `ensures`
of every callee at its call sites) is **satisfiable** — operationally, that
`context -> false` is **NOT** provable. If it *is* provable, the function's "green" is
vacuous → **FAIL** (fail-closed), with a clear diagnostic. Wire it into the same gate
as the proof checks. This catches this bug and any future vacuity, independent of the
specific SMT trigger.

Mitigation (model side, secondary): avoid exposing exact nonlinear-division
*equations* in assumed contracts; prefer inequality bounds, and supply hard division
bounds via cited cross-validated lemmas rather than `result == …//…`.

## Files
- `repro-sound-single-div.py` — one div-equation helper + caller: SOUND (false twin FAILs).
- `repro-vacuous-5fn.py` — minimal 5-function reproducer: VACUOUS (false body-assert proves).
- `repro-vacuous-postcond.py` — same with a false postcondition: VACUOUS (reliable probe).

Run each with: `PYTHONHASHSEED=0 .venv/bin/python3 src/pycsl/pycsl.py <file> --fun <fn>`
