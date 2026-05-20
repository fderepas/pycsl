"""Test 0199 — Python Reference 8.6.4.5: Wildcard Patterns"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 0
def test_match_wildcard_patterns() -> int:
    """Wildcard _ matches anything."""
    match "anything":
        case _:
            return 0

if __name__ == "__main__":
    assert test_match_wildcard_patterns() == 0
