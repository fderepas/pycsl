"""Test 0200 — Python Reference 8.6.4.6: Value Patterns"""
_ = 0  # anchor
#@ ensures \result == 0
def test_match_value_patterns() -> int:
    """Value patterns use dotted names."""
    import http
    match 200:
        case http.HTTPStatus.OK.value:
            return 0
        case _:
            return 1

if __name__ == "__main__":
    assert test_match_value_patterns() == 0
