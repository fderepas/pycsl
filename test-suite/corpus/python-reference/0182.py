"""Test 0182 — Python Reference 7.13: The nonlocal statement"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 5
def test_nonlocal_statement() -> int:
    """nonlocal binds to enclosing scope variable."""
    x = 0
    def inner():
        nonlocal x
        x = 5
    inner()
    return x

if __name__ == "__main__":
    assert test_nonlocal_statement() == 5
