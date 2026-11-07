from collections import UserList


def _unused() -> int:
    class UserList:
        pass
    return 0


class D(UserList):
    pass


#@ no_exception \all
def f(d: D) -> int:
    s = {d}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(D())
        print("no violation", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
