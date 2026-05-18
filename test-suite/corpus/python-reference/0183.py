"""Test 0183 — Python Reference 7.14: The type statement"""
_ = 0  # anchor
#@ ensures \result == 0
def test_type_statement() -> int:
    """type X = ... creates a type alias (3.12+)."""
    type Vector = list[int]
    assert Vector is not None
    return 0

if __name__ == "__main__":
    assert test_type_statement() == 0
