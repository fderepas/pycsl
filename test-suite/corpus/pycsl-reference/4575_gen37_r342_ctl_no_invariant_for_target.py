r"""Test 4575 -- gen #37 route #342: CONTROL: a class WITHOUT an invariant keeps `for self.x in ..` in its constructor; PROVES.
"""
class C:
    def __init__(self) -> None:
        self.k = 7
        self.x = 0
        for self.x in range(3):
            pass

#@ ensures \result == 7
def f() -> int:
    c = C()
    return c.k

if __name__ == "__main__":
    assert f() == 7
