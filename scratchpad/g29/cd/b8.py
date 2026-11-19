r"""G29 CD8 — __bool__ False makes `if obj:` take the else branch."""
_ = 0  # anchor


class A:
    def __init__(self) -> None:
        self.k = 0

    def __bool__(self) -> bool:
        return False


#@ ensures \result == 1
def probe() -> int:
    a = A()
    if a:
        return 1
    return 2


if __name__ == "__main__":
    print("CPython:", probe())
