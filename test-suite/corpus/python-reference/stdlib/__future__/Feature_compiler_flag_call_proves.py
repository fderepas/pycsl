"""Test __future__.Feature_compiler_flag L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import __future__  # noqa: F401


#@ requires True
#@ ensures True
def use_Feature_compiler_flag(x: int) -> int:
    return __future__.Feature_compiler_flag(x)


if __name__ == "__main__":
    pass
