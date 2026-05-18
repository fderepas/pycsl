"""Test 0038 — PyCSL Annotation Reference 4.4"""
_ = 0  # anchor
#@ ensures \result == x * x
def test_no_function_calls(x: int) -> int:
    """Function calls are NOT supported in contracts."""
    return x * x

if __name__ == "__main__":
    assert test_no_function_calls(3) == 9
