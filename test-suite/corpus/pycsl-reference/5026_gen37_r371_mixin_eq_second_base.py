r"""Test 5026 -- gen #37 route #371 (expected FAIL): `D(N, M)` with `M.__eq__` (second base) (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
class M:
    def __eq__(self, o: object) -> bool:
        return True

class N:
    pass

class D(N, M):
    def __init__(self) -> None:
        self.x = 1

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D()))
