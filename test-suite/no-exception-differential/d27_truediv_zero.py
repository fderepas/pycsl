# pycsl-flags: --memory-model hoare

_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    a = 1
    b = 0
    return int(a / b)

if __name__ == "__main__":
    f()
