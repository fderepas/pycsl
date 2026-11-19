r"""Test 6643 -- route #439 (expected PASS): CONTROL: a file with `setattr(self, nm, v)` (a computed name): a field hashed in an UN-claimed function, and a typed parameter hashed under `no_exception \all`, are not refused. PROVED at base and candidate.
"""
# pycsl-expected: PASS
class R:
    def __init__(self, nm: str) -> None:
        self.x: int = 1
        setattr(self, nm, 2)


#@ ensures \result == n + 1
def g(r: R, n: int) -> int:
    s = {r.x}
    return n + 1


#@ no_exception \all
#@ ensures \result == n + 1
def f(k: int, n: int) -> int:
    s = {k}
    return n + 1


if __name__ == "__main__":
    try:
        r = g(R("y"), 1) + f(3, 1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
