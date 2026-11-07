r"""Test 6111 -- route #417 (expected FAIL): `setattr(self, "x", [1])` then `{r.x}` under `no_exception \all` (CPython TypeError, unhashable list). PROVED at base 930d68ed5.
"""
# pycsl-expected: FAIL
class R:
    def __init__(self) -> None:
        self.x = 0
        setattr(self, "x", [1])


#@ no_exception \all
def f(r: R) -> int:
    s = {r.x}
    return 0


if __name__ == "__main__":
    try:
        print(f(R()))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
