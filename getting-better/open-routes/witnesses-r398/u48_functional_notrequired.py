from typing import NotRequired, TypedDict

TD = TypedDict("TD", {"a": int, "b": NotRequired[int]})


#@ no_exception \all
def f(d: TD) -> int:
    return d["b"]


if __name__ == "__main__":
    try:
        print("result", f({"a": 1}))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
