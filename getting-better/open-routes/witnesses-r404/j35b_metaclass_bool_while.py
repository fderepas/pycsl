class M(type):
    def __bool__(cls) -> bool:
        n = len(cls.__name__)
        if n > 0:
            raise ValueError("b")
        return n > 5


class C(metaclass=M):
    pass


#@ no_exception \all
def f() -> int:
    if C:
        return 1
    return 0


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
