"""Test 0173 — Python Reference 7.5: The del statement"""
_ = 0  # anchor
#@ ensures \result == 0
def test_del_statement() -> int:
    """del unbinds a name."""
    x = 42
    del x
    return 0

if __name__ == "__main__":
    assert test_del_statement() == 0
