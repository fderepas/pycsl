"""Test compileall.compile_path L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import compileall  # noqa: F401


#@ requires True
#@ ensures True
def use_compile_path(x: int) -> int:
    return compileall.compile_path(x)


if __name__ == "__main__":
    pass
