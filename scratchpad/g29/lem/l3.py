r"""G29 LEM3 — a `#@ lemma` calling a `\trusted` function with an optimistic contract (WATCH row: dotted call escapes `_lemma_calls_trusted`)."""
_ = 0  # anchor


class K:
    def __init__(self) -> None:
        self.n = 1

    #@ \trusted reviewer: g29
    #@ ensures \result == 5
    def five(self) -> int:
        return 4

    #@ lemma
    #@ ensures False
    #@ assigns \nothing
    def bogus(self) -> None:
        x = self.five()
        #@ assert x == 5
        pass


if __name__ == "__main__":
    print("CPython:", K().five())
