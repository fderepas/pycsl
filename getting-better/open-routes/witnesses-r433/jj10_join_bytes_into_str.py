from typing import List

#@ no_exception \all
def f(xs: List[bytes]) -> int:
    return len("".join(xs))


if __name__ == "__main__":
    try:
        r = f([b"a"])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
