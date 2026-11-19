from typing import NotRequired, TypedDict
class TD(TypedDict):
    a: int
    b: NotRequired[int]
#@ no_exception \all
#@ ensures \result == d["a"] + 1
def f(d: TD) -> int:
    return d["a"] + 1
if __name__ == "__main__":
    print("result", f({"a": 1}))
