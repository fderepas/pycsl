from typing import Callable
class Cc:
    __hash__ = None
    def __call__(self) -> int:
        return 1


#@ no_exception \all
def f(c: Callable[[], int]) -> int:
    s = {c}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(Cc())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
