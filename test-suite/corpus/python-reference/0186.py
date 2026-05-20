"""Test 0186 — Python Reference 8.3: The for statement"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 15
def test_for_statement() -> int:
    """for loop iterates over a sequence."""
    s = 0
    for i in range(6):
        s += i
    return s

if __name__ == "__main__":
    assert test_for_statement() == 15
