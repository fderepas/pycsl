"""Test 0109 — Python Reference 4.3: Exceptions"""
_ = 0  # anchor
#@ ensures \result == 0
def test_interaction_dynamic_features() -> int:
    """Dynamic features: eval, exec, metaclasses."""
    assert eval("2 + 3") == 5
    return 0

if __name__ == "__main__":
    assert test_interaction_dynamic_features() == 0
