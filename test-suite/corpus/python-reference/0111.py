"""Test 0111 — Python Reference 4.4.2: Python Runtime Model"""
_ = 0  # anchor
#@ ensures \result == 0
def test_exception_groups() -> int:
    """ExceptionGroup bundles multiple exceptions."""
    try:
        raise ExceptionGroup("eg", [ValueError(1), TypeError(2)])
    except* ValueError:
        pass
    except* TypeError:
        pass
    return 0

if __name__ == "__main__":
    assert test_exception_groups() == 0
