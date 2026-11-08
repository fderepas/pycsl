class M(type):
    def __init__(cls, name: str, bases: tuple, ns: dict) -> None:
        super().__init__(name, bases, ns)
        cls.K = [1]


class C(metaclass=M):
    K = 1


#@ no_exception \all
def f() -> int:
    s = {C.K}
    return len(s)


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
