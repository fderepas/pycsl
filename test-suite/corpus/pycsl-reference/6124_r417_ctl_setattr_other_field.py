r"""Test 6124 -- route #417 (expected PASS): CONTROL: `setattr(self, "y", [1])` and `{r.x}` of the int field `x` (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
class R:
    def __init__(self) -> None:
        self.x = 0
        self.y = 0
        setattr(self, "y", [1])


#@ no_exception \all
def f(r: R) -> int:
    s = {r.x}
    return 0


if __name__ == "__main__":
    print(f(R()))
