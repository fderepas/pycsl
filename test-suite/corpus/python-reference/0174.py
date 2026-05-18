"""Test 0174 — Python Reference 7.6: The return statement"""
_ = 0  # anchor
#@ ensures \result == 5
def test_return_statement() -> int:
    """return exits a function with a value."""
    return 5

if __name__ == "__main__":
    assert test_return_statement() == 5
