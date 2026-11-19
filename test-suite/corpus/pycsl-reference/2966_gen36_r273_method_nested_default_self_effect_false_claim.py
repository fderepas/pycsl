r"""Test 2966 — route #273 (expected FAIL): inside a METHOD, the nested def's default
`self.push()` runs at the `def` and sets `self.v = 5`; `f` claims `\result == 0` for
`return self.v`. PROVED at 5a307a33. CPython: 5. Now refused
(PYCSL-SEM-DEF-TIME-EVALUATION).
"""
# pycsl-expected: FAIL

class C:
    def __init__(self) -> None:
        self.v: int = 0

    #@ ensures \result == 1
    #@ assigns self.v
    def push(self) -> int:
        self.v = 5
        return 1

    #@ requires self.v == 0
    #@ ensures \result == 0
    #@ assigns self.v
    def f(self) -> int:
        def inner(y: int = self.push()) -> int:
            return y
        return self.v

if __name__ == "__main__":
    print(C().f())
