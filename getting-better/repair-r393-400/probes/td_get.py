from typing import NotRequired, TypedDict
class TD(TypedDict):
    a: int
    b: NotRequired[int]
#@ ensures \result == 7
def f(d: TD) -> int:
    return d.get("b", 7)
if __name__ == "__main__":
    print("result", f({"a": 1, "b": 3}))
