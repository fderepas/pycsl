"""Test 1034 — ROUTE #39 positive control: a file with NO context-manager class
is untouched by the whitelist, and its `with` still carries the body.

The route-#39 whitelist is armed only when the unified AST defines a class with
`__enter__`/`__exit__`/`__aenter__`/`__aexit__`. Every `with <lock>:` critical
section in this corpus (33 of them, files 0252-0280 and 0417) lives in a file that
defines no such class, so all of them keep working exactly as before — and so does
the 52-site `with self.block()` / `with self.delimit()` population in the
self-annotation mirror, which is reached through the W1 generator fixpoint
instead.

This TRUE contract must keep proving. If it ever starts failing, the whitelist has
been armed somewhere it should not be.
"""
_ = 0  # anchor
class Plain:
    def __init__(self) -> None:
        self.n: int = 0


#@ ensures \result == 9
#@ assigns \nothing
def f() -> int:
    p = Plain()
    p.n = 9
    return p.n
