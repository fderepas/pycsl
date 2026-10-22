# OPEN ROUTE #304 — A FUNCTION'S OWN EXPLICIT `raise` ESCAPES ITS `#@ no_exception` CLAIM (auto-added `raises { E }`)
**Status: OPEN (gen #37, 2026-10-22), Severity 1.** Red-team round 12; driver-reproduced on main (7/7 probes rc=0 "All contracts
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
