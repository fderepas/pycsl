from typing import TypedDict


class TD(TypedDict, total=False):
    a: int


#@ no_exception \all
def f(d: TD) -> int:
    return d["a"]


if __name__ == "__main__":
    try:
        print("result", f({}))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
