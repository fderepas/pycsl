r"""Test 5093 -- gen #37 route #376 (expected PASS): CONTROL: `getattr(r, "zz", 7)` where no class body binds `zz` still answers the default 7 (CPython 7).
"""
# pycsl-expected: PASS
class R:
    k = 3
    def __init__(self) -> None:
        self.x = 1

#@ ensures \result == 7
def f(r: R) -> int:
    return getattr(r, "zz", 7)

if __name__ == "__main__":
    assert f(R()) == 7, f(R())
