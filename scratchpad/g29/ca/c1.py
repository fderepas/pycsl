r"""G29 CA-C1 — class-level attribute state: instance creation bumps a class counter (claim != truth; CPython 2)."""
_ = 0  # anchor


class C:
    count = 0

    def __init__(self) -> None:
        self.v = 1
    @staticmethod
    def bump() -> None:
        C.count += 1


#@ ensures \result != 2
def probe() -> int:
    C.bump()
    C.bump()
    return C.count


if __name__ == "__main__":
    print("CPython:", probe())
