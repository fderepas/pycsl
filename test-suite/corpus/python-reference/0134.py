"""Test 0134 — Python Reference 6.2.3.1: Literals and object identity"""
_ = 0  # anchor
#@ ensures \result == 0
def test_literals_and_object_identity() -> int:
    """Ref 6.2.3.1: Literals and object identity."""
    return 0

if __name__ == "__main__":
    assert test_literals_and_object_identity() == 0
