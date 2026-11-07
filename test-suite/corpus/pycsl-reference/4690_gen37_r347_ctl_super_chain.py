r"""Test 4690 -- gen #37 route #347: CONTROL: base field reached by a leading `super().__init__()`; PROVES (CPython 3).
"""
class A:
    def __init__(self) -> None:
        self.x = 1

class B(A):
    def __init__(self) -> None:
        super().__init__()
        self.y = 2

#@ no_exception \all
def f(b: B) -> int:
    return b.x + b.y

if __name__ == "__main__":
    print(f(B()))
