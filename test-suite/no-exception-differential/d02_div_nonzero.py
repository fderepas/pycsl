# pycsl-flags: --memory-model hoare
#@ requires b != 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f(a: int, b: int) -> int:
    return a // b


if __name__ == "__main__":
    f(6, 2)
