r"""G29 RS1 — the body raises MORE often than its `raises ... when` clause admits."""
_ = 0  # anchor


#@ raises ValueError when k < 0
#@ assigns \nothing
def f(k: int) -> int:
    if k <= 0:
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
