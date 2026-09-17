r"""G29 CC2 — a constructor `ensures` that its body does NOT establish."""
_ = 0  # anchor


class C:
    #@ ensures self.x == 5
    def __init__(self, k: int) -> None:
        self.x = k


#@ ensures \result == 5
def probe() -> int:
    c = C(3)
    return c.x


if __name__ == "__main__":
    print("CPython:", probe())
