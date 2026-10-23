"""Test 0178 — Python Reference 7.10: The continue statement"""
# (#44) WAS `pycsl-expected: FAIL`, and it PROVES today. Its contract is TRUE of the
# program, so this is a CAPABILITY GAIN, not a soundness regression — the construct
# it exercises became supported after the file was written. Found by making the
# suite report XPASS as a FAILURE: until then an expected-FAIL test that started
# proving was reported PASS, which made all 241 negative witnesses unenforceable.
# pycsl-expected: PASS
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
