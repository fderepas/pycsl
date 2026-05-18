"""Test 0001 — Python Reference 1.1: Alternate Implementations"""
_ = 0  # anchor
#@ ensures \result >= 0
def test_alternate_implementations(x: int) -> int:
    """CPython is the reference implementation; this test validates integer semantics."""
    if x >= 0:
        return x
    return -x

if __name__ == "__main__":
    assert test_alternate_implementations(5) == 5
    assert test_alternate_implementations(-3) == 3
