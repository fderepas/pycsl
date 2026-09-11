# pycsl-flags: --memory-model hoare

_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    s = "a b"
    parts = s.split(" ")
    return len(parts[5])

if __name__ == "__main__":
    f()
