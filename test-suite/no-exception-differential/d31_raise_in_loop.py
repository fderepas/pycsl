# pycsl-flags: --memory-model hoare

_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    t = 0
    for i in range(3):
        t = t + 1 // (i - i)
    return t

if __name__ == "__main__":
    f()
