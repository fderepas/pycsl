# FALSE: nested class body executes push(xs).
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
    class K:
        v = push(xs)
    return xs[0]

if __name__ == "__main__":
    print(f([0]))
