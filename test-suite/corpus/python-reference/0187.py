"""Test 0187 — Python Reference 8.4.1: except clause"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 0
def test_except_star() -> int:
    """except* handles ExceptionGroups."""
    result = 1
    try:
        raise ExceptionGroup("g", [ValueError(1)])
    except* ValueError:
        result = 0
    return result

if __name__ == "__main__":
    assert test_except_star() == 0
