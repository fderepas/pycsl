"""Test compileall.compile_file L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import compileall  # noqa: F401


#@ requires True
#@ ensures True
def use_compile_file(x: int) -> int:
    return compileall.compile_file(x)


if __name__ == "__main__":
    pass
