# ROUTE #121 — a user DECORATOR is silently DROPPED: calls resolve to the undecorated body

**Status: OPEN (found by gen #24, 2026-09-15) — repair drafted for gen #24 battery-A.**
**Severity: SEV-1. First-order.** Ordinary Python; no adversarial naming.

## PROVENANCE
Generator `carrier-rerun`: gen #23 logged `decorator-replacing-a-function-with-another` VACUOUS
(the replacement `dec` tripped "Symbol dec is already defined"). Gen #23's own lesson was that the
fence is a property of the VALUE chosen, so the probe was re-run with a builtin replacement.

## MEASURED at HEAD `7c9dede2`
```python
def swap(fn: Any) -> Any:
    return abs

#@ ensures \result == y + 1
#@ assigns \nothing
@swap
def inc(y: int) -> int:
    return y + 1

#@ ensures \result == -2
#@ assigns \nothing
def f() -> int:
    return inc(-3)
```
`[+] Verification SUCCESS`; CPython prints 3. Emission: `let function inc (y) ensures {result = y+1} = (y + 1)`
and `f = (inc (- 3))` — no trace of `swap`.
Sibling (VACUOUS, logged): a wrapper decorator (`@twice`) is dropped the same way but dies on the
hoisted wrapper's duplicate symbol.

## REPAIR (to scope)
Refuse any decorator whose semantics the pipeline does not model. Census the decorators the four
trees actually use FIRST and whitelist only those with a modelled meaning.
Drivers: `scratchpad/g24/p1/deco_builtin.py`, `deco_wrapper.py`.
