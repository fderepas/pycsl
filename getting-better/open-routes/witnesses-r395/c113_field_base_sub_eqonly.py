from dataclasses import dataclass


class B:
    def __init__(self) -> None:
        self.x: int = 1


class D(B):
    def __eq__(self, o: object) -> bool:
        return True


#@ no_exception \all
def f(b: B) -> int:
    s = {b}
    return len(s)


if __name__ == "__main__":
    try:
        print("result", f(D()))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
