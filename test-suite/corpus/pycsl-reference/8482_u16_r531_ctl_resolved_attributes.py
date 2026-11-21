r"""Test 8482 -- route #531 (control, expected PASS): attribute reads that resolve stay field initialisers: `self.j` after its store, a class constant `self.K` read before any store; CPython f(2) returns 1
"""
# pycsl-expected: PASS


class C:
    K = 5

    def __init__(self, n: int) -> None:
        self.j = n
        self.k = self.j
        self.c = self.K


#@ no_exception \all
#@ ensures \result == 1
def f(n: int) -> int:
    c = C(n)
    return 1


if __name__ == "__main__":
    print(f(2))
