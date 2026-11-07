# NamedTuple modelled as a mutable record: a "store" through one name is invisible through another,
# but in CPython the store itself raises; here use a ghost-free contract on value
from typing import NamedTuple

class N(NamedTuple):
    x: int

#@ no_exception \all
#@ ensures \result == 7
def f() -> int:
    n = N(1)
    n.x = 7
    return n.x

if __name__ == "__main__":
    print(f())
