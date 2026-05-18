"""Test 0139 — Python Reference 6.2.7: Set displays"""
_ = 0  # anchor
#@ ensures \result == 2
def test_dict_displays() -> int:
    """Dict displays: {k: v, ...}."""
    d = {"a": 1, "b": 2}
    return len(d)

if __name__ == "__main__":
    assert test_dict_displays() == 2
