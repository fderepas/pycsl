# pycsl-flags: --memory-model hoare

#@ requires True
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f(a: int) -> int:
    return int(a)


if __name__ == "__main__":
    f(5)
