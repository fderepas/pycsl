# FALSE: `del x` then read -> UnboundLocalError.
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    x = 1
    del x
    return x

if __name__ == "__main__":
    print(f())
