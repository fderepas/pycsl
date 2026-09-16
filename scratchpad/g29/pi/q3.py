r"""G29 Q3 — a class-level `__setattr__` override intercepts every constructor store."""
_ = 0  # anchor


class P:
    def __init__(self, k: int) -> None:
        self.x = k

    def __setattr__(self, name: str, value: int) -> None:
        object.__setattr__(self, name, value + 1)


#@ ensures \result == 5
#@ assigns \nothing
def probe() -> int:
    p = P(5)
    return p.x


if __name__ == "__main__":
    print("CPython:", probe())
