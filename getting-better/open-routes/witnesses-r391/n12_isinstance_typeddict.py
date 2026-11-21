from typing import Any, TypedDict


class TD(TypedDict):
    a: int


#@ no_exception \all
def f(x: Any) -> bool:
    return isinstance(x, TD)


if __name__ == "__main__":
    try:
        f({"a": 1})
        print("no violation")
    except TypeError as e:
        print("VIOLATION TypeError", e)
