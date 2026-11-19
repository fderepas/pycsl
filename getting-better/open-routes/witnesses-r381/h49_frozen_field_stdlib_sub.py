from dataclasses import dataclass
from collections import UserDict

class U(UserDict):
    pass

@dataclass(frozen=True)
class D:
    u: U

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D(U())))
