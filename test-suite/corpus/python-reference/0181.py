"""Test 0181 — Python Reference 7.12: The global statement"""
# pycsl-expected: FAIL
# (#49) route #129: a write through `global` lowered to a FRESH local while reads of the module
# variable are one opaque constant (a read before and after a write was proved equal). A `global`
# write to a name that is not `#@ shared` is REFUSED now, so this coverage test is expected-FAIL.
_ = 0  # anchor
#@ ensures \result == 10
def test_global_statement() -> int:
    """global declares a variable as global."""
    global _test_g
    _test_g = 10
    return _test_g

if __name__ == "__main__":
    assert test_global_statement() == 10
