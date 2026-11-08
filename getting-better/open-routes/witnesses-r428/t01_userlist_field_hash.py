import collections


class R:
    def __init__(self) -> None:
        self.data: int = 0
        collections.UserList.__init__(self, [1])


#@ no_exception \all
def f(r: R) -> int:
    s = {r.data}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(R())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
