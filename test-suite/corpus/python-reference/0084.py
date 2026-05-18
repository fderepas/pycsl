"""Test 0084 — Python Reference 3.3.3.5: Executing the class body"""
_ = 0  # anchor
#@ ensures \result == 0
def test_executing_the_class_body() -> int:
    """Ref 3.3.3.5: Executing the class body."""
    return 0

if __name__ == "__main__":
    assert test_executing_the_class_body() == 0
