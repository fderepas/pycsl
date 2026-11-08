# FALSE: for any list, sorted(reverse=True) is ascending (claimed). xs=[1,2] counterexample.
#@ requires len(xs) == 2
#@ ensures \result == True
#@ assigns \nothing
def f(xs: list[int]) -> bool:
    ys = sorted(xs, reverse=True)
    return ys[0] <= ys[1]

if __name__ == "__main__":
    print(f([1, 2]))
