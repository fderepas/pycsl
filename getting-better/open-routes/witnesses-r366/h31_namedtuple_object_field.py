from typing import NamedTuple

class N(NamedTuple):
    xs: object

#@ no_exception \all
#@ ensures \result == 1
def g(n: N) -> int:
    s = {n}
    return 1

if __name__ == "__main__":
    print(g(N([1])))
