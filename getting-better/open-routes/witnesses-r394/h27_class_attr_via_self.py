from dataclasses import dataclass
from typing import Dict, List


@dataclass
class D:
    x: int


class C:
    K = D(1)

    #@ no_exception \all
    #@ assigns \nothing
    def m(self) -> int:
        s = {self.K}
        return len(s)


if __name__ == "__main__":
    try:
        print("result", C().m())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
