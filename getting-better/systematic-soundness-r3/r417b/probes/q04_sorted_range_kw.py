#@ requires n >= 0
#@ no_exception \all
def f(n: int) -> int:
    xs = sorted(range(n), reverse=True)
    return 0
if __name__ == "__main__":
    print(f(10**20))
