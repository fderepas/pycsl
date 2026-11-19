r"""Test 4886 -- gen #37 route #363: CONTROL: `super(B, self).__init__()` (the two-argument spelling of `super()`) credits A's constructor; PROVES (CPython 1).
"""
class A:
    def __init__(self) -> None:
        self.x = 1

class B(A):
    def __init__(self) -> None:
        super(B, self).__init__()
        self.n = 0

#@ no_exception \all
def f(b: B) -> int:
    return b.x + b.n

if __name__ == "__main__":
    print(f(B()))
