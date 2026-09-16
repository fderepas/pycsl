r"""G29 GH1 — a GHOST assignment to a name that is also a PROGRAM variable."""
_ = 0  # anchor


#@ ensures \result == 7
def probe() -> int:
    x = 1
    #@ ghost x = 7
    y = 0
    return x


if __name__ == "__main__":
    print("CPython:", probe())
