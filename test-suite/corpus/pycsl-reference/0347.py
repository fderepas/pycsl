"""Test 0347 — Body-level set modelling (`set()`, `.add()`, `in`, `.discard()`).

Exercises Module6's body-set path. Sets share the dict-locals tracking
and the `map int (option int)` model: present keys map to `Some 0`,
absent keys to `None`. `s.add(x)` and `s.discard(x)` lower to
`map_update_some` / `map_update_none` program-val wrappers (because
`Map.set` is logic-only in Why3 and the result can't be assigned back
to a non-ghost ref). Returns a bool-flag result.
"""
#@ requires True
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def set_membership(x: int, y: int) -> int:
    s = set()
    s.add(x)
    if y in s:
        return 1
    else:
        return 0

if __name__ == "__main__":
    assert set_membership(3, 3) == 1
    assert set_membership(3, 4) == 0
    assert set_membership(0, 0) == 1
    print("PASS")
