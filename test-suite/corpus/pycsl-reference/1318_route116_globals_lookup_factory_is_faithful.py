r"""Test 1318 — ROUTE #116 faithful twin: a genuine globals-lookup helper
(`_g = globals()`, `def _N(name): return _g[name]`) still resolves `_N("inc")(3)` to
`(inc 3)`, and the TRUE `\result == 4` PROVES (CPython 4). Negative: 1317; a helper over a
FAKE namespace dict (`_g = {"inc": dec}`) is refused, measured in the route file.
"""
#@ ensures \result == y + 1
#@ assigns \nothing
def inc(y: int) -> int:
    return y + 1


_g = globals()


def _N(name):
    return _g[name]


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return _N("inc")(3)
