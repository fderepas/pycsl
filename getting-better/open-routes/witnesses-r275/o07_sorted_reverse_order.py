# FALSE: sorted([1, 2], reverse=True) == [2, 1]; claim ys[0] <= ys[1].
#@ ensures \result == True
#@ assigns \nothing
def f() -> bool:
    xs: list[int] = [1, 2]
    ys = sorted(xs, reverse=True)
    return ys[0] <= ys[1]

if __name__ == "__main__":
    print(f())
