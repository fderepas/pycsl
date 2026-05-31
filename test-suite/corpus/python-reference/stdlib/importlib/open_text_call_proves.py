"""Test importlib.open_text L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import importlib  # noqa: F401


#@ requires True
#@ ensures True
def use_open_text(x: int) -> int:
    return importlib.open_text(x)


if __name__ == "__main__":
    pass
