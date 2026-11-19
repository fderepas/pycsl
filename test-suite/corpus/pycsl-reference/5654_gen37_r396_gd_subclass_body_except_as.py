r"""Test 5654 -- gen #37 route #396 latent (expected FAIL): a subclass body binds `k` (`except .. as k`, then `k = 5`); `getattr(r, "k", 0) == 0`; PROVED at base 3b2d2e763 (CPython 5). REFUSED (PYCSL-R376-GETATTR-CLASS-BINDING).
"""
# pycsl-expected: FAIL
class R:
    def __init__(self) -> None:
        self.x: int = 1
class S(R):
    try:
        raise ValueError()
    except ValueError as k:
        pass
    k = 5
#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "k", 0)
if __name__ == "__main__":
    print("result", f(S()))
