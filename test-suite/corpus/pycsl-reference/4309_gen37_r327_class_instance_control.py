r"""Test 4309 -- gen #37 route #327 (control, expected PASS): control: `c = C()` (a class and its instance) is NOT a collision — the class lowers to the type namespace. PROVED.
"""
# pycsl-expected: PASS
class C:
    def __init__(self) -> None:
        self.v = 4
#@ ensures \result == 4
#@ assigns \nothing
def g() -> int:
    c = C()
    return c.v

if __name__ == "__main__":
    assert g() == 4, g()
