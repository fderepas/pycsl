class R:
    def __init__(self, v: int) -> None:
        self.v = v


#@ no_exception \all
def f(r: R) -> int:
    x = float(r.v)
    return 0


if __name__ == "__main__":
    try:
        print(f(R(10**400)))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
