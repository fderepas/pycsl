from typing import List


#@ ensures \result == 3
def f() -> int:
    return sum([1, 2], **{"start": 10})


if __name__ == "__main__":
    r = f()
    print("VIOLATION f =", r) if r != 3 else print("no violation")
