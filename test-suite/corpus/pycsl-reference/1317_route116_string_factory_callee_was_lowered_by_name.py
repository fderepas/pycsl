r"""Test 1317 — ROUTE #116 negative: Module 5's CLASS-BY-NAME FACTORY recognizer lowered ANY
`F("name")(args)` to a direct call of the function named by the string, justified by a fact
about ONE helper (`pure_ast._N(name)` is `return _g[name]` over `_g = globals()`). A callable
class `Pick("inc")(3)` was emitted `(inc 3)` and `\result == 4` PROVED while CPython returns 2.
The recognizer now requires the outer callee to be a module-level function whose body is
exactly `return G[<param>]` with `G` bound once to `globals()`; this file's `Pick` is not.
Faithful twin: 1318.
"""
# pycsl-expected: FAIL
#@ ensures \result == y + 1
#@ assigns \nothing
def inc(y: int) -> int:
    return y + 1


class Pick:
    #@ assigns self.name
    def __init__(self, name: str) -> None:
        self.name = name

    #@ ensures \result == y - 1
    #@ assigns \nothing
    def __call__(self, y: int) -> int:
        return y - 1


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return Pick("inc")(3)
