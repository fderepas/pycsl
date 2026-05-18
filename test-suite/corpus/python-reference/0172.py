"""Test 0172 — Python Reference 7.4: The pass statement"""
_ = 0  # anchor
#@ ensures \result == 0
def test_pass_statement() -> int:
    """pass is a no-op statement."""
    pass
    return 0

if __name__ == "__main__":
    assert test_pass_statement() == 0
