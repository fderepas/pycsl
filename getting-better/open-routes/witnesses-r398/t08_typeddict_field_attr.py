from typing import TypedDict


class TD(TypedDict):
    a: int


#@ no_exception \all
def f(d: TD) -> int:
    return d.a


if __name__ == "__main__":
    try:
        print("result", f({"a": 1}))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
