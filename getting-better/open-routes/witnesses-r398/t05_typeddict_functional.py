from typing import TypedDict

TD = TypedDict("TD", {"a": int})


#@ no_exception \all
def f() -> int:
    d = TD(a=1)
    return d.a


if __name__ == "__main__":
    try:
        print("result", f())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
