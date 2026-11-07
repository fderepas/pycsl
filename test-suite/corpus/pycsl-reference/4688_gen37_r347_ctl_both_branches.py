r"""Test 4688 -- gen #37 route #347: CONTROL: field stored on BOTH `if` branches; PROVES (CPython 2).
"""
class R:
    def __init__(self, flag: bool) -> None:
        self.n = 0
        if flag:
            self.x = 1
        else:
            self.x = 2

#@ no_exception \all
def f(r: R) -> int:
    return r.x

if __name__ == "__main__":
    print(f(R(False)))
