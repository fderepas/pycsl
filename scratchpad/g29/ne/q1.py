r"""G29 NE-Q1 — #161/#66 carrier: `int(s)` where `s` is a string that the symbol table does not type as `str` (a str-returning call result)."""
_ = 0  # anchor


#@ assigns \nothing
def getname() -> str:
    return "x"


#@ no_exception ValueError
def probe() -> int:
    return int(getname())


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
