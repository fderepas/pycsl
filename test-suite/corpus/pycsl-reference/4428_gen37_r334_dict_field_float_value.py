r"""Test 4428 -- gen #37 route #334 (expected FAIL): a dict field with a float VALUE (`self.d = {"a": 0.5}`) had its values read as ints and `c.d["a"] % 1 == 0` PROVED (CPython False). REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK): the values of a dict field are classified like a field.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.d = {"a": 0.5}

#@ assigns \nothing
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    c = C()
    return 1 if c.d["a"] % 1 == 0 else 0

if __name__ == "__main__":
    assert g() == 1, g()
