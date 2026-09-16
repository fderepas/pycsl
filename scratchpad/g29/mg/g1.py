r"""G29 MG1 — route #149 through a MODULE-GLOBAL instance: `G = C()` with a defaulted parameter."""
_ = 0  # anchor


class C:
    def __init__(self, r: int = 5) -> None:
        self.r = r


G = C()


#@ ensures \result == 0
def probe() -> int:
    return G.r


if __name__ == "__main__":
    print("CPython:", probe())
