r"""Test 4442 -- gen #37 route #334 (expected PASS): control: a dict field whose every VALUE is provably int (`self.d = {"a": 1}`) keeps its int values: `c.d["a"] % 1 == 0` PROVES (twin 4428 with a float value is refused).
"""
# pycsl-expected: PASS
class C:
    def __init__(self) -> None:
        self.d = {"a": 1}


#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    c = C()
    return c.d["a"] % 1 == 0

if __name__ == "__main__":
    assert g() == True, g()
