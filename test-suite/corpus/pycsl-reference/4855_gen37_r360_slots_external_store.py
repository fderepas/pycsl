r"""Test 4855 -- gen #37 route #360 (expected FAIL): (new) a verified function stores `r.y = 1` on a parameter annotated with a slotted class (`y` a field another method stores). REFUSED (PYCSL-R360-SLOTS-STORE, route #360).
"""
# pycsl-expected: FAIL
class R:
    __slots__ = ("x",)
    def __init__(self) -> None:
        self.x = 0

#@ no_exception \all
#@ ensures \result == 1
def f(r: R) -> int:
    r.y = 1
    return r.y

if __name__ == "__main__":
    print(f(R()))
