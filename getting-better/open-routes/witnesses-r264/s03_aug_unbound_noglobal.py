# FALSE: `n` is never bound anywhere; `n += 1` raises UnboundLocalError. Claims \result == 1.
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    n += 1
    return n

if __name__ == "__main__":
    print(f())
