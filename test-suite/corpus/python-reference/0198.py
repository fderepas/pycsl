"""Test 0198 — Python Reference 8.6.4.4: Capture Patterns"""
_ = 0  # anchor
#@ ensures \result == 5
def test_match_capture_patterns() -> int:
    """Capture patterns bind to a name."""
    match 5:
        case x:
            return x

if __name__ == "__main__":
    assert test_match_capture_patterns() == 5
