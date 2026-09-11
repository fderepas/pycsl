# pycsl-flags: --memory-model hoare

_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    s = "abc"
    return s.index("z")

if __name__ == "__main__":
    f()
