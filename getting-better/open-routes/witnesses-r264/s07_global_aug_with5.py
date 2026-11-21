# FALSE: global n = 5 but no `global` decl; `n += 1` -> UnboundLocalError. Claims \result == 1 (default 0?).
n = 5

#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    n += 1
    return n

if __name__ == "__main__":
    print(f())
