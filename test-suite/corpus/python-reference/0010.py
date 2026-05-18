"""Test 0010 — Python Reference 2.1.8: Indentation"""
_ = 0  # anchor
#@ ensures \result >= 0
def test_indentation(x: int) -> int:
    """Indentation determines block structure."""
    if x > 0:
        if x > 10:
            return x
        else:
            return x
    else:
        return -x

if __name__ == "__main__":
    assert test_indentation(-5) == 5
    assert test_indentation(3) == 3
