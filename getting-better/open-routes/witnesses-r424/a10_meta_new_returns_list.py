class M(type):
    pass


class K(metaclass=M):
    def __class_getitem__(cls, item: int) -> list:
        return [item]


#@ no_exception \all
def f() -> int:
    s = {K[1]}
    return len(s)


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
