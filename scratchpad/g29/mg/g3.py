r"""G29 MG3 — route #153 through a MODULE-GLOBAL instance."""
_ = 0  # anchor


class C:
    def __init__(self, k: int) -> None:
        k = k + 1
        self.r = k


G = C(5)


#@ ensures \result == 5
def probe() -> int:
    return G.r


if __name__ == "__main__":
    print("CPython:", probe())
