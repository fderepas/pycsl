"""Test 0107 — Python Reference 4.2.5: Builtins and restricted execution"""
_ = 0  # anchor
#@ ensures \result == 0
def test_builtins_and_restricted_execution() -> int:
    """Ref 4.2.5: Builtins and restricted execution."""
    return 0

if __name__ == "__main__":
    assert test_builtins_and_restricted_execution() == 0
