"""Test 0059 — Python Reference 3.2.9.1: Import-related attributes on module objects"""
_ = 0  # anchor
#@ ensures \result == 3
def test_user_defined_functions() -> int:
    """User-defined functions created by def statements."""
    def add(a, b):
        return a + b
    return add(1, 2)

if __name__ == "__main__":
    assert test_user_defined_functions() == 3
