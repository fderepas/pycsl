r"""Test 4084 -- gen #37 route #316 (expected FAIL): method with no `assigns` writes a field of its RECORD argument (`q.n = 5`); the stub cannot name it (it was an ill-typed `int` slot). REFUSED: PYCSL-METHOD-ARG-UNFRAMED.
"""
# pycsl-expected: FAIL
class Q:
    def __init__(self) -> None:
        self.n = 0

class P:
    def __init__(self) -> None:
        self.c = 0
    def reset(self, q: Q) -> None:
        q.n = 5

#@ ensures \result == 0
def f() -> int:
    q = Q()
    p = P()
    p.reset(q)
    return q.n

if __name__ == "__main__":
    assert f() == 0, f()
