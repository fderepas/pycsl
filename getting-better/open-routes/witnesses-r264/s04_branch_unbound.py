# FALSE: y bound only on the True branch; f(False) raises UnboundLocalError. Claims \result >= 0.
#@ ensures \result >= 0
#@ assigns \nothing
def f(c: bool) -> int:
    if c:
        y = 1
    return y

if __name__ == "__main__":
    print(f(False))
