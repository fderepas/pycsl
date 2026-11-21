from typing import List, Union

#@ no_exception \all
def f(xs: List[Union[str, int]]) -> int:
    return len("".join(xs))


if __name__ == "__main__":
    try:
        r = f(["a", 1])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
