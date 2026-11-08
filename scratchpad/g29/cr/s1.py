r"""G29 S1 — route #149 family: an omitted STRING parameter default."""
_ = 0  # anchor


class Cy:
    def __init__(self, name: str = "abc") -> None:
        self.name = name


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    return len(c.name)


if __name__ == "__main__":
    print("CPython:", probe())
