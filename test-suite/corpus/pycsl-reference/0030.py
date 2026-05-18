"""Test 0030 — PyCSL Annotation Reference 3.4.1"""
_ = 0  # anchor
#@ ensures \result == a + b
#@ assigns \nothing
def test_assigns_nothing(a: int, b: int) -> int:
    """Assigns \nothing: no mutation allowed."""
    return a + b

if __name__ == "__main__":
    assert test_assigns_nothing(1, 2) == 3
