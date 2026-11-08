r"""Test 1786 — WITNESS: a write through `nonlocal`, which has no IR statement.

The nested `def` is lifted to a SIBLING function, so a `nonlocal` write would land on a
fresh local and be SILENTLY INVISIBLE to the enclosing function while the run still
reported "All contracts formally proven". Refused. One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no witness.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result >= 0
def outer(n: int) -> int:
    acc = 0

    #@ assigns \nothing
    #@ ensures \result == 0
    def bump() -> int:
        nonlocal acc
        acc = acc + 1
        return 0

    return acc
