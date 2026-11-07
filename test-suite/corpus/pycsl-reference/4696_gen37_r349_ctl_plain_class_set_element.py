r"""Test 4696 -- gen #37 route #349: CONTROL: plain class (identity hash) in a set; PROVES (CPython 1).
"""
class R:
    def __init__(self) -> None:
        self.x = 0

#@ no_exception \all
#@ ensures \result == 1
def g(r: R) -> int:
    s = {r}
    return 1

if __name__ == "__main__":
    print(g(R()))
