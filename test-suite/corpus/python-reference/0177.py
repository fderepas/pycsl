"""Test 0177 — Python Reference 7.9: The break statement"""
# (#44) WAS `pycsl-expected: FAIL`, and it PROVES today. Its contract is TRUE of the
# program, so this is a CAPABILITY GAIN, not a soundness regression — the construct
# it exercises became supported after the file was written. Found by making the
# suite report XPASS as a FAILURE: until then an expected-FAIL test that started
# proving was reported PASS, which made all 241 negative witnesses unenforceable.
# pycsl-expected: PASS
_ = 0  # anchor
#@ ensures \result == 0
def test_break_statement() -> int:
    """break exits the nearest loop."""
    for i in range(100):
        if i == 5:
            break
    assert i == 5
    return 0

if __name__ == "__main__":
    assert test_break_statement() == 0
