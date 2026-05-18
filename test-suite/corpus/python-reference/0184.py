"""Test 0184 — Python Reference 8.1: The if statement"""
_ = 0  # anchor
#@ ensures \result >= 0
def test_if_statement(x: int) -> int:
    """if/elif/else conditional."""
    if x > 0:
        return x
    elif x == 0:
        return 0
    else:
        return -x

if __name__ == "__main__":
    assert test_if_statement(5) == 5
    assert test_if_statement(-3) == 3
