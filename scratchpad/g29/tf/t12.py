r"""G29 T12 — route #156 control: a `\trusted` function containing a jumping handler-less `finally` is not refused."""
_ = 0  # anchor


#@ \trusted reviewer: g29
#@ ensures True
def helper() -> int:
    x = 0
    try:
        return 1
    finally:
        x = 7


#@ ensures True
def probe() -> int:
    return helper()
