r"""Test 4440 -- gen #37 route #334 (expected PASS): control: fields whose every stored value is PROVABLY int keep their int model: a local bound to an int (`x = 3; self.r = x`), `2 ** 3`, `7 // 2 + 3 % 2`, `len("ab")`, `-(-2) + (1 if True else 2)`: `(c.r + c.a + c.b + c.p + c.q + c.n + c.m) % 1 == 0` PROVES.
"""
# pycsl-expected: PASS
class C:
    def __init__(self) -> None:
        x = 3
        self.r = x
        self.a = 1
        self.b = 2
        self.p = 2 ** 3
        self.q = 7 // 2 + 3 % 2
        self.n = len("ab")
        self.m = -(-2) + (1 if True else 2)


#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    c = C()
    return (c.r + c.a + c.b + c.p + c.q + c.n + c.m) % 1 == 0

if __name__ == "__main__":
    assert g() == True, g()
