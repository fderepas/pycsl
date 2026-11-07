#@ requires 0 <= n and n <= 100
#@ no_exception \all
def f(n: int) -> int:
    c = 0
    for x in sorted(range(n)):
        c = 1
    for y in sorted(range(n)):
        c = 2
    xs = list(range(n))
    ys = list(range(n))
    a = float(n)
    b = float(n)
    return 0
if __name__ == "__main__":
    print(f(5))
