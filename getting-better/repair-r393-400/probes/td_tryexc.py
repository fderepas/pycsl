from typing import NotRequired, TypedDict
class TD(TypedDict):
    a: int
    b: NotRequired[int]
#@ ensures \result == d["b"]
def f(d: TD) -> int:
    try:
        return d["b"]
    except KeyError:
        return 0
if __name__ == "__main__":
    print("result", f({"a": 1}))
