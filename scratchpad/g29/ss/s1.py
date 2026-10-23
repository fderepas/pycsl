r"""G29 SS1 — gen #26 WATCH (#132): a module str SET built with `set((...))` then `.add`ed; membership."""
_ = 0  # anchor
XS = set(("a", "b"))
XS.add("c")


#@ ensures \result == 0
def probe() -> int:
    return 1 if "c" in XS else 0


if __name__ == "__main__":
    print("CPython:", probe())
