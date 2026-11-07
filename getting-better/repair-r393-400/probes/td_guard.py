from typing import NotRequired, TypedDict
class TD(TypedDict):
    a: int
    b: NotRequired[int]
#@ no_exception \all
def f(d: TD) -> int:
    if "b" in d:
        return d["b"]
    return 0
if __name__ == "__main__":
    print("result", f({"a": 1}))
