# FALSE: no `global`, `n += 1` raises UnboundLocalError in CPython; claims normal return 1.
n = 0

#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    n += 1
    return n

if __name__ == "__main__":
    print(f())
