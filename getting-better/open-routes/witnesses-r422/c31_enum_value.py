import enum


class E(enum.Enum):
    A = [1]


#@ no_exception \all
def f() -> int:
    k = E.A.value
    s = {k}
    return len(s)


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
