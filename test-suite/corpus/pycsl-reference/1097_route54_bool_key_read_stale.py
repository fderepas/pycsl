"""Test 1097 — ROUTE #54 negative witness (b): THE FOLD ANSWERED THE OVERWRITTEN VALUE.

FALSE OF THE PROGRAM: `{1: 10, True: 20}[1]` is 20 in Python — the second entry writes the
same key and wins.

The element fold kept a map from literal key to literal value and SKIPPED the `True: 20`
entry entirely (its key is a `Bool` node, not a `Number`), so it answered the first entry's
value while the emitted WhyML map already held the second. At 967c68e1 `\\result == 10`
PROVED. 1098 is its faithful twin.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ ensures \result == 10
#@ assigns \nothing
def f() -> int:
    d = {1: 10, True: 20}
    return d[1]


if __name__ == "__main__":
    assert f() == 20
