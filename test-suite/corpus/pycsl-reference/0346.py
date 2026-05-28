"""Test 0346 — Body-level dict membership (`in` / `not in`).

Exercises Module6's body-dict `in` / `not in` emission:
`k in d` → `Map.get !d k <> None`. The function inserts a known key
and checks both an inserted key (must be present) and an
absent key (must be absent). Returns a 2-bit result for both probes.
"""
#@ requires True
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def dict_membership(k: int) -> int:
    d = {}
    d[k] = 1
    other = k + 1
    if k in d:
        if other not in d:
            return 1
        else:
            return 0
    else:
        return 0

if __name__ == "__main__":
    assert dict_membership(5) == 1
    assert dict_membership(0) == 1
    assert dict_membership(-3) == 1
    print("PASS")
