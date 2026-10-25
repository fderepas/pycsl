from typing import TypedDict


class TD(TypedDict):
    a: int


#@ no_exception \all
def f() -> int:
    t = TD(a=1)
    return t.a  # type: ignore


if __name__ == "__main__":
    try:
        f()
        print("no violation")
    except AttributeError as e:
        print("VIOLATION AttributeError", e)
