from pathlib import Path


#@ requires len(str(p.parent)) == 1
#@ no_exception \all
def f(p: Path) -> int:
    q = p.parent
    return ord(q)


if __name__ == "__main__":
    try:
        print("result", f(Path("a/b")))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
