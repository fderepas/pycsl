from typing import Optional


#@ no_exception \all
def f(x: str | None) -> int:
    return len(x.lower())


if __name__ == "__main__":
    try:
        r = f(None)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
