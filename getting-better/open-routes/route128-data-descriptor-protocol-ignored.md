# ROUTE #128 — the DESCRIPTOR protocol (`__get__`/`__set__`) is ignored: an attribute bound to a descriptor
# instance is modelled as a plain field

**Status: OPEN — repair drafted for gen #24 battery-A.**
**Severity: SEV-1. First-order.** Sibling of #120 (attribute-access hooks) on the ATTRIBUTE's class.

## MEASURED at HEAD `0a3d1d2e`
```python
class Seven:
    def __get__(self, obj, tp=None) -> int: return 7
    def __set__(self, obj, val: int) -> None: pass

class C:
    x = Seven()
    def __init__(self) -> None:
        self.x = 42

#@ ensures \result == 42
def f() -> int:
    c = C(); return c.x
```
PROVES (`type c = { mutable x: int }`, `{ x = 42 }`, `c.x`); CPython 7.
Found while reading pyref 0078 (a descriptor test, expected-FAIL) when scoping #127.

## REPAIR (drafted)
The #120 hook refusal in Module3_Weaver.process also refuses a class defining `__get__`, `__set__`,
`__delete__` or `__set_name__` (by def or by class-body assignment). Census: pyref 0078 only. Witness 1353.
Sibling fenced: `x = property(_get)` (a Why3 error on `c.x`).
