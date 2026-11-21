from pathlib import Path


#@ requires len(str(p)) >= 1
#@ no_exception \all
def f(p: Path) -> int:
    return ord(p[0])


if __name__ == "__main__":
    try:
        print("result", f(Path("a")))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
