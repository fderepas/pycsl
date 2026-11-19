#@ requires n >= 0
#@ no_exception \all
def f(n: int) -> int:
    xs = list(range(0, n, 1))
    return 0
if __name__ == "__main__":
    print(f(10**20))
