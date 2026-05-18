"""Test 0202 — Python Reference 8.6.4.8: Sequence Patterns"""
_ = 0  # anchor
#@ ensures \result == 3
def test_match_sequence_patterns() -> int:
    """Sequence patterns: [a, b, c]."""
    match [1, 2, 3]:
        case [a, b, c]:
            return c
        case _:
            return 0

if __name__ == "__main__":
    assert test_match_sequence_patterns() == 3
