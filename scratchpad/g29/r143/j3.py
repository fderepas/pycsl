r"""G29 J3 — route #143 carrier: NO module-level clash, but the CALLER has a LOCAL named like
the callee module's constant; the call-site raises-assert renders the condition in the
caller's scope."""
_ = 0  # anchor
from multi_file_lib.r141_raiselib import f


#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    LIM = 5
    return f(k) + LIM


if __name__ == "__main__":
    print("CPython:", caller(3))
