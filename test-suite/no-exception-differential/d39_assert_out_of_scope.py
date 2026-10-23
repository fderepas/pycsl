# pycsl-flags: --memory-model hoare

_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    a = 0
    assert a == 1
    return 0

if __name__ == "__main__":
    f()
