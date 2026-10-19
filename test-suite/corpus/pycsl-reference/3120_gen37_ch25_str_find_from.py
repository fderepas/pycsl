r"""Test 3120 — gen #37 ch25 (expected PASS): the 2-argument `s.find(sub, start)` (the shape of
the emitter's own `audit_proof_reverify._split_rocq_print_assumptions`). At base it fell to the
opaque receiver-dropped `s_find_2 (str_hash_op sub) start` (receiver erased, `sub` int-hashed,
result unconstrained), so neither the `>= start` postcondition nor the scan loop's variant
`len(s) - pos` was provable. Now it is the faithful `str_find_from_op s sub start`: -1, or an
index at or after `start` where `sub` occurs in `s`. Twins: 3121, 3122 (must FAIL).
"""
# pycsl-expected: PASS


#@ requires 0 <= start
#@ ensures \result == -1 or (start <= \result and \result + len(sub) <= len(s))
#@ assigns \nothing
def find_from(s: str, sub: str, start: int) -> int:
    return s.find(sub, start)


#@ requires len(sub) > 0
#@ ensures \result >= 0
#@ assigns \nothing
def count_occ(s: str, sub: str) -> int:
    n = 0
    pos = 0
    #@ loop invariant 0 <= pos and 0 <= n
    #@ loop variant len(s) - pos
    while pos < len(s):
        i = s.find(sub, pos)
        if i == -1:
            break
        n += 1
        pos = i + 1
    return n


if __name__ == "__main__":
    assert find_from("abcabc", "c", 3) == 5
    assert find_from("abcabc", "c", 6) == -1
    assert count_occ("abcabc", "bc") == 2
    assert count_occ("", "x") == 0
    print("ok")
