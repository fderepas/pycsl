class R:
    def __init__(self, t: tuple) -> None:
        self.t: tuple = t

#@ no_exception \all
def f(r: R) -> int:
    s = {r.t}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(R(([1],)))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
