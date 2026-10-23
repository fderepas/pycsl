r"""G29 SS2 — the plain `{...}` literal module str set, membership of a member (does a consumer fold it?)."""
_ = 0  # anchor
XS = {"a", "b"}


#@ ensures \result == 1
def probe() -> int:
    return 1 if "a" in XS else 0


if __name__ == "__main__":
    print("CPython:", probe())
