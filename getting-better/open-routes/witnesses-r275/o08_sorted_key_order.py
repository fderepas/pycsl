# FALSE: sorted([1, 2], key=lambda v: -v) == [2, 1]; claim ys[0] <= ys[1].
#@ ensures \result == True
#@ assigns \nothing
def f() -> bool:
    xs: list[int] = [1, 2]
    ys = sorted(xs, key=lambda v: -v)
    return ys[0] <= ys[1]

if __name__ == "__main__":
    print(f())
