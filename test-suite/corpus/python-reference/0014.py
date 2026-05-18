"""Test 0014 — Python Reference 2.3.1: Keywords"""
_ = 0  # anchor
#@ ensures \result >= 0
def test_keywords(x: int) -> int:
    """Keywords are reserved identifiers: if, else, return, def, etc."""
    if x >= 0:
        return x
    else:
        return -x

if __name__ == "__main__":
    assert test_keywords(-4) == 4
