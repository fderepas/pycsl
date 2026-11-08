# pycsl-flags: --memory-model hoare
_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    b = bytearray([1])
    b[0] = 999
    return b[0]


if __name__ == "__main__":
    f()
