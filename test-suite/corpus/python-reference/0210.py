"""Test 0210 — Python Reference 8.10.1: Generic functions"""
_ = 0  # anchor
#@ ensures \result == 0
def test_generic_functions() -> int:
    """Generic functions with type parameters (PEP 695)."""
    def identity[T](x: T) -> T:
        return x
    assert identity(42) == 42
    return 0

if __name__ == "__main__":
    assert test_generic_functions() == 0
