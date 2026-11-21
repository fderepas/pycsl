class M(type):
    def __eq__(cls, other: object) -> bool:
        return True


class K(metaclass=M):
    def __init__(self) -> None:
        self.x: int = 1


#@ no_exception \all
def f(k: K) -> int:
    s = {type(k)}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(K())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
