r"""G29 IE-U1 — tuple unpack into an attribute target."""
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.x = 0


#@ ensures \result == 0
def probe() -> int:
    c = C()
    a, c.x = 1, 5
    return c.x
if __name__ == "__main__":
    print("CPython:", probe())
