"""Test 0195 — Python Reference 8.6.4.1: OR Patterns"""
_ = 0  # anchor
#@ ensures \result == 0
def test_match_or_patterns() -> int:
    """OR patterns: case a | b."""
    x = 2
    match x:
        case 1 | 2 | 3:
            return 0
        case _:
            return 1

if __name__ == "__main__":
    assert test_match_or_patterns() == 0
