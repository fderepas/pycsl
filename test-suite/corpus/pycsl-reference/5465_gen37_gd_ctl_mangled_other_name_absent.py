r"""Test 5465 -- gen #37 systematic rule GD (expected PASS): CONTROL: `self.__k` is stored as `_R__k`; `getattr(r, "_R__j", 0)` names a DIFFERENT mangled name that nothing binds, so the default is still the answer; PROVED (CPython 0).
"""
# pycsl-expected: PASS
class R:
    def __init__(self) -> None:
        self.__k: int = 5

#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "_R__j", 0)

if __name__ == "__main__":
    assert f(R()) == 0
