"""Test 0203 — Python Reference 8.6.4.9: Mapping Patterns"""
_ = 0  # anchor
#@ ensures \result == 1
def test_match_mapping_patterns() -> int:
    """Mapping patterns: {"key": value}."""
    match {"x": 1, "y": 2}:
        case {"x": v}:
            return v
        case _:
            return 0

if __name__ == "__main__":
    assert test_match_mapping_patterns() == 1
