r"""Test 4691 -- gen #37 route #347: CONTROL: the path without the store RAISES (no instance); PROVES (CPython 1).
"""
class R:
    def __init__(self, flag: bool) -> None:
        self.n = 0
        if not flag:
            raise ValueError("no")
        self.x = 1

#@ no_exception \all
def f(r: R) -> int:
    return r.x

if __name__ == "__main__":
    print(f(R(True)))
