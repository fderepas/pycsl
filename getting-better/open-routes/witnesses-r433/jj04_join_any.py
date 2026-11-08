from typing import Any, List

#@ no_exception \all
def f(xs: List[Any]) -> int:
    return len("".join(xs))


if __name__ == "__main__":
    try:
        r = f([1])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
