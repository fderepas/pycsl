"""Runtime gate OR5 — `is None` is a runtime identity test.

Spec clause OR5 (optional-twoplane-spec.md §2.3): `x is None` is the
runtime identity test against the singleton `None`. It returns `True`
iff `x` IS the `None` singleton. The runtime test narrows the VALUE
(sometimes); the static narrowing narrows the TYPE (always, on the
path) — they are DIFFERENT things (OD2 no-blend).

This driver confirms the runtime test runs as a value comparison: on
the True branch `x` is provably `None`; on the False branch `x` is NOT
`None`. The postcondition `ensures \\result == 0 \\/ \\result == 1`
discharges because the runtime `is None` test partitions the value
space — the static plane does not need to know the type of `val` for
this postcondition to hold, only that `is None` is a boolean-valued
comparison.

Expected (from spec): prove (the runtime `is None` test partitions the
value space into None / not-None, and the postcondition discharges on
both branches).
"""

#@ ensures \result == 0 or \result == 1
def f(val) -> int:
    if val is None:
        return 0
    return 1


if __name__ == "__main__":
    assert f(None) == 0
    assert f(1) == 1
    assert f("a") == 1
    print("PASS")
