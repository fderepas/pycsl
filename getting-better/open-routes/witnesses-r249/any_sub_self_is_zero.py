from typing import Any


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any) -> int:
    return x - x


if __name__ == "__main__":
    class P:
        def __sub__(self, o: object) -> int:
            return 7

    print(f(P()))  # 7
