# FALSE: nested def's default `push(xs)` runs when the def executes and appends to xs; f returns 1.
#@ requires len(xs) >= 1
#@ ensures \result == 0
#@ assigns xs[0]
def push(xs: list[int]) -> int:
    xs[0] = 5
    return 0

#@ requires len(xs) >= 1 and xs[0] == 0
#@ ensures \result == 0
#@ assigns xs[0]
def f(xs: list[int]) -> int:
    def inner(y: int = push(xs)) -> int:
        return y
    return xs[0]

if __name__ == "__main__":
    print(f([0]))
