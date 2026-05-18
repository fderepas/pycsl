"""Test 0040 — Python Reference 3.2.2: NotImplemented"""
_ = 0  # anchor
#@ ensures \result == 0
def test_notimplemented_type() -> int:
    """NotImplemented is returned by binary special methods."""
    x = NotImplemented
    if x is NotImplemented:
        return 0
    return 1

if __name__ == "__main__":
    assert test_notimplemented_type() == 0
