r"""G29 SS3 — a module str set literal mutated by `.discard` at module scope; membership of the discarded member."""
_ = 0  # anchor
XS = {"a", "b"}
XS.discard("a")


#@ ensures \result == 1
def probe() -> int:
    return 1 if "a" in XS else 0


if __name__ == "__main__":
    print("CPython:", probe())
