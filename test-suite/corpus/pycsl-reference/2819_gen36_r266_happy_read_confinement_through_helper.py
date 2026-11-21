r"""Test 2819 — route #266 (expected FAIL): the READ-confinement sibling — non-exempt `peeker`
hands self.secret to a module helper that reads `a[1]`, inside the confined region [0, 4).
CPython: 7 (the confined cell). Now refused (the field escapes as a call argument).
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires 0 <= i and i < len(a)
#@ assigns \nothing
def peek(a: list[int], i: int) -> int:
    return a[i]

_z = 0
#@ happy conf:
#@     region 0 .. 4
#@     reads self.secret outside region
#@     except reader
#@ class invariant \length(self.secret) >= 8
class S:
    def __init__(self) -> None:
        self.secret: list[int] = [7] * 8

    #@ assigns \nothing
    def reader(self) -> int:
        return self.secret[0]

    #@ assigns \nothing
    def peeker(self) -> int:
        return peek(self.secret, 1)

if __name__ == "__main__":
    print(S().peeker())
