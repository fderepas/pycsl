# route #343: iterate an erased `x: object` under no_exception
#@ no_exception \all
def f(x: object) -> int:
    n = 0
    for z in x:
        n = n + 1
    return n

if __name__ == "__main__":
    f(object())
