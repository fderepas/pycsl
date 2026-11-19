r"""Test 4271 -- gen #37 route #325 control (expected PASS): a user method annotated `-> int` whose body returns an int keeps its stub.
"""
# pycsl-expected: PASS
class C:
    #@ assigns \nothing
    def r(self) -> int:
        return 4
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    c = C()
    if c.r() % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert g() == 1
