r"""G29 RS3 — the raise happens in a CALLEE's callee (two levels), no raises clauses anywhere."""
_ = 0  # anchor


#@ assigns \nothing
def g(k: int) -> int:
    if k == 0:
        raise ValueError
    return k


#@ assigns \nothing
def f(k: int) -> int:
    return g(k)


#@ assigns \nothing
#@ no_exception ValueError
def caller() -> int:
    return f(0)


if __name__ == "__main__":
    try:
        print("CPython:", caller())
    except Exception as e:
        print("CPython raises", type(e).__name__)
