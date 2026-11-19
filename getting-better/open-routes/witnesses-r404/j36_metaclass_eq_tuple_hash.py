class M(type):
    def __eq__(cls, other: object) -> bool:
        return True


class C(metaclass=M):
    pass


#@ no_exception \all
def f() -> int:
    s = {(C, 1)}
    return len(s)


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
