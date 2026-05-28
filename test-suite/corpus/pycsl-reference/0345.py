"""Test 0345 — Body-level dict modelling (round-trip read after write).

Exercises Module6's body-dict path: `d = {}` lowers to
`let d = ref (const (None: option int)) in`, `d[k] = v` lowers to
`d := map_update_some !d k v` (a program-level wrapper around
`Map.set`), and `d[k]` reads through
`match Map.get !d k with Some v_ -> v_ | None -> 0 end`. The function
writes a single key and then returns the value at that same key —
the simplest round-trip the new modelling needs to support. The
`map_update_some` wrapper's ensures clause is enough for Why3 +
Alt-Ergo to discharge `\\result == v`.
"""
#@ requires True
#@ ensures \result == v
#@ assigns \nothing
def dict_roundtrip(k: int, v: int) -> int:
    d = {}
    d[k] = v
    return d[k]

if __name__ == "__main__":
    assert dict_roundtrip(1, 42) == 42
    assert dict_roundtrip(0, -7) == -7
    assert dict_roundtrip(99, 0) == 0
    print("PASS")
