r"""Test 4689 -- gen #37 route #347: CONTROL: conditional store over a class-level default; PROVES (CPython 0).
"""
class R:
    x = 0
    def __init__(self, flag: bool) -> None:
        self.n = 0
        if flag:
            self.x = 1

#@ no_exception \all
def f(r: R) -> int:
    return r.x

if __name__ == "__main__":
    print(f(R(False)))
