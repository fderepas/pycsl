"""Test 0196 — Python Reference 8.6.4.2: AS Patterns"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 0
def test_match_as_patterns() -> int:
    """AS patterns: case pattern as name."""
    x = (1, 2)
    match x:
        case (1, _) as p:
            assert p == (1, 2)
            return 0

if __name__ == "__main__":
    assert test_match_as_patterns() == 0
