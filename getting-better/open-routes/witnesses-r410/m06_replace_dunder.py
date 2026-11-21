import copy


class D:
    def __init__(self) -> None:
        self.x: int = 1

    def __replace__(self) -> list:
        return [1]


#@ no_exception \all
def f(d: D) -> int:
    s = {copy.replace(d)}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(D())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
