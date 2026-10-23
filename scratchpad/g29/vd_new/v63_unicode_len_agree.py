"""v63 AGREE — `len` of a NON-ASCII string counts CODE POINTS, not UTF-8 bytes: `len('é')` is 1."""


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    s: str = "é"
    return len(s)


if __name__ == "__main__":
    print(f())
