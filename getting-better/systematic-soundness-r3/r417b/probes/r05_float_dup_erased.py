#@ no_exception \all
def f(n: int) -> int:
    if -100 < n and n < 100:
        a = float(n)
    if isinstance(float(n), float):
        return 1
    return 0
if __name__ == "__main__":
    print(f(10**400))
