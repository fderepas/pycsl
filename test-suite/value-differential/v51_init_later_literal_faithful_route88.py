"""v51 AGREE — the true twin of v50. `init_body` is now keyed by FIELD and last-wins, and the
superseding literal is carried by `field_defaults` (last-wins too), so this TRUE claim PROVES.
CPython returns 3."""


class C:
    n: int

    #@ assigns self.n
    def __init__(self, k: int) -> None:
        self.n = k
        self.n = 3


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    c = C(7)
    return c.n


if __name__ == "__main__":
    print(f())
