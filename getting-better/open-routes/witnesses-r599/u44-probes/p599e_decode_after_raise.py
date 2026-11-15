from __future__ import annotations


#@ ensures \result == 0
#@ assigns \nothing
def f(b: bytes, n: int) -> int:
    x = 0
    try:
        if n > 100:
            raise UnicodeDecodeError("utf-8", b"", 0, 1, "u")
        x = 1
        t = b.decode()
    except UnicodeDecodeError:
        return x
    return 0


if __name__ == "__main__":
    r = f(b"\xff", 0)
    print("VIOLATION contract" if r != 0 else "result", r)
