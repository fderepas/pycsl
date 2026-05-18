"""Test 0201 — Python Reference 8.6.4.7: Group Patterns"""
_ = 0  # anchor
#@ ensures \result == 2
def test_match_group_patterns() -> int:
    """Group patterns: (pattern)."""
    match 2:
        case (2):
            return 2
        case _:
            return 0

if __name__ == "__main__":
    assert test_match_group_patterns() == 2
