from typing import NotRequired, TypedDict


class TD(TypedDict):
    a: int
    b: NotRequired[int]


#@ no_exception \all
def f(d: TD) -> int:
    return d["b"]


if __name__ == "__main__":
    try:
        print("result", {"a": 1} and f({"a": 1}))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
