r"""Test 4085 -- gen #37 route #317 (expected FAIL): `\trusted` function with no `assigns` writes a field of its record argument; its `val` had no writes and `q.n == 0` PROVED (CPython 5). REFUSED: PYCSL-VAL-ARG-UNFRAMED.
"""
# pycsl-expected: FAIL
class Q:
    def __init__(self) -> None:
        self.n = 0

#@ \trusted
def reset(q: Q) -> None:
    q.n = 5

#@ ensures \result == 0
def f() -> int:
    q = Q()
    reset(q)
    return q.n

if __name__ == "__main__":
    assert f() == 0, f()
