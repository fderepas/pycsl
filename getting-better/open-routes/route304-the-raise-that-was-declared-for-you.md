# OPEN ROUTE #304 — A FUNCTION'S OWN EXPLICIT `raise` ESCAPES ITS `#@ no_exception` CLAIM (auto-added `raises { E }`)
**Status: REPAIRED (gen #37, 2026-10-22; opened the same day), Severity 1.** Red-team round 12; driver-reproduced on main (7/7 probes rc=0 "All contracts
formally proven"; CPython raises in `__main__`).
Witnesses `witnesses-r304/`: `#@ no_exception ValueError` + `ensures \result == 0` + `if x < 0: raise ValueError("neg")` proves (f14);
`no_exception \all` + own `raise ValueError/KeyError/ZeroDivisionError` (f13_*); subclass of a tracked exception raised under a named
`no_exception` (f05, f16); method form (f18). Out-of-tracked-set raises under `\all` (f01 RuntimeError, f13_TypeError, f15 custom)
also prove — annotations.md says `\all` demands an EMPTY raised set. Arguable variant j02: `#@ raises ValueError when x < 0` with an
extra undeclared `raise E()`.
Mechanism: the emitter adds `raises { E }` to the function's own `let` for every explicit `raise` in the body, and Why3 checks the
`ensures` only on normal termination; the no_exception/raises contradiction check consults the DECLARED raises only.
Emitted (f01): `let g ... ensures { result = 0 } raises { RuntimeError } = if x < 0 then raise RuntimeError; 0`.
Blast radius: callers are protected (module callers FAIL f03/f20; method callers refused by #272 f21) — the false claim is at the raiser.
Repair direction: under `no_exception S` (S named set, with subclass closure, or `\all` = every exception), every own explicit `raise`
of an exception in S (subclass-aware; `\all` = any) must become a proof obligation `absurd`/`assert false` at the raise site (reachability
VC), or the function is refused; never an inferred `raises` clause for those classes. Consider whether an undeclared own raise
outside any declared `raises` should likewise be refused (j02).

## REPAIR (2026-10-22, r304 executor off 1d2401a5; commits 518a7819 + 511c4554 + controls/docs commits)
Probe table (`src/pycsl/pycsl.py`, full proof, rc; CPython ground truth in each file's `__main__`):

| shape | 1d2401a5 | after |
|---|---|---|
| route witnesses f01, f05, f13_{Key,Type,Value,ZeroDivision}Error, f14, f15, f16, f18 (10) | rc=0 PROVED (x10) | rc=1 FAIL (x10), each on `no_exception: own raise E reachable` only |
| j02 (`raises ValueError when x < 0` + undeclared `raise E()`, NO `no_exception`) | rc=0 | rc=0 (residual, below) |
| 3720 named `ValueError` + own `raise ValueError` (= f14) | PROVED | FAIL |
| 3721-3723 `\all` + own `ValueError` / `KeyError` / `ZeroDivisionError` (= f13) | PROVED | FAIL |
| 3724 / 3725 / 3726 `\all` + `TypeError` / `RuntimeError` / user `E(Exception)` (= f13_Type, f01, f15) | PROVED | FAIL |
| 3727 / 3728 named + user subclass `E(ValueError)` / `E(KeyError)` (= f05, f16) | PROVED | FAIL |
| 3729 named `ValueError` + two-level `B(A)`, `A(ValueError)` (= g02) | PROVED | FAIL |
| 3730 method, `\all` (= f18) | PROVED | FAIL |
| 3731 raise inside `try` whose handler is `except KeyError` (= g04) | PROVED | FAIL |
| 3732 handler of a caught `ValueError` raises `KeyError` (= g03) | PROVED | FAIL |
| 3733 CONTROLS: dead raise under `requires` (named, `\all`, method), raise caught locally (named, `\all`), out-of-set `KeyError` / user `Unrel(Exception)` under named `ValueError` with declared `raises`, declared `raises` without `no_exception`, `\all` caller of a guarded raiser | FAIL (L3-tc: the caller did not list the callee's auto-`raises { RuntimeError }`) | PASS |
| witnesses-r304 c01-c07, c09, c10 (same controls one per file, incl. c04 no claim, c06/c09 out-of-set with NO declared raises) | PASS | PASS |
| c08 user subclass caught by `except ValueError` | REFUSED (#175) | REFUSED (#175) |
| g05 `\all` caller of a guarded `\all` raiser | FAIL (L3-tc) | PASS |
| i02 IMPORTED `Sub(ValueError)` under named `ValueError` | PROVED (false) | FAIL |
| i01 IMPORTED `Unrel(Exception)` raised (reachable) under named `ValueError` | PASS | FAIL (spurious, fail-closed; residual 2) |

Rule (inline in `_emit_function_block`, functions.py; no new def, no IR change, no axiom -- ledger 3): the escaping set of
the body (`IRScanner.collect_escaping_exceptions`, handler-aware) is split against the DECLARED claim (never the #171
handler-widened context). A class is COVERED when the form is `\all`, or when it or an ancestor is listed: builtin
`exception_model.bases_closure` plus the program's class bases, which `_run_pipeline` snapshots before `_ir_resolve`
(the inheritance merge clears `td["bases"]`) and hands to the transpiler as `class_bases_r304` (the `strict_*` attribute
precedent; first cut put it on the IR root and made 5 frozen front-end goldens MISMATCH, so it was moved off the IR). A
class with unknown ancestry (not a modelled builtin and not in the snapshot, e.g. imported) is covered, fail-closed.
Covered classes are dropped from the inferred `raises` and the lowered body is wrapped
`try (<body>) with E -> (assert { [@expl:no_exception: own raise E reachable] false }; absurd) end`, so a reachable own
raise FAILS at its label and a raise dead under `requires` proves. A raise caught by a handler of the same function is
not in the escaping set and never reaches the wrapper (controls PASS; no spurious FAIL measured for locally caught raises
of builtin classes). Functions without `no_exception` and declared `raises` without `no_exception` are untouched. A
covered class that is ALSO declared `raises` is rejected by Why3 ("does not raise exception E") -- consistent with
annotations.md's conflict rule. Not a refusal: no refusal-witness census rows.
Blast radius: corpus root 0 MOVED / 0 GONE / 0 APPEARED (1999 base / 2013 candidate, 14 new sources); pyref 0/0/0
(2186/2186); mirror 0/0/0 (53/53). No mover: no M1 re-proof, NO mirror proof OWED, and NO latent false proof found in
the existing corpus (no corpus/pyref/mirror function combines `no_exception` with an escaping own raise; AST census: only
0356/0393, the Module-4 conflict tests). Mirror: `_emit_function_block` has no mirror twin; `_run_pipeline` is a
`\trusted` mirror stub; no mirrored method touched.
Gates (logs in the executor scratchpad `scratchpad/r304/`): byte-diff-sweep base/after rc=0; byte-diff-compare root rc=0,
pyref rc=0; mirror-emit-sweep base/after rc=0, compare `--min-files 50` rc=0; check-self-annotate-sync.sh rc=0 (926
verbatim); self-annotate-mirror-check.sh rc=0 (53); run-soundness-planes.sh fast rc=0, 61/61 green (the first run was
3 RED: frontend-only-conformance from the IR-key cut, fixed; corpus-contract-truth-args from three reachable-raise
controls, fixed by declaring their `raises`; check-vacuous-drivers did not reproduce standalone or on the re-run);
doc-coherency --check rc=0; check-assumed-facts rc=0.
Residuals: (1) j02 -- a declared `#@ raises E1 when C` is not exhaustive: an undeclared own `raise E2` without
`no_exception` keeps its inferred `raises { E2 }` and `ensures` is a normal-return claim, as documented (annotations.md
row 9 constrains E1 only). Making declared `raises` exhaustive is a language change, not a soundness repair under the
documented semantics; measured blast radius: 0 corpus/pyref/stdlib functions, 1 mirror method
(`Module5_IREmitter._csl_proj`, declares `raises PyCSLIRError`, raises `PyCSLSemanticError`). Left as documented.
(2) Completeness: an IMPORTED user exception class is covered fail-closed under a NAMED set even when unrelated (i01:
spurious FAIL; under `\all` it is covered anyway). (3) A user subclass caught by a base-class handler remains refused by
#175 (unchanged). (4) A bare `raise` (re-raise) has no class and is outside this rule (unchanged lowering).
