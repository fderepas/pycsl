"""Test 0197 — Python Reference 8.6.4.3: Literal Patterns"""
_ = 0  # anchor
#@ ensures \result == 42
def test_match_literal_patterns() -> int:
    """Literal patterns match exact values."""
    match 42:
        case 42:
            return 42
        case _:
            return 0

if __name__ == "__main__":
    assert test_match_literal_patterns() == 42
