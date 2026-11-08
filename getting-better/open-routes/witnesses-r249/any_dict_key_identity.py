from typing import Any, Dict


#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any) -> int:
    d: Dict[Any, int] = {}
    d[x] = 1
    return d[x]


if __name__ == "__main__":
    import itertools
    c = itertools.count()

    class H:
        def __hash__(self) -> int:
            return next(c)

    try:
        f(H())
    except KeyError:
        print("KeyError")
