"""Test 0181 — Python Reference 7.12: The global statement"""
_ = 0  # anchor
#@ ensures \result == 10
def test_global_statement() -> int:
    """global declares a variable as global."""
    global _test_g
    _test_g = 10
    return _test_g

if __name__ == "__main__":
    assert test_global_statement() == 10
