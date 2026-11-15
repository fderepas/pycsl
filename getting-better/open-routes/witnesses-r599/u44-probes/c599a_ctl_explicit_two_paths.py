from __future__ import annotations


#@ ensures (n > 100 and \result == 1) or (n <= 100 and \result == 2)
#@ assigns \nothing
def f(n: int) -> int:
    x = 0
    try:
        if n > 100:
            raise OSError("u")
        x = 2
    except OSError:
        return 1
    return x


if __name__ == "__main__":
    ok = f(101) == 1 and f(0) == 2
    print("result" if ok else "VIOLATION contract", f(101), f(0))
