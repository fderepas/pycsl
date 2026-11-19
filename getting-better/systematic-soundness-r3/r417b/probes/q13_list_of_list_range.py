#@ requires n >= 0
#@ no_exception \all
def f(n: int) -> int:
    xs = len(list(range(n)))
    return 0
if __name__ == "__main__":
    print(f(10**20))
