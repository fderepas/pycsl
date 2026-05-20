"""Test 0193 — Python Reference 8.6.2: Guards"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 0
def test_match_guards() -> int:
    """Guards add conditions to case clauses."""
    x = 10
    match x:
        case n if n > 5:
            return 0
        case _:
            return 1

if __name__ == "__main__":
    assert test_match_guards() == 0
