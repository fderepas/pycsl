r"""G29 RS2 — a function WITHOUT a raises clause whose body raises; a no_exception caller."""
_ = 0  # anchor


#@ assigns \nothing
def f(k: int) -> int:
    if k == 0:
        raise ValueError
    return k


#@ assigns \nothing
#@ no_exception ValueError
def caller() -> int:
    return f(0)


if __name__ == "__main__":
    try:
        print("CPython:", caller())
    except Exception as e:
        print("CPython raises", type(e).__name__)
