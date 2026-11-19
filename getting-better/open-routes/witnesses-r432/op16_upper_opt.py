from typing import Optional

#@ no_exception \all
def f(s: str, x: Optional[str]) -> int:
    return len(x.upper())


if __name__ == "__main__":
    try:
        r = f("abc", None)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
