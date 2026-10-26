class M(type):
    def __hash__(cls) -> int:
        n = len(cls.__name__)
        if n > 0:
            raise ValueError("mh")
        return n


class K(metaclass=M):
    pass


#@ no_exception \all
def f() -> int:
    s = {K}
    return len(s)


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
