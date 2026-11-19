# advice audit (route #480 / #445 on a builtin receiver): corpus 7508 `return len.zz` with the
# attribute name FIXED to one the real builtin has (`len.__name__`), claim kept.
#@ no_exception \all
def f(n: int) -> int:
    s = len.__name__
    return n


if __name__ == "__main__":
    print("result", f(1))
