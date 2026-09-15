# ROUTE #123 — a subclass's CLASS-BODY BINDING (`m = lambda self: 2`, `m = staticmethod(abs)`) that
# overrides an INHERITED method is ignored: calls resolve to the base's def

**Status: OPEN (found by gen #24, 2026-09-15).**
**Severity: SEV-1. Order 2** (carrier = #118/#119 rule (1): the class-body pass flags a Name store
only against the defs of the SAME class body, so a name inherited from a base walks past it).

## MEASURED at HEAD `7c9dede2`
1. `class A: m -> 1`; `class B(A): m = lambda self: 2` (+`__init__`); `B().m()` with `\result == 1`
   PROVES; CPython 2. Emission `b__m` = A's body, `val b_m_0 ensures result = 1`.
2. `class A: m(y) -> y + 1`; `class B(A): m = staticmethod(abs)`; `B().m(-3)` with `\result == -2`
   PROVES; CPython 3.

## REPAIR (to scope)
Rule (1) must key the class-body scope on the METHODS OF THE CLASS AND ITS ANCESTORS (in-module), and
treat a foreign base as having unknown methods (rule (8)'s convention) — census class-body bindings
in subclasses of foreign bases before choosing how far that goes.
Drivers: `scratchpad/g24/p1/cls_attr_lambda.py`, `cls_attr_builtin.py`.
