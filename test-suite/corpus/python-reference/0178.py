"""Test 0178 — Python Reference 7.10: The continue statement"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 0
def test_continue_statement() -> int:
    """continue skips to the next iteration."""
    total = 0
    for i in range(5):
        if i == 2:
            continue
        total += i
    assert total == 0 + 1 + 3 + 4
    return 0

if __name__ == "__main__":
    assert test_continue_statement() == 0
