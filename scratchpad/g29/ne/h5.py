r"""G29 NE-H5 — #161 whitelist carrier: a whitelisted builtin that raises ValueError (directly or through a function object)."""
from typing import List
_ = 0  # anchor


#@ raises ValueError when k == 0
#@ assigns \nothing
def f(k: int) -> int:
    if k == 0:
        raise ValueError
    return k


#@ no_exception ValueError
def probe() -> int:
    xs: List[int] = [0]
    return max(xs, key=f)


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
