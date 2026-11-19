#@ requires n >= 0
#@ no_exception \all
def f(n: int) -> int:
    c = 0
    if n < 100:
        for x in sorted(range(n)):
            c = 1
    s = set(sorted(range(n)))
    return 0
if __name__ == "__main__":
    print(f(10**20))
