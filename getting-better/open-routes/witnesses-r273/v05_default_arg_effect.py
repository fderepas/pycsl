# FALSE: nested def's default calls bump(), which increments the global; claim result 0.
count: int = 0

#@ ensures \result == 7
#@ assigns count
def bump() -> int:
    global count
    count = count + 1
    return 7

#@ requires count == 0
#@ ensures \result == 0
#@ assigns count
def f() -> int:
    def inner(y: int = bump()) -> int:
        return y
    return count

if __name__ == "__main__":
    print(f())
