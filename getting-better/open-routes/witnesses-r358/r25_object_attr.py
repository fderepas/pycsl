# route #343 residual: attribute read on an erased `x: object` under no_exception
#@ no_exception \all
def f(x: object) -> int:
    y = x.foo
    return 0

if __name__ == "__main__":
    f(object())
