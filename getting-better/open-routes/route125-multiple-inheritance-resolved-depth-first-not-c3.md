# ROUTE #125 — a method call on a class with MULTIPLE bases is resolved DEPTH-FIRST, not by C3 MRO

**Status: CLOSED AND FULLY GATED by gen #24 (2026-09-15), battery-A (cheap legs, emission vs HEAD, suite 3481/3499 same 18 0 XPASS, planes 34/34 — every leg predicted and hit).**
**Severity: SEV-1. First-order.**

## MEASURED at HEAD `7c9dede2`
```python
class A:    (__init__) ; m -> 1
class B(A): (__init__ only)
class C(A): (__init__) ; m -> 3
class D(B, C): (__init__ only)
#@ ensures \result == 1
def f() -> int:
    d = D(); return d.m()
```
PROVES; CPython 3 (MRO D, B, C, A). Emission `d__m` = A's body, `val d_m_0 ensures result = 1`.
Control (logged FAIL-CLOSED): the same diamond with `pass` bodies (no `__init__`) resolves to C —
the depth-first walk needs B to be a record class. Mechanism is a hypothesis until the resolver is read.
`super()` in a diamond is fenced (opaque `super_0`).

## REPAIR (to scope)
Compute the C3 linearization where method resolution walks bases (or refuse when C3 and the walk
disagree). Locate every resolver first (Module5 + module6 method tables).
Drivers: `scratchpad/g24/p1/mro_diamond.py`, `mro_diamond_nodef.py`, `super_diamond.py`.
