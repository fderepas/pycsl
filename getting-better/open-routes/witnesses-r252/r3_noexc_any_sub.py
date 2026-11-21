from typing import Any


#@ no_exception \all
#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any) -> int:
    y = x - x
    return 1


if __name__ == "__main__":
    class P:
        def __sub__(self, o: object) -> int:
            raise ValueError("no")

    try:
        f(P())
    except ValueError:
        print("ValueError escaped")
