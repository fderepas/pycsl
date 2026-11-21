from pathlib import Path


#@ no_exception \all
def f() -> int:
    p = Path("a")
    return ord(p)


if __name__ == "__main__":
    try:
        print("result", f())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
