"""Test abc.update_abstractmethods L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import abc  # noqa: F401


#@ requires True
#@ ensures True
def use_update_abstractmethods(x: int) -> int:
    return abc.update_abstractmethods(x)


if __name__ == "__main__":
    pass
