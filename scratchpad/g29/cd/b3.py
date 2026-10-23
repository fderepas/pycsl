r"""G29 CD3 — a class attribute incremented in __init__."""
_ = 0  # anchor


class C:
    count = 0

    def __init__(self) -> None:
        C.count += 1


#@ ensures \result == 0
def probe() -> int:
    C()
    C()
    return C.count


if __name__ == "__main__":
    print("CPython:", probe())
