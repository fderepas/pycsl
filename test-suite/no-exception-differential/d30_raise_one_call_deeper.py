# pycsl-flags: --memory-model hoare

#@ ensures True
#@ assigns \nothing
def g(a: int) -> int:
    b = 0
    return a // b

_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    return g(1)

if __name__ == "__main__":
    f()
