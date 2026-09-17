r"""G29 CC1 — a constructor `requires` violated at the construction site, then its ensures exploited."""
_ = 0  # anchor


class C:
    #@ requires k > 0
    #@ ensures self.x > 0
    def __init__(self, k: int) -> None:
        self.x = k


#@ ensures \result > 0
def probe() -> int:
    c = C(-1)
    return c.x


if __name__ == "__main__":
    print("CPython:", probe())
