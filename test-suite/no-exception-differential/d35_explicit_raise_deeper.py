# pycsl-flags: --memory-model hoare

#@ ensures True
#@ assigns \nothing
def g() -> int:
    raise ValueError("boom")

_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    return g()

if __name__ == "__main__":
    f()
