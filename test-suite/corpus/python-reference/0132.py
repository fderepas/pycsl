"""Test 0132 — Python Reference 6.2.1: Built-in constants"""
_ = 0  # anchor
#@ ensures \result == 1
def test_identifiers_names() -> int:
    """An identifier is a name referring to an object."""
    x = 1
    return x

if __name__ == "__main__":
    assert test_identifiers_names() == 1
