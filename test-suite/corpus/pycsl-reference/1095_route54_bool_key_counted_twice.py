"""Test 1095 — ROUTE #54 negative witness (a): `True` AND `1` WERE TWO DICT KEYS.

FALSE OF THE PROGRAM: `True` hashes and compares equal to `1`, so Python's dict has ONE
entry and `len(d)` is 1.

A dict literal had TWO models and they disagreed. The emitted map is FAITHFUL —
`map_update_some (map_update_some empty 1 10) 1 20`, source order, so a repeated key's LAST
value wins exactly as in Python — and the constant fold that answers `len(d)` never consulted
it: it counted the literal's SYNTACTIC entries and compared keys by their source form. At the
parent commit 967c68e1 `\\result == 2` PROVED.

Same shape as route #48 mirrored. There a SEEDED collection dropped its seed; here the seed
is kept in the map and dropped by the READER. The rule that catches both: a fold over a
literal is sound only where the fold's key equality IS the model's key equality.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    d = {1: 10, True: 20}
    return len(d)


if __name__ == "__main__":
    assert f() == 1
