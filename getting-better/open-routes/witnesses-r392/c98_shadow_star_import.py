from collections import *


def _unused() -> int:
    class OrderedDict:
        pass
    return 0


class D(OrderedDict):
    pass


#@ no_exception \all
def f(d: D) -> int:
    s = {d}
    return len(s)


if __name__ == "__main__":
    try:
        print("result", f(D()))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
