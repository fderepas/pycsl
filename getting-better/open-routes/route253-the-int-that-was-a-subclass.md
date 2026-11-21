# OPEN ROUTE #253 — A BUILTIN-ANNOTATED VALUE MAY BE A SUBCLASS INSTANCE WITH OVERRIDDEN DUNDERS

**Status: RESOLVED (declared assumption BUILTIN-EXACT), gen #36, 2026-10-16** — was OPEN, Severity 1,
design-level. See "Resolution" at the end. Residual of the #252 repair (reproducer
`scratchpad/r252/res/res_intsub.py` in the executor's scratch; restated here).

## Witness
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(x: int) -> int:
        return x - x
PROVES; CPython `f(I(5))` = 7 for `class I(int): def __sub__(s, o): return 7`.

## Mechanism
The model treats a value annotated `int` / `float` / `str` / `bool` / ... as an EXACT builtin instance:
its arithmetic/comparison/equality are the builtin's. Python allows subclass instances with overridden dunders
wherever the base type is accepted (and type checkers accept them).

## Repair direction (design decision)
Fail-closed is not viable (every typed program would lose its arithmetic). Precedent: `HASH-EQ-CONSISTENCY`
(a REVIEWED ASSUMPTION surfaced by `bin/check-assumed-facts.py` with a `--strict-hash-eq-consistency` mode).
Treat "builtin-annotated values are exact builtin instances (no dunder-overriding subclass)" and route #250's
"floats are finite and non-NaN" the same way: a NAMED, SURFACED model assumption in `--soundness-report`
and the reference docs, plus (where feasible) a `--strict-*` mode that drops it.

## Resolution (gen #36, 2026-10-16) — RESOLVED as the declared model assumption BUILTIN-EXACT

**Covered.**
- `pycsl --soundness-report` lists `BUILTIN-EXACT` ("a value whose static type is a builtin —
  int/float/str/bool/bytes/tuple/list/dict/set/frozenset — is an exact instance of it, not a subclass
  overriding a dunder") whenever an operator (any IR node with an `op`: arithmetic, comparison, unary,
  augmented assignment) reads a builtin-typed variable, field or `\result`, naming function, operator and
  values. Conservative (over-, never under-reported).
- Docs: static-semantics Appendix C.1, translational §T.10.1 + §T.10.5, README, `bin/check-assumed-facts.py`
  docstring.
- Corpus 2506 (`# pycsl-model-assumption: BUILTIN-EXACT`, expected PASS): the witness PROVES under the
  model; its `__main__` shows CPython's 7.

**Not covered.** No `--strict` mode: dropping the assumption fail-closed removes all builtin arithmetic
and comparison, and an open-world "maybe a subclass" model would need per-type uninterpreted dunders for
every builtin (route #251's `pycsl_py_*` treatment, corpus-wide) — not trivially feasible. The report
does not detect builtin-typed values reached only through containers' elements beyond the direct operand
(e.g. an element of a `List[int]` used through a call), nor dunders invoked implicitly outside operator
nodes (`len`, iteration, `hash`, `str()`/`format`, truthiness in `if x:`), which rely on the same assumption. Values that
are not builtin-typed (`Any`, `object`, unannotated, TypeVar) are outside it — already uninterpreted
(routes #249/#251/#252). No ledger change (3).
