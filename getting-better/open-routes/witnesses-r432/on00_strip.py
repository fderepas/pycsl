from typing import Optional


#@ no_exception \all
def f(x: Optional[str]) -> int:
    return len(x.strip())


if __name__ == "__main__":
    try:
        r = f(None)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
