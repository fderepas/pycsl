from typing import NotRequired, TypedDict
class TD(TypedDict):
    a: int
    b: NotRequired[int]
#@ ensures \result == 1
def f(d: TD) -> int:
    if "b" in d:
        return 1
    return 0
if __name__ == "__main__":
    print("result", f({"a": 1}))
