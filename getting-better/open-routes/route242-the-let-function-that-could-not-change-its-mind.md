# OPEN ROUTE #242 — A `let function` WHOSE BODY IS NONDETERMINISTIC IS ONE VALUE PER ARGUMENT

**Status: OPEN (gen #36, 2026-10-15), Severity 1.** Recorded as a residual by the #240/#241 repair executor
(present before and after that repair); driver-reproduced at HEAD 961346bb — all three witnesses rc=0
"Verification SUCCESS"; CPython prints 0 for each.

## Witnesses
- `let_function_bool_true_vs_one.py`: `h(x: int)` returns 1 iff `isinstance(x, bool)`; `m()` returns 1 iff
  `h(True) == h(1)` — `\result == 1` PROVES (CPython: 1 vs 0 -> m() = 0).
- `let_function_type_is_bool.py`: same with `type(x) == bool`.
- `let_function_generator_twice_equal.py`: `r()` returns a generator; `r() == r()` proves (two distinct
  generator objects compare unequal in CPython).

## Mechanism
A Python function with no writes is emitted as a Why3 `let function`. Why3 treats a `let function` as a
mathematical function of its arguments, so a fresh `(any int)` / opaque program `val` call inside its body is
fixed per argument: measured `let function r () = (any int)` proves `r () = r ()`. Combined with `True`
lowering to `1`, `h(True)` and `h(1)` are the same term.

## Repair direction
A function whose body (transitively) contains a nondeterministic construct — `any`, a call to an opaque
program `val` without a functional spec, an erased value — must not be a `let function` (emit `let`, so each
call is a fresh evaluation), or the model must distinguish `True` from `1` where it matters. Check how spec
contexts that reference such a function are handled (they need the function form): refuse those references
or provide a contract-only `val function` whose result is constrained only by the postcondition.
Also check route #237's contract-side `hval_isinst_opaque h "bool"` (True and 1 are both `HInt 1`).
