"""Test 0185 — Python Reference 8.2: The while statement"""
_ = 0  # anchor
#@ ensures \result == 10
def test_while_statement() -> int:
    """while loop."""
    s = 0
    i = 0
    #@ loop invariant 2 * s == i * (i - 1)
    #@ loop invariant 0 <= i
    #@ loop invariant i <= 5
    #@ loop variant 5 - i
    while i < 5:
        s += i
        i += 1
    return s

if __name__ == "__main__":
    assert test_while_statement() == 10
