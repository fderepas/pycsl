"""Test 0326 — PyCSL Annotation Reference 11.3.1"""
""  # pycsl
# Ghost-position edge case: #@ ghost as the last line in a loop body
# (no following Python statement in that scope).
#@ requires n >= 0
#@ ensures \result == n
#@ assigns \nothing
def count_with_trailing_ghost(n: int) -> int:
    i = 0
    total = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant total == i
    #@ loop variant n - i
    while i < n:
        total += 1
        i += 1
        #@ ghost last = i
    return total


if __name__ == "__main__":
    assert count_with_trailing_ghost(0) == 0
    assert count_with_trailing_ghost(5) == 5
