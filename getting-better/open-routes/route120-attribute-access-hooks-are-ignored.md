# ROUTE #120 — a class's ATTRIBUTE-ACCESS HOOKS (`__getattribute__`, `__setattr__`) are ignored:
# method calls and field stores are modelled as if the hooks did not exist

**Status: FOUND, REPRODUCED (gen #23, 2026-09-15). Repair drafted, gated with #119 (battery-5).**
**Severity: SEV-1. First-order.** Both hooks are ordinary Python.

## PROVENANCE

Generator `carrier-rerun`, while running the #118/#119 rebinding family to exhaustion: after every
way of REBINDING a method was refused, the next question was whether a class can change what a
lookup RETURNS without rebinding anything. It can, and nothing looks.

## MEASURED at HEAD `c01ef653`

**`__getattribute__` redirects a method call.**

```python
class C:
    def __init__(self) -> None:
        self.a = 0
    def __getattribute__(self, name):
        if name == "m":
            name = "n"
        return object.__getattribute__(self, name)
    #@ ensures \result == 1
    def m(self) -> int: return 1
    #@ ensures \result == 2
    def n(self) -> int: return 2

#@ ensures \result == 1
def f() -> int:
    return C().m()
```
`[+] Verification SUCCESS`; CPython returns 2.

**`__setattr__` drops a field store.** A class whose `__setattr__` ignores `a = 5`;
`put(self): self.a = 5; return self.a` with `ensures \result == 5` PROVES (emitted
`self.a <- 5; self.a`); CPython returns 0.

Fenced siblings (logged): `c.__class__ = D` (a Why3 type error on the class value); a metaclass
`__new__` (UB-7.6 refusal).

## POPULATION (AST census, all four trees)

`__getattribute__` 0 · `__setattr__` 1 (python-reference 0076, expected-FAIL) · `__getattr__` 1
(0076) · descriptors `__get__/__set__/__set_name__` 1 file (python-reference 0078, expected-FAIL).

## REPAIR (drafted)

Refuse, in the shared `Module3_Weaver.process` guard, any class that defines `__getattribute__`,
`__setattr__` or `__delattr__` — the hooks that intercept a lookup or a store the model resolves
statically. (`__getattr__` fires only when normal lookup FAILS; unmodelled attribute reads are
already fresh opaque `getattr_*` values, so it is not refused.)
