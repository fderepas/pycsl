#@ no_exception \all
def f(n: int) -> int:
    y = float(n + 1)
    return 0
if __name__ == "__main__":
    print(f(10**400))
