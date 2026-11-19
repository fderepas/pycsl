r"""Test 3819 -- gen #37 route #306 (expected PASS): CONTROL: same shape with `len(s) >= 6` proves `\result == "y"`.
"""
# pycsl-expected: PASS
OP_MAP = {"a": "x", "b": "y"}


#@ requires len(s) >= 6
#@ no_exception \all
#@ ensures \result == "y"
def f(s: str) -> str:
    return OP_MAP.get("b", s[5])

if __name__ == "__main__":
    assert f("abcdef") == "y"
