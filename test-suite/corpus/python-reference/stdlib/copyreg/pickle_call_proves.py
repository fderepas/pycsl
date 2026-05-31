"""Test copyreg.pickle L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import copyreg  # noqa: F401


#@ requires True
#@ ensures True
def use_pickle(x: int) -> int:
    return copyreg.pickle(x)


if __name__ == "__main__":
    pass
