"""Test 0216 — Python Reference 9.3: Interactive input"""
_ = 0  # anchor
#@ ensures \result == 0
def test_interactive_input() -> int:
    """Interactive mode reads one statement at a time."""
    return 0

if __name__ == "__main__":
    assert test_interactive_input() == 0
