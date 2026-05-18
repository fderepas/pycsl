"""Test 0020 — PyCSL Annotation Reference 3.1.13"""
_ = 0  # anchor
#@ ensures \result == x + y
#@ assigns \nothing
def test_nothing(x: int, y: int) -> int:
    """Nothing atom: \nothing means no mutation allowed (pure function)."""
    return x + y

if __name__ == "__main__":
    assert test_nothing(3, 4) == 7
