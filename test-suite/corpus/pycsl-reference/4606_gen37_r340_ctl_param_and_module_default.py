r"""Test 4606 -- gen #37 route #340 (expected PASS): CONTROL: a never-rebound parameter and a module constant as nested-def defaults stay admitted and prove.
"""
# pycsl-expected: PASS
K = 7

#@ ensures \result == x + 7
def f(x: int) -> int:
    def g(y: int = x, z: int = K) -> int:
        return y + z
    return g()

if __name__ == "__main__":
    assert f(1) == 8
