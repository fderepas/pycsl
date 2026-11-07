# pycsl-flags: --memory-model hoare

_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    a = 1
    if a > 0:
        return 1 // (a - a)
    return 0

if __name__ == "__main__":
    f()
