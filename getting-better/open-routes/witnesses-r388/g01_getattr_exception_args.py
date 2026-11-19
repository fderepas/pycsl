class E(Exception):
    def __init__(self) -> None:
        self.x: int = 1


#@ ensures \result == 0
def f(e: E) -> int:
    return getattr(e, "args", 0)


if __name__ == "__main__":
    r = f(E())
    print("VIOLATION f =", r) if r != 0 else print("no violation")
