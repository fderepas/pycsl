"""Test ensurepip.bootstrap L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import ensurepip  # noqa: F401


#@ requires True
#@ ensures True
def use_bootstrap(x: int) -> int:
    return ensurepip.bootstrap(x)


if __name__ == "__main__":
    pass
