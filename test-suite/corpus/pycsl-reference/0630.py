"""Test 0630 — `\in_globals` decides TRUE for a declared module binding (07-1839 P1/P2).

Introspection answered at verification time: `\in_globals(name)` is a sound lower bound over the
statically-declared module bindings (functions, module globals, constants, classes). A declared
module function `helper` is in `globals()`, so `\in_globals(helper)` lowers to `true` and proves.
"""
# pycsl-flags: --memory-model hoare


#@ assigns \nothing
def helper(x: int) -> int:
    return x


#@ ensures \in_globals(helper)
#@ assigns \nothing
def f() -> int:
    return 0
