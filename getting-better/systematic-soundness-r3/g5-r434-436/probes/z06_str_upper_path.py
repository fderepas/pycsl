from pathlib import Path


#@ no_exception \all
def f(p: Path) -> int:
    s = str.upper(p)
    return 0


if __name__ == "__main__":
    try:
        print("result", f(Path("a")))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
