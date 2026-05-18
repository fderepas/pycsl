"""Test 0205 — Python Reference 8.7: Function definitions"""
_ = 0  # anchor
#@ ensures \result == 5
def test_function_definitions() -> int:
    """def creates a function."""
    def double(x):
        return x * 2
    return double(2) + 1

if __name__ == "__main__":
    assert test_function_definitions() == 5
