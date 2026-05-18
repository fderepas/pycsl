"""Test 0017 — Python Reference 2.3.4: Non-ASCII characters in names"""
_ = 0  # anchor
#@ ensures \result == x
def test_non_ascii_names(x: int) -> int:
    """Identifiers can contain non-ASCII letters."""
    résultat = x
    return résultat

if __name__ == "__main__":
    assert test_non_ascii_names(5) == 5
