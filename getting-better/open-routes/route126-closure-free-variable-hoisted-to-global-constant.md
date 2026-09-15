# ROUTE #126 — a nested def's CLOSURE VARIABLE becomes ONE GLOBAL OPAQUE CONSTANT when the def is lifted

**Status: OPEN (found by gen #24, 2026-09-15).**
**Severity: SEV-1. First-order.**

## MEASURED at HEAD `7c9dede2`
```python
#@ assigns \nothing
def f(x: int) -> int:
    def h() -> int:
        return x
    return h()

#@ ensures \result == 0
#@ assigns \nothing
def g() -> int:
    return f(1) - f(2)
```
`[+] Verification SUCCESS`; CPython prints -1. Emission: `val constant x : int`, `let h () : int = x`,
`let function f (x: int) : int = (h ())` — the captured PARAMETER became a single global constant shared by
every call of `f`, so `f 1 = f 2`.

## REPAIR (to scope)
CENSUS: mirror nested defs with free variables in NON-trusted parents: ~20 (incl. `self` captures), pycsl_lib
json 7, python-reference 0166. A front-end refusal would refuse mirror files. The lowering site (Module 6, where
the lifted body is emitted and an unbound name becomes a `val constant`) is where the refusal belongs, with the
`\trusted`/`\abstract`/`trusted_parent` exemption of the `nonlocal_writes` precedent.
Driver: `scratchpad/g24/p1/closure_const.py`.
