r"""G29 ER2 — early return, annotated field with a class-level default."""
_ = 0  # anchor


class C:
    x: int = 0

    def __init__(self, k: int) -> None:
        if k < 0:
            return
        self.x = k


#@ ensures \result == -1
#@ assigns \nothing
def probe() -> int:
    c = C(-1)
    return c.x


if __name__ == "__main__":
    print("CPython:", probe())
