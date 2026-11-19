# pycsl-flags: --memory-model hoare

_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    return int("10", 1)

if __name__ == "__main__":
    f()
