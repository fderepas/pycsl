r"""Test 4308 -- gen #37 route #327 (expected FAIL): classes `Ab` and `AB` lower their methods to one `ab__m`. Fail-closed at base; REFUSED now.
"""
# pycsl-expected: FAIL
class Ab:
    def __init__(self) -> None:
        self.v = 1
    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return 1
class AB:
    def __init__(self) -> None:
        self.v = 2
    #@ ensures \result == 2
    #@ assigns \nothing
    def m(self) -> int:
        return 2
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    a = AB()
    return a.m()

if __name__ == "__main__":
    assert g() == 1, g()
