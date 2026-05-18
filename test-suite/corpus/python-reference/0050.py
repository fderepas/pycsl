"""Test 0050 — Python Reference 3.2.8.1.2: Special writable attributes"""
_ = 0  # anchor
#@ ensures \result == 2
def test_dict_special_writable() -> int:
    """Dicts are writable: d[k] = v."""
    d = {}
    d["a"] = 1
    d["b"] = 2
    return len(d)

if __name__ == "__main__":
    assert test_dict_special_writable() == 2
