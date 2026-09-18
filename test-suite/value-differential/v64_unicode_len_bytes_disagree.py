"""v64 DISAGREE — the UTF-8 BYTE-length reading of a non-ASCII string. Python says 1; this claims the 2 that `len(s.encode())` would give."""


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    s: str = "é"
    return len(s)


if __name__ == "__main__":
    print(f())
