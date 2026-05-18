"""Test 0049 — Python Reference 3.2.8.1.1: Special read-only attributes"""
_ = 0  # anchor
#@ ensures \result == 10
def test_dict_special_readonly() -> int:
    """Dicts have special read-only attribute: views."""
    d = {1: 10, 2: 20}
    return d[1]

if __name__ == "__main__":
    assert test_dict_special_readonly() == 10
