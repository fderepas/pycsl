r"""no_exception ValueError on a tuple unpack arity mismatch"""
_ = 0  # anchor


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    s = "a"
    a, b = s.split(",")
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
