"""Test compileall.compile_dir L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import compileall  # noqa: F401


#@ requires True
#@ ensures True
def use_compile_dir(x: int) -> int:
    return compileall.compile_dir(x)


if __name__ == "__main__":
    pass
