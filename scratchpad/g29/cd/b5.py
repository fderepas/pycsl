r"""G29 CD5 — __len__ override used by len()."""
_ = 0  # anchor


class A:
    def __init__(self) -> None:
        self.n = 4

    def __len__(self) -> int:
        return self.n


#@ ensures \result == 0
def probe() -> int:
    return len(A())


if __name__ == "__main__":
    print("CPython:", probe())
